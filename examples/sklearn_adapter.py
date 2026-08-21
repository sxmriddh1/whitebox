"""
examples/sklearn_adapter.py — a working example adapter for any
scikit-learn-compatible classifier (LogisticRegression, RandomForest,
XGBoost's sklearn API, LightGBM's sklearn API, etc.).

This is the file you copy and edit for YOUR model. Only two things
need to change for a typical scikit-learn model:
  1. The path passed to joblib.load()
  2. FEATURE_NAMES, if you want the report to use your real column
     names instead of falling back to --data's CSV header.

Run it standalone first to sanity-check it before pointing the CLI
at it:
    python examples/sklearn_adapter.py
"""

import joblib
import numpy as np

# ---------------------------------------------------------------
# 1. Load your trained model once, at import time. This runs a
#    single time when Whitebox starts, not on every prediction.
# ---------------------------------------------------------------
_model = joblib.load("my_model.pkl")  # <-- point this at your saved model


# ---------------------------------------------------------------
# 2. (Optional) list your feature columns in the exact order your
#    model expects them. If omitted, Whitebox uses --data's CSV
#    column order instead.
# ---------------------------------------------------------------
FEATURE_NAMES = None  # e.g. ["age", "income", "credit_score", ...]


# ---------------------------------------------------------------
# 3. The one required function. Must return a 1D array of
#    P(positive class) — one probability per input row.
# ---------------------------------------------------------------
def predict_proba(X: np.ndarray) -> np.ndarray:
    """
    X: shape (n_rows, n_features), already numeric and already
    preprocessed exactly the way your model expects (scaled,
    one-hot encoded, etc. — Whitebox does not preprocess for you).
    """
    return _model.predict_proba(X)[:, 1]


if __name__ == "__main__":
    # Quick self-test: run it directly with `python sklearn_adapter.py`
    # before wiring it into the CLI, so adapter bugs are obvious and
    # fast to find.
    dummy_row = np.zeros((1, _model.n_features_in_))
    proba = predict_proba(dummy_row)
    print(f"Adapter self-test OK. predict_proba on a zero row returned: {proba}")
