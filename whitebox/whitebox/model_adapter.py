"""
model_adapter.py — the single integration point between Whitebox and
YOUR model.

WHY THIS EXISTS
----------------
Whitebox needs to work with scikit-learn, XGBoost, TensorFlow,
PyTorch, or literally anything else that can turn a row of numbers
into a probability. Rather than writing (and maintaining) a separate
wrapper for every ML framework, Whitebox asks you to write a tiny
"adapter" file — a few lines of Python — that exposes exactly one
function:

    def predict_proba(X: np.ndarray) -> np.ndarray

This is a deliberate design choice, not a limitation: it means
Whitebox only ever calls your model and reads what comes back. It
never inspects your model's internals. That's not just convenient —
it's the correct threat model for this tool. An adversarial audit is
supposed to test what an OUTSIDE auditor could discover with
black-box access, so Whitebox restricts itself to that same access
level by construction.

WHAT YOUR ADAPTER FILE MUST CONTAIN
-------------------------------------
See examples/sklearn_adapter.py and examples/keras_adapter.py for
full working examples. At minimum:

    import joblib
    import numpy as np

    _model = joblib.load("my_model.pkl")

    def predict_proba(X: np.ndarray) -> np.ndarray:
        \"\"\"Must return a 1D array of P(positive class) for each row.\"\"\"
        return _model.predict_proba(X)[:, 1]

Optionally, an adapter can also define:

    FEATURE_NAMES = ["duration", "src_bytes", ...]  # column order

If FEATURE_NAMES is omitted, Whitebox falls back to the column names
of whatever CSV you pass with --data.
"""

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np


class AdapterError(Exception):
    """Raised when a user-supplied adapter file is missing or malformed."""


@dataclass
class ModelAdapter:
    """
    A thin, validated wrapper around the user's predict_proba function.

    This is what every other module in Whitebox actually calls — no
    other file ever imports the user's adapter module directly, which
    keeps the "only one integration point" guarantee real rather than
    aspirational.
    """

    predict_proba_fn: Callable[[np.ndarray], np.ndarray]
    feature_names: Optional[List[str]] = None
    source_path: str = ""

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Call the underlying model and sanity-check its output shape.

        Raises AdapterError early with a clear message if the user's
        function returns something malformed — this is deliberately
        strict, because a silently-wrong prediction shape would
        corrupt every downstream SHAP value, attack success rate, and
        defense result without any obvious symptom.
        """
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        out = self.predict_proba_fn(X)
        out = np.asarray(out, dtype=float)

        if out.ndim == 2 and out.shape[1] == 2:
            # Some users will naturally return sklearn's full
            # (n_samples, 2) predict_proba output. Be forgiving and
            # take the positive-class column rather than erroring.
            out = out[:, 1]

        out = out.reshape(-1)

        if out.shape[0] != X.shape[0]:
            raise AdapterError(
                f"predict_proba() in '{self.source_path}' returned "
                f"{out.shape[0]} predictions for {X.shape[0]} input rows. "
                "It must return exactly one probability per row."
            )
        if np.any((out < 0) | (out > 1)):
            raise AdapterError(
                f"predict_proba() in '{self.source_path}' returned values "
                "outside [0, 1]. It must return probabilities, not raw "
                "logits or class labels."
            )
        return out

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Convenience: hard 0/1 predictions at the given threshold."""
        return (self.predict_proba(X) > threshold).astype(int)


def load_adapter(adapter_path: str) -> ModelAdapter:
    """
    Dynamically import a user's adapter .py file and validate it.

    This is the function the CLI calls. It intentionally fails loudly
    and specifically — a vague stack trace here would be the single
    most frustrating first-run experience for a new user, since it's
    the very first thing that runs.
    """
    path = Path(adapter_path).resolve()
    if not path.exists():
        raise AdapterError(f"Adapter file not found: {path}")
    if path.suffix != ".py":
        raise AdapterError(f"Adapter file must be a .py file, got: {path.suffix}")

    module_name = f"whitebox_user_adapter_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AdapterError(f"Could not load adapter module from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 — we deliberately re-wrap any error
        raise AdapterError(
            f"Adapter file '{path.name}' raised an error while loading:\n  {exc}\n"
            "Common causes: a missing dependency your model needs (e.g. "
            "the library the model was pickled with), or a wrong path to "
            "your saved model file inside the adapter."
        ) from exc

    if not hasattr(module, "predict_proba"):
        raise AdapterError(
            f"Adapter file '{path.name}' does not define a predict_proba(X) "
            "function. See examples/sklearn_adapter.py for the required "
            "shape."
        )

    feature_names = getattr(module, "FEATURE_NAMES", None)

    return ModelAdapter(
        predict_proba_fn=module.predict_proba,
        feature_names=feature_names,
        source_path=str(path),
    )
