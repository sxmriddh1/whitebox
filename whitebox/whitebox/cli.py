"""
cli.py — the command-line entry point. This is the primary, intended
way to use Whitebox (see README.md "Quickstart").

DESIGN INTENT: every command prints context before it prints numbers.
A user should be able to run `whitebox audit ...` having never read
a SHAP paper and still understand what each phase did and why it
matters, purely from the terminal output.
"""

import sys
from pathlib import Path

import click
import numpy as np
import pandas as pd

from . import __version__
from .audit import run_audit
from .config import WhiteboxConfig
from .model_adapter import AdapterError, load_adapter
from .report import render_terminal_report, save_report


BANNER = r"""
 __      _____  _  ____ ____   _____  __
 \ \    / / __ \| |/ / _ \  _ \ / _ \ \/ /
  \ \  / / |  | | | | | |_| |  _/ | | \  /
   \ \/ /| |__| | | |_| |  _ <| |_| /  \
    \__/  \____/|_|\____|_| \_\\___/_/\_\

 Whitebox — can you trust what your model tells you, and why?
"""


@click.group()
@click.version_option(version=__version__, prog_name="whitebox")
def cli():
    """Whitebox: an explainability trust auditor for tabular ML models."""
    pass


@cli.command()
@click.option(
    "--data", "data_path", required=True, type=click.Path(exists=True),
    help="Path to a CSV file containing your feature columns (and, "
         "optionally, the target column).",
)
@click.option(
    "--target", "target_col", default=None,
    help="Name of the label/target column in --data, if present. It will "
         "be dropped before being passed to your model. Not required — "
         "Whitebox only needs your model's own predictions, not ground "
         "truth — but useful for context in the report.",
)
@click.option(
    "--adapter", "adapter_path", required=True, type=click.Path(exists=True),
    help="Path to your model adapter .py file. See "
         "examples/sklearn_adapter.py for the required shape "
         "(a predict_proba(X) function).",
)
@click.option(
    "--output", "output_dir", default="whitebox_report", show_default=True,
    help="Directory to write report.txt, report.json, and "
         "surrogate_rules.txt into.",
)
@click.option(
    "--sample-size", default=50, show_default=True,
    help="How many rows to run SHAP + narration on. Larger = slower but "
         "more representative.",
)
@click.option(
    "--decoy-alpha", default=4.0, show_default=True,
    help="Push strength (in standardized-feature units) for the "
         "explanation-manipulation attack's decoy feature. See "
         "attacks.py's module docstring before changing this.",
)
@click.option(
    "--groq-api-key", default=None,
    help="Groq API key for the plain-English narration layer. Prefer "
         "setting the GROQ_API_KEY environment variable instead — see "
         "config.py's docstring for why.",
)
@click.option(
    "--no-llm", is_flag=True, default=False,
    help="Skip the plain-English narration layer entirely, even if a "
         "Groq API key is configured.",
)
@click.option("--quiet", is_flag=True, default=False, help="Suppress phase-by-phase narration during the run.")
def audit(
    data_path, target_col, adapter_path, output_dir, sample_size,
    decoy_alpha, groq_api_key, no_llm, quiet,
):
    """
    Run the full Whitebox audit: explain, distill, narrate, attack, defend.

    \b
    Example:
        whitebox audit --data applications.csv --target approved \\
            --adapter my_model_adapter.py --output report/
    """
    if not quiet:
        click.echo(click.style(BANNER, fg="cyan"))

    # ---- load adapter ----
    click.echo(f"Loading model adapter from {adapter_path} ...")
    try:
        adapter = load_adapter(adapter_path)
    except AdapterError as e:
        click.echo(click.style(f"ADAPTER ERROR: {e}", fg="red"), err=True)
        sys.exit(1)
    click.echo("  adapter loaded OK.")

    # ---- load data ----
    click.echo(f"Loading data from {data_path} ...")
    df = pd.read_csv(data_path)
    if target_col and target_col in df.columns:
        df = df.drop(columns=[target_col])

    non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        click.echo(
            click.style(
                f"  WARNING: non-numeric columns found and dropped: {non_numeric}. "
                "Whitebox expects an already-encoded, already-scaled feature "
                "matrix — one-hot encode categorical columns and standardize "
                "numeric ones before passing data in, the same way you "
                "prepared data for your model.",
                fg="yellow",
            )
        )
        df = df.drop(columns=non_numeric)

    feature_names = adapter.feature_names or df.columns.tolist()
    if adapter.feature_names and list(df.columns) != list(adapter.feature_names):
        click.echo(
            click.style(
                "  NOTE: using FEATURE_NAMES from your adapter file, which "
                "differs from --data's column order. Make sure --data's "
                "columns are in the same order your model expects.",
                fg="yellow",
            )
        )

    X = df.to_numpy(dtype=float)
    click.echo(f"  loaded {X.shape[0]} rows x {X.shape[1]} features.")

    # ---- build config ----
    config = WhiteboxConfig(
        groq_api_key=(None if no_llm else (groq_api_key or WhiteboxConfig().groq_api_key)),
        shap_sample_size=sample_size,
        audit_decoy_alpha=decoy_alpha,
        output_dir=output_dir,
    )

    # ---- run pipeline ----
    click.echo("\nStarting audit pipeline. This calls your model many times "
               "and may take a few minutes depending on model speed and "
               "--sample-size.\n")
    report = run_audit(adapter, X, feature_names, config, verbose=not quiet)

    # ---- render + save ----
    text_report = render_terminal_report(report)
    click.echo("\n" + text_report)

    save_report(report, output_dir)
    click.echo(
        click.style(
            f"\nFull report saved to: {Path(output_dir).resolve()}/"
            f" (report.txt, report.json, surrogate_rules.txt)",
            fg="green",
        )
    )


@cli.command()
def check_env():
    """
    Quick diagnostic: checks which optional dependencies and
    configuration are available, without running a full audit.
    Useful as a first command to run after installing.
    """
    click.echo(click.style(BANNER, fg="cyan"))
    click.echo("Environment check:\n")

    def _check(label, ok, detail=""):
        symbol = click.style("OK", fg="green") if ok else click.style("MISSING", fg="red")
        click.echo(f"  [{symbol}] {label}" + (f" — {detail}" if detail else ""))

    try:
        import shap  # noqa
        _check("shap (real SHAP attributions)", True)
    except ImportError:
        _check("shap (real SHAP attributions)", False, "pip install shap — falling back to permutation approximation without it")

    try:
        import groq  # noqa
        _check("groq (LLM narration client)", True)
    except ImportError:
        _check("groq (LLM narration client)", False, "pip install groq — narration layer disabled without it")

    import os
    has_key = bool(os.environ.get("GROQ_API_KEY"))
    _check("GROQ_API_KEY environment variable", has_key,
           "see config.py docstring for how to set this" if not has_key else "")

    click.echo("\nAll other dependencies (numpy, pandas, scikit-learn, click) "
               "are required, not optional — if you got this far, they're "
               "already installed.")


if __name__ == "__main__":
    cli()
