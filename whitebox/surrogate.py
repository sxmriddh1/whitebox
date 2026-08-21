"""
surrogate.py — distilling the black-box model into a readable tree.

WHAT THIS MODULE DOES
-----------------------
SHAP (explainers.py) tells you which features mattered for ONE
prediction. This module builds something complementary: a shallow,
fully human-readable decision tree trained to mimic the black-box
model's overall behavior across MANY predictions — global, not just
local, interpretability.

The critical detail, easy to get wrong: the tree is trained on the
BLACK-BOX MODEL'S OWN PREDICTIONS, not on the real ground-truth
labels. This is model distillation — the tree is a student watching
an expert (your model) make decisions and writing down simple rules
that reproduce that behavior, not rules that reproduce reality. That
distinction matters: a low-fidelity tree means "this simple
explanation doesn't actually match what your model is doing," which
is itself a useful, reportable finding, separate from whether the
model is accurate.
"""

from dataclasses import dataclass
from typing import List

import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text


@dataclass
class SurrogateResult:
    tree: DecisionTreeClassifier
    fidelity: float           # fraction of rows where tree agrees with the real model
    feature_names: List[str]
    max_depth: int

    def rules_as_text(self) -> str:
        """Human-readable if/else rule dump of the fitted tree."""
        return export_text(self.tree, feature_names=self.feature_names)


def build_surrogate(
    predict_fn,
    X_train: np.ndarray,
    X_eval: np.ndarray,
    feature_names: List[str],
    max_depth: int = 4,
    random_seed: int = 42,
) -> SurrogateResult:
    """
    Train a shallow decision tree to mimic predict_fn's hard 0/1
    predictions, then measure fidelity on a held-out evaluation set.

    predict_fn is expected to return hard class labels (0/1), not
    probabilities — pass adapter.predict, not adapter.predict_proba.

    max_depth is a deliberate interpretability-vs-fidelity tradeoff:
    a deeper tree could match the black box almost perfectly, but
    would become just as unreadable as the thing it's meant to
    explain. The remaining fidelity gap at a shallow depth is the
    honest, quantified cost of choosing readability over completeness
    — report it, don't hide it.
    """
    train_labels = predict_fn(X_train)
    tree = DecisionTreeClassifier(max_depth=max_depth, random_state=random_seed)
    tree.fit(X_train, train_labels)

    eval_model_labels = predict_fn(X_eval)
    eval_tree_labels = tree.predict(X_eval)
    fidelity = float((eval_tree_labels == eval_model_labels).mean())

    return SurrogateResult(
        tree=tree,
        fidelity=fidelity,
        feature_names=feature_names,
        max_depth=max_depth,
    )
