"""
Whitebox — an explainability trust auditor for any binary-classification
model on tabular data.

Whitebox does not just explain a black-box model. It explains it, then
deliberately tries to break that explanation, to answer one question:

    "When a model gives you a reason for its decision, can that reason
    itself be trusted, or can it be manipulated to hide the truth?"

Public entry points
--------------------
Most users should never import this package directly — the CLI
(`whitebox audit ...`) is the intended interface. But everything is
also usable as a library:

    from whitebox.audit import run_audit
    from whitebox.model_adapter import load_adapter

See README.md for the full walkthrough, and each module's docstring
for what that specific piece does and why it exists.
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
