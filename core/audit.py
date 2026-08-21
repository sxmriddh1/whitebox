"""
audit.py — the orchestrator. Runs every phase in order and assembles
one AuditReport that the CLI and report.py both consume.

PIPELINE ORDER (mirrors the phases in README.md's "How it works"):
  1. Explain     — SHAP attribution over a sample of rows
  2. Distill      — surrogate decision tree, fidelity measured
  3. Narrate      — optional plain-English explanation via Groq
  4. Attack        — evasion (Type 1) + explanation manipulation (Type 2)
  5. Defend        — evaluate candidate defenses against Type 2

Each phase is wrapped so a failure in one (e.g. no Groq key, so
narration is skipped) does not prevent later phases from running —
the CLI should always produce as complete a report as the available
configuration allows, and clearly label what was skipped and why.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from .attacks import (
    EvasionResult,
    ExplanationManipulationResult,
    run_evasion_attack,
    run_explanation_manipulation_attack,
)
from .config import WhiteboxConfig
from .defenses import DefenseResult, run_all_defenses
from .explainers import AttributionResult, explain
from .llm_layer import Explanation, LLMNarrator
from .model_adapter import ModelAdapter
from .surrogate import SurrogateResult, build_surrogate


@dataclass
class AuditReport:
    n_rows_explained: int
    feature_names: List[str]
    attribution: AttributionResult
    surrogate: SurrogateResult
    sample_narrations: List[Explanation]
    evasion: EvasionResult
    manipulation: ExplanationManipulationResult
    defenses: List[DefenseResult]
    llm_enabled: bool
    llm_disabled_reason: Optional[str] = None


def run_audit(
    adapter: ModelAdapter,
    X: np.ndarray,
    feature_names: List[str],
    config: WhiteboxConfig,
    verbose: bool = True,
) -> AuditReport:
    """
    Run the complete Whitebox audit pipeline against `adapter`, using
    `X` (already-numeric, already-scaled feature matrix — see
    cli.py's data-loading step for what "ready" means) as both the
    background reference and the pool of rows to explain / attack.
    """
    rng = np.random.default_rng(config.random_seed)

    # ---------- Phase 1: Explain ----------
    if verbose:
        print("\n[1/5] EXPLAIN — computing SHAP attributions...")
    n_explain = min(config.shap_sample_size, len(X))
    explain_idx = rng.choice(len(X), size=n_explain, replace=False)
    X_explain = X[explain_idx]

    attribution = explain(
        adapter.predict_proba,
        X_background=X,
        X_explain=X_explain,
        feature_names=feature_names,
        background_size=config.shap_background_size,
        random_seed=config.random_seed,
        verbose=verbose,
    )

    # ---------- Phase 2: Distill ----------
    if verbose:
        print("\n[2/5] DISTILL — training surrogate decision tree...")
    surrogate = build_surrogate(
        predict_fn=adapter.predict,
        X_train=X,
        X_eval=X_explain,
        feature_names=feature_names,
        max_depth=config.surrogate_max_depth,
        random_seed=config.random_seed,
    )
    if verbose:
        print(f"  [surrogate] fidelity to black-box model: {surrogate.fidelity:.4f}")

    # ---------- Phase 3: Narrate (optional) ----------
    if verbose:
        print("\n[3/5] NARRATE — generating plain-English explanations (Groq)...")
    narrator = LLMNarrator(
        api_key=config.groq_api_key,
        model=config.groq_model,
        temperature=config.llm_temperature,
    )
    sample_narrations: List[Explanation] = []
    if narrator.is_enabled():
        n_narrate = min(3, len(X_explain))
        for i in range(n_narrate):
            proba = adapter.predict_proba(X_explain[i].reshape(1, -1))[0]
            label = "positive class" if proba >= 0.5 else "negative class"
            top_feats = attribution.top_features(i, k=5)
            expl = narrator.explain_prediction(label, float(proba), top_feats)
            sample_narrations.append(expl)
            if verbose:
                comp = expl.completeness_ratio()
                print(f"  [narrate] example {i+1}/{n_narrate}: completeness={comp:.0%}")
    elif verbose:
        print(f"  [narrate] SKIPPED — {narrator.disabled_reason}")

    # ---------- Phase 4: Attack ----------
    if verbose:
        print("\n[4/5] ATTACK — running adversarial audit...")
        print("  [attacks] Type 1 (evasion)...")
    evasion = run_evasion_attack(
        adapter_predict_proba=adapter.predict_proba,
        attribution=attribution,
        X_pool=X,
        top_k_features=config.audit_top_k_features,
        n_borderline=config.audit_borderline_n,
        n_steps=config.audit_evasion_steps,
        random_seed=config.random_seed,
    )
    if verbose:
        print(
            f"    -> {evasion.n_success}/{evasion.n_tested} borderline examples "
            f"flipped ({evasion.success_rate:.1%})"
        )
        print("  [attacks] Type 2 (explanation manipulation)...")
    manipulation = run_explanation_manipulation_attack(
        adapter_predict_proba=adapter.predict_proba,
        predict_proba_fn_for_shap=adapter.predict_proba,
        X_pool=X,
        feature_names=feature_names,
        decoy_alpha=config.audit_decoy_alpha,
        n_examples=config.audit_decoy_batch_n,
        random_seed=config.random_seed,
        verbose=verbose,
    )
    if verbose:
        print(
            f"    -> {manipulation.n_success_among_stable}/"
            f"{manipulation.n_decision_stable} decision-stable trials had their "
            f"explanation successfully hijacked ({manipulation.success_rate:.1%}); "
            f"{manipulation.n_contaminated} trials excluded (decision flipped)"
        )

    # ---------- Phase 5: Defend ----------
    if verbose:
        print("\n[5/5] DEFEND — evaluating candidate defenses...")
    defenses = run_all_defenses(
        adapter_predict_proba=adapter.predict_proba,
        predict_proba_fn_for_shap=adapter.predict_proba,
        X_pool=X,
        feature_names=feature_names,
        decoy_alpha=config.audit_decoy_alpha,
        n_examples=min(8, config.audit_decoy_batch_n),
        small_noise_std=config.defense_smoothing_small_std,
        large_noise_std=config.defense_smoothing_large_std,
        clip_sigma=config.defense_clip_sigma,
        random_seed=config.random_seed,
        verbose=verbose,
    )
    if verbose:
        for d in defenses:
            print(f"    -> {d.name}: attack success {d.attack_success_rate:.1%}")

    return AuditReport(
        n_rows_explained=n_explain,
        feature_names=feature_names,
        attribution=attribution,
        surrogate=surrogate,
        sample_narrations=sample_narrations,
        evasion=evasion,
        manipulation=manipulation,
        defenses=defenses,
        llm_enabled=narrator.is_enabled(),
        llm_disabled_reason=narrator.disabled_reason,
    )
