"""
defenses.py — candidate defenses against the explanation-manipulation
attack in attacks.py, and honest measurement of whether they work.

Three defenses are implemented. Report your own numbers when you run
this against your own model — do not assume these will rank the same
way they did in this project's original NIDS prototype. That said,
the MECHANISM of why each one can fail is general, not dataset-
specific, and is worth understanding before you pick one:

  1. SMOOTHING (small noise) — average SHAP over a few small random
     perturbations of the input, hoping to wash out an attacker's
     unstable, decoy-driven spike. Can fail if the attack's push is
     large relative to the noise radius: wobbling by +/-0.1 around an
     already-extreme value of 4.0 still leaves you at 3.9-4.1 — still
     obviously out-of-distribution to the explainer.

  2. SMOOTHING (large noise) — same idea, bigger radius. Can
     backfire: if the noise is large enough, the BASELINE
     (unattacked) explanation becomes unstable across repeated calls
     too, since each call draws fresh randomness — so "did the top
     feature change" stops cleanly measuring attack success and
     starts partly measuring the defense's own instability.

  3. CLIPPING (winsorization) — cap every feature to a realistic
     range before explaining, directly neutralizing the most extreme
     part of a push. Can still fail: clipping to exactly the boundary
     (e.g. 3 standard deviations) can still be atypical enough to
     meaningfully skew attribution. The vulnerability is not really
     about "how extreme is too extreme" as a hard threshold — it's a
     continuous gradient of atypicality, and capping the worst excess
     isn't the same as making a value look genuinely typical.

None of these is guaranteed to work on your model. If your results
show no defense beating baseline, that is a legitimate, reportable
finding — not a bug in this module. Adversarial robustness in
explainable AI is, as of this writing, an open research problem; see
README.md's research papers section, particularly the SHLIME paper,
for work specifically on improving this.
"""

from dataclasses import dataclass
from typing import Callable, List

import numpy as np

from .explainers import explain


@dataclass
class DefenseResult:
    name: str
    n_tested: int
    n_decision_stable: int
    n_success_among_stable: int  # attack still succeeded despite the defense

    @property
    def attack_success_rate(self) -> float:
        return (
            self.n_success_among_stable / self.n_decision_stable
            if self.n_decision_stable
            else 0.0
        )


def _run_defended_attack(
    defense_name: str,
    shap_fn: Callable,
    adapter_predict_proba,
    predict_proba_fn_for_shap,
    X_pool: np.ndarray,
    feature_names: List[str],
    decoy_alpha: float,
    n_examples: int,
    random_seed: int,
) -> DefenseResult:
    """Shared harness: run the Type 2 attack, but compute attributions
    through `shap_fn` (a defended variant) instead of a plain SHAP call."""
    rng = np.random.default_rng(random_seed)
    n_examples = min(n_examples, len(X_pool))
    idx_pool = rng.choice(len(X_pool), size=n_examples, replace=False)

    n_stable = 0
    n_success = 0

    for idx in idx_pool:
        row = X_pool[idx].copy()
        baseline_proba = adapter_predict_proba(row.reshape(1, -1))[0]
        baseline_side = baseline_proba >= 0.5

        baseline_values = shap_fn(row, predict_proba_fn_for_shap, X_pool, feature_names)
        baseline_top_idx = int(np.argsort(np.abs(baseline_values))[::-1][0])
        decoy_idx = int(np.argsort(np.abs(baseline_values))[0])

        attacked_row = row.copy()
        attacked_row[decoy_idx] = decoy_alpha
        attacked_proba = adapter_predict_proba(attacked_row.reshape(1, -1))[0]
        attacked_side = attacked_proba >= 0.5

        if attacked_side != baseline_side:
            continue  # contaminated trial, excluded exactly as in attacks.py

        n_stable += 1
        attacked_values = shap_fn(
            attacked_row, predict_proba_fn_for_shap, X_pool, feature_names
        )
        attacked_top_idx = int(np.argsort(np.abs(attacked_values))[::-1][0])
        if attacked_top_idx != baseline_top_idx:
            n_success += 1

    return DefenseResult(
        name=defense_name,
        n_tested=n_examples,
        n_decision_stable=n_stable,
        n_success_among_stable=n_success,
    )


def _smoothed_shap(row, predict_proba_fn, X_pool, feature_names, n_samples=3, noise_std=0.1):
    rng = np.random.default_rng(0)
    samples = [row + rng.normal(0, noise_std, row.shape) for _ in range(n_samples)]
    vals = []
    for s in samples:
        attr = explain(
            predict_proba_fn, X_pool, s.reshape(1, -1), feature_names,
            background_size=min(30, len(X_pool)), verbose=False,
        )
        vals.append(attr.values[0])
    return np.mean(vals, axis=0)


def _clipped_shap(row, predict_proba_fn, X_pool, feature_names, clip_sigma=3.0):
    clipped = np.clip(row, -clip_sigma, clip_sigma)
    attr = explain(
        predict_proba_fn, X_pool, clipped.reshape(1, -1), feature_names,
        background_size=min(30, len(X_pool)), verbose=False,
    )
    return attr.values[0]


def run_all_defenses(
    adapter_predict_proba,
    predict_proba_fn_for_shap,
    X_pool: np.ndarray,
    feature_names: List[str],
    decoy_alpha: float = 4.0,
    n_examples: int = 8,
    small_noise_std: float = 0.1,
    large_noise_std: float = 0.5,
    clip_sigma: float = 3.0,
    random_seed: int = 42,
    verbose: bool = True,
) -> List[DefenseResult]:
    """
    Runs all three defenses and returns their results in a fixed
    order (small-noise smoothing, large-noise smoothing, clipping),
    matching the order they're presented in the CLI summary table.
    """
    results = []
    configs = [
        ("smoothing_small_noise", lambda r, p, x, f: _smoothed_shap(r, p, x, f, noise_std=small_noise_std)),
        ("smoothing_large_noise", lambda r, p, x, f: _smoothed_shap(r, p, x, f, noise_std=large_noise_std)),
        ("clipping", lambda r, p, x, f: _clipped_shap(r, p, x, f, clip_sigma=clip_sigma)),
    ]
    for name, fn in configs:
        if verbose:
            print(f"  [defenses] evaluating: {name} ...")
        result = _run_defended_attack(
            name, fn, adapter_predict_proba, predict_proba_fn_for_shap,
            X_pool, feature_names, decoy_alpha, n_examples, random_seed,
        )
        results.append(result)
    return results
