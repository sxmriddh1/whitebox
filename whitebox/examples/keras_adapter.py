"""
examples/keras_adapter.py — a working example adapter for a Keras /
TensorFlow model (e.g. the Dense 122->64->32->1 style network this
project's original prototype used for network intrusion detection).

This demonstrates the point of the adapter pattern: Whitebox's core
package never imports tensorflow at all. It only ever calls whatever
predict_proba() your adapter defines, so a TensorFlow model, a
PyTorch model, and a scikit-learn model are all equally "generic"
to Whitebox — the adapter is where framework-specific code lives,
and nowhere else.
"""

import numpy as np
from tensorflow import keras

_model = keras.models.load_model("my_model.h5")  # <-- point at your saved model

FEATURE_NAMES = None  # optionally list your columns in model input order


def predict_proba(X: np.ndarray) -> np.ndarray:
    """
    Keras's model.predict() already returns a probability for a
    sigmoid-output binary classifier — just flatten it to 1D.
    """
    return _model.predict(X, verbose=0).flatten()


if __name__ == "__main__":
    dummy_row = np.zeros((1, _model.input_shape[1]))
    proba = predict_proba(dummy_row)
    print(f"Adapter self-test OK. predict_proba on a zero row returned: {proba}")
