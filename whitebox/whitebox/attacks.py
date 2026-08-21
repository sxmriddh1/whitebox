"""
attacks.py — the core of Whitebox: testing whether a model's decision
or its explanation can be adversarially manipulated.

This module runs two DIFFERENT kinds of attack. Keeping them
conceptually separate matters — they test different things and a
model can be robust to one while vulnerable to the other:

  ATTACK TYPE 1 — EVASION
    Question: "Can I change what the model actually decides?"
    Method: take a correctly-classified example, nudge only the
    features the explainer says the model relies on most, toward
    what the opposite class typically looks like, and see how much
    nudging it takes to flip the verdict.
    This is a classic adversarial-ML attack. It matters here because
    it's explanation-INFORMED: it uses the attribution values from
    explainers.py to target the perturbation efficiently, rather than
    perturbing randomly.

  ATTACK TYPE 2 — EXPLANATION MANIPULATION
    Question: "Can I change WHY the model says it decided that, while
    the actual decision stays identical?"
    Method: take a feature the explainer currently treats as
    unimportant (a "decoy"), push it to an extreme value, and check
    whether (a) the model's actual prediction stays the same
    (decision-stable — required for this to be a clean test) and
    (b) the explanation's feature ranking shifts anyway.
    This is the subtler, more novel attack, and the one this project
    is really about: a decision-stable success here means an analyst
    reading the explanation would be told a different, wrong story
    about why the model did what it did — without the model's
    behavior changing at all. This is the mechanism demonstrated in
    Slack et al. (2020), "Fooling LIME and SHAP" — see README.md's
    research section.

WHY THIS FILE VALIDATES DECISION-STABILITY BEFORE COUNTING A SUCCESS
------------------------------------------------------------------------
An earlier, naive version of the Type 2 attack in this project's
original prototype pushed the decoy feature hard enough that it
occasionally flipped the actual prediction too — contaminating the
result, since "the explanation changed" is trivially true and
meaningless once the model is now explaining a genuinely different
verdict. This module explicitly separates decision-stable trials
from contaminated ones and only reports success rate over the clean
subset. If you change `decoy_alpha` and start seeing your
decision-stable count drop sharply, that's this exact failure mode
re-appearing — reduce alpha.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from .explainers import AttributionResult, explain


@dataclass
class EvasionResult:
    n_tested: int
    n_success: int
    per_example: List[dict] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return self.n_success / self.n_tested if self.n_tested else 0.0


@dataclass
class ExplanationManipulationResult:
    n_tested: int
    n_decision_stable: int
    n_success_among_stable: int
    n_contaminated: int  # trials excluded because the decision itself flipped
    per_example: List[dict] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """
        Success rate is computed over decision-stable trials ONLY —
        see the module docstring for why contaminated trials must be
        excluded rather than counted as either a success or failure.
        """
        return (
            self.n_success_among_stable / self.n_decision_stable
            if self.n_decision_stable
            else 0.0
        )


def run_evasion_attack(
    adapter_predict_proba,
    attribution: AttributionResult,
    X_pool: np.ndarray,
    top_k_features: int = 3,
    n_borderline: int = 20,
    n_steps: int = 20,
    random_seed: int = 42,
) -> EvasionResult:
    """
    ATTACK TYPE 1. See module docstring.

    Selects the `n_borderline` correctly-classified positive-class
    examples closest to the decision boundary (0.5 confidence) —
    deliberately the easiest cases to flip, since a maximally
    confident example is close to un-exploitable through a handful of
    features alone (this was confirmed empirically in this project's
    original prototype: a single maximally-confident example showed
    zero movement across 20 perturbation steps).
    """
    rng = np.random.default_rng(random_seed)
    preds = adapter_predict_proba(X_pool)

    # "malicious"/positive-class analogue: rows the model currently
    # scores LOW (toward the negative/flagged class) but not near 0 —
    # i.e. confidently-caught cases, from which we pick the least
    # confident subset to attack.
    positive_flagged_mask = preds < 0.5
    if positive_flagged_mask.sum() == 0:
        return EvasionResult(n_tested=0, n_success=0)

    confidences = 1 - preds[positive_flagged_mask]  # how confidently flagged
    flagged_idx = np.where(positive_flagged_mask)[0]
    order = np.argsort(confidences)  # least confident first = most borderline
    borderline_idx = flagged_idx[order[: min(n_borderline, len(order))]]

    # "Normal-looking" target profile: mean value of the top-k
    # dominant features across rows the model currently does NOT flag.
    top_feature_names = [f["feature"] for f in attribution.global_ranking()[:top_k_features]]
    top_feature_idx = [attribution.feature_names.index(f) for f in top_feature_names]

    normal_mask = preds >= 0.5
    if normal_mask.sum() == 0:
        normal_profile = X_pool[:, top_feature_idx].mean(axis=0)
    else:
        normal_profile = X_pool[normal_mask][:, top_feature_idx].mean(axis=0)

    n_success = 0
    per_example = []
    for idx in borderline_idx:
        original_row = X_pool[idx].copy()
        flipped_at_alpha: Optional[float] = None

        for step in range(n_steps + 1):
            alpha = step / n_steps
            row = original_row.copy()
            row[top_feature_idx] = (
                (1 - alpha) * original_row[top_feature_idx] + alpha * normal_profile
            )
            proba = adapter_predict_proba(row.reshape(1, -1))[0]
            if proba >= 0.5:  # flipped from flagged -> normal
                flipped_at_alpha = alpha
                break

        success = flipped_at_alpha is not None
        n_success += int(success)
        per_example.append(
            {
                "row_index": int(idx),
                "success": success,
                "flipped_at_alpha": flipped_at_alpha,
                "targeted_features": top_feature_names,
            }
        )

    return EvasionResult(
        n_tested=len(borderline_idx), n_success=n_success, per_example=per_example
    )


def run_explanation_manipulation_attack(
    adapter_predict_proba,
    predict_proba_fn_for_shap,  # passed through to a fresh SHAP call per example
    X_pool: np.ndarray,
    feature_names: List[str],
    decoy_alpha: float = 4.0,
    n_examples: int = 15,
    random_seed: int = 42,
    verbose: bool = True,
) -> ExplanationManipulationResult:
    """
    ATTACK TYPE 2. See module docstring.

    For each tested example:
      1. Get the baseline SHAP top-1 feature.
      2. Identify the current least-important feature (the "decoy").
      3. Push the decoy to `decoy_alpha` (in standardized-feature
         units — assumes X_pool is already scaled, as it should be
         going into any of Whitebox's pipeline).
      4. Check the new prediction (must stay on the same side of 0.5
         to count as decision-stable).
      5. Recompute SHAP and check whether the new top-1 feature
         differs from the baseline top-1 feature.

    `decoy_alpha` is the single most important tuning knob in this
    attack. Too high, and you contaminate results by flipping actual
    decisions (see module docstring); too low, and the attack may
    have no effect on the explanation at all. 4.0 standard deviations
    is a reasonable starting point for standardized tabular features,
    but re-tune it for your own dataset's scale.
    """
    rng = np.random.default_rng(random_seed)
    n_examples = min(n_examples, len(X_pool))
    idx_pool = rng.choice(len(X_pool), size=n_examples, replace=False)

    n_stable = 0
    n_success = 0
    n_contaminated = 0
    per_example = []

    for i, idx in enumerate(idx_pool):
        row = X_pool[idx].copy()
        baseline_proba = adapter_predict_proba(row.reshape(1, -1))[0]
        baseline_side = baseline_proba >= 0.5

        baseline_attr = explain(
            predict_proba_fn_for_shap,
            X_background=X_pool,
            X_explain=row.reshape(1, -1),
            feature_names=feature_names,
            background_size=min(30, len(X_pool)),
            random_seed=random_seed,
            verbose=False,
        )
        baseline_row = baseline_attr.values[0]
        baseline_top_idx = int(np.argsort(np.abs(baseline_row))[::-1][0])
        decoy_idx = int(np.argsort(np.abs(baseline_row))[0])  # least important

        attacked_row = row.copy()
        attacked_row[decoy_idx] = decoy_alpha
        attacked_proba = adapter_predict_proba(attacked_row.reshape(1, -1))[0]
        attacked_side = attacked_proba >= 0.5

        decision_stable = attacked_side == baseline_side
        if not decision_stable:
            n_contaminated += 1
            per_example.append(
                {
                    "row_index": int(idx),
                    "decision_stable": False,
                    "excluded_reason": "decoy push flipped the actual prediction",
                }
            )
            if verbose:
                print(
                    f"  [attacks] example {i+1}/{n_examples}: decoy push flipped "
                    f"the decision — excluding from clean statistics"
                )
            continue

        n_stable += 1
        attacked_attr = explain(
            predict_proba_fn_for_shap,
            X_background=X_pool,
            X_explain=attacked_row.reshape(1, -1),
            feature_names=feature_names,
            background_size=min(30, len(X_pool)),
            random_seed=random_seed,
            verbose=False,
        )
        attacked_top_idx = int(np.argsort(np.abs(attacked_attr.values[0]))[::-1][0])

        success = attacked_top_idx != baseline_top_idx
        n_success += int(success)
        per_example.append(
            {
                "row_index": int(idx),
                "decision_stable": True,
                "success": success,
                "baseline_top_feature": feature_names[baseline_top_idx],
                "post_attack_top_feature": feature_names[attacked_top_idx],
                "decoy_feature": feature_names[decoy_idx],
            }
        )

    return ExplanationManipulationResult(
        n_tested=n_examples,
        n_decision_stable=n_stable,
        n_success_among_stable=n_success,
        n_contaminated=n_contaminated,
        per_example=per_example,
    )
