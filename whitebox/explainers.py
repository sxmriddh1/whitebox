"""
explainers.py — feature attribution for a black-box model.

WHAT THIS MODULE DOES
-----------------------
Given a fitted model (via ModelAdapter) and a set of rows to explain,
this module answers: "for this specific prediction, how much did each
feature push the output toward the positive class, and how much
toward the negative class?"

Primary method: SHAP (SHapley Additive exPlanations), specifically
KernelExplainer, which works with ANY predict_proba function — this
is what makes Whitebox model-framework-agnostic. KernelExplainer
repeatedly perturbs the input and observes how the output changes,
using game-theoretic Shapley values to fairly split credit across
features. This perturb-and-observe mechanism is also, not
coincidentally, the exact mechanism the adversarial audit later
tries to exploit (see attacks.py) — SHAP's strength and its
attack surface come from the same design choice.

FALLBACK MODE
--------------
If the `shap` package is not installed, this module automatically
falls back to a permutation-importance-based approximation so the
rest of the pipeline can still run end-to-end (useful for a first
smoke-test on a machine without `shap` installed yet). Fallback mode
is clearly labeled everywhere it appears in output — it is NOT a
substitute for real SHAP values in a report you intend to trust or
publish.
"""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

try:
    import shap as _shap  # type: ignore
    _HAS_SHAP = True
except ImportError:
    _HAS_SHAP = False


@dataclass
class AttributionResult:
    """
    Per-row, per-feature attribution scores plus bookkeeping.

    values: shape (n_rows, n_features) — signed contribution of each
            feature to each row's prediction. Positive = pushed
            toward the positive class (however the user's model
            defines it); negative = pushed toward the negative class.
    feature_names: column labels, same order as `values` columns.
    method: "shap" or "permutation_fallback" — always check this
            before treating attributions as publication-grade.
    """
    values: np.ndarray
    feature_names: List[str]
    method: str

    def top_features(self, row_idx: int, k: int = 5) -> List[dict]:
        """
        Return the k features with the largest |attribution| for one
        row, sorted most-to-least influential. Used by both the LLM
        narration layer and the adversarial audit's decoy-selection
        logic.
        """
        row = self.values[row_idx]
        order = np.argsort(np.abs(row))[::-1][:k]
        return [
            {
                "feature": self.feature_names[i],
                "attribution": float(row[i]),
                "direction": "positive class" if row[i] > 0 else "negative class",
                "rank": rank + 1,
            }
            for rank, i in enumerate(order)
        ]

    def global_ranking(self) -> List[dict]:
        """
        Mean absolute attribution per feature across all explained
        rows — the "which features matter most overall" view, used
        in the CLI summary table.
        """
        mean_abs = np.abs(self.values).mean(axis=0)
        order = np.argsort(mean_abs)[::-1]
        return [
            {"feature": self.feature_names[i], "mean_abs_attribution": float(mean_abs[i])}
            for i in order
        ]


def explain(
    predict_proba_fn,
    X_background: np.ndarray,
    X_explain: np.ndarray,
    feature_names: List[str],
    background_size: int = 50,
    random_seed: int = 42,
    verbose: bool = True,
) -> AttributionResult:
    """
    Compute feature attributions for X_explain, using X_background as
    the reference distribution SHAP perturbs around.

    This function is intentionally framework-agnostic: it takes a
    plain predict_proba_fn callable, not a model object, so it works
    identically whether the underlying model is a scikit-learn
    classifier, a Keras network, or anything else.
    """
    rng = np.random.default_rng(random_seed)

    if _HAS_SHAP:
        n_bg = min(background_size, len(X_background))
        bg_idx = rng.choice(len(X_background), size=n_bg, replace=False)
        background = X_background[bg_idx]

        explainer = _shap.KernelExplainer(predict_proba_fn, background)
        if verbose:
            print(
                f"  [explainers] Running SHAP KernelExplainer on "
                f"{len(X_explain)} rows against a {n_bg}-row background "
                f"(this re-runs the model many times per row and may take "
                f"a minute)..."
            )
        raw_values = explainer.shap_values(X_explain)

        # KernelExplainer can return either a single array or a list
        # (one array per output class), depending on shap version and
        # whether predict_proba_fn returns 1D or 2D output. Normalize
        # to a single (n_rows, n_features) array either way.
        if isinstance(raw_values, list):
            raw_values = raw_values[-1]  # take the positive-class array
        values = np.asarray(raw_values)
        if values.ndim == 3:
            values = values[:, :, -1]

        return AttributionResult(values=values, feature_names=feature_names, method="shap")

    # ---- fallback path: shap not installed ----
    if verbose:
        print(
            "  [explainers] WARNING: `shap` is not installed — falling back "
            "to a permutation-importance approximation. This is a rough "
            "stand-in for real SHAP values and should NOT be used for a "
            "report you intend to publish or rely on. Install shap "
            "(`pip install shap`) for real attributions."
        )
    return _permutation_fallback(predict_proba_fn, X_explain, feature_names)


def _permutation_fallback(predict_proba_fn, X_explain, feature_names) -> AttributionResult:
    """
    A crude but dependency-free stand-in for SHAP: for each row and
    feature, zero out that one feature (replace with the column mean
    across X_explain) and measure how much the prediction shifts.
    This captures rough directional signal but has none of SHAP's
    theoretical guarantees (local accuracy, consistency, etc.) — see
    the module docstring for why this is fallback-only.
    """
    n_rows, n_features = X_explain.shape
    baseline_preds = predict_proba_fn(X_explain)
    col_means = X_explain.mean(axis=0)

    values = np.zeros((n_rows, n_features))
    for f in range(n_features):
        perturbed = X_explain.copy()
        perturbed[:, f] = col_means[f]
        perturbed_preds = predict_proba_fn(perturbed)
        # Positive = removing this feature DECREASED the prediction,
        # i.e. the feature was pushing toward the positive class.
        values[:, f] = baseline_preds - perturbed_preds

    return AttributionResult(
        values=values, feature_names=feature_names, method="permutation_fallback"
    )
