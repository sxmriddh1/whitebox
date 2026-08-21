"""
report.py — turns an AuditReport into human-readable output, both on
the terminal (rich, explanatory, with context — not just numbers) and
as saved files (a Markdown report + raw JSON for programmatic use).

This module is deliberately verbose. The CLI's whole value
proposition is that someone unfamiliar with SHAP internals can run
one command and understand what happened and why it matters — that
requires narration around every number, not just the number itself.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .audit import AuditReport


HR = "=" * 72
SUBHR = "-" * 72


def _severity_label(rate: float) -> str:
    """Turn a raw success-rate float into a plain-language severity tag."""
    if rate == 0:
        return "NONE OBSERVED"
    if rate < 0.15:
        return "LOW"
    if rate < 0.40:
        return "MODERATE"
    return "HIGH"


def render_terminal_report(report: AuditReport) -> str:
    """Build the full descriptive terminal report as one string."""
    lines = []
    w = lines.append

    w(HR)
    w("WHITEBOX AUDIT REPORT")
    w(HR)
    w("")
    w("WHAT THIS REPORT IS")
    w(
        "  Whitebox tested your model in two stages. First, it explained your\n"
        "  model's decisions (which features drive them, and why) using SHAP\n"
        "  and a distilled surrogate tree. Second — the part most explainability\n"
        "  tools skip — it tried to BREAK those explanations: to make the model\n"
        "  give a misleading reason for a decision without changing the decision\n"
        "  itself. What follows is what it found."
    )
    w("")

    # ---------------- Section 1: Explainability summary ----------------
    w(SUBHR)
    w("1. FEATURE ATTRIBUTION (SHAP)")
    w(SUBHR)
    w(
        f"  Method: {report.attribution.method}"
        + (
            "  [WARNING: fallback mode — install `shap` for real attributions]"
            if report.attribution.method == "permutation_fallback"
            else ""
        )
    )
    w(f"  Rows explained: {report.n_rows_explained}")
    w("")
    w("  Top features driving your model's decisions overall:")
    w("")
    w(f"  {'Rank':<6}{'Feature':<30}{'Mean |Attribution|':<20}")
    for i, row in enumerate(report.attribution.global_ranking()[:10], start=1):
        w(f"  {i:<6}{row['feature']:<30}{row['mean_abs_attribution']:<20.4f}")
    w("")

    # ---------------- Section 2: Surrogate ----------------
    w(SUBHR)
    w("2. SURROGATE MODEL (GLOBAL INTERPRETABILITY)")
    w(SUBHR)
    w(
        "  A shallow, fully-readable decision tree was trained to mimic your\n"
        "  model's own predictions (not the real ground-truth labels) — this\n"
        "  measures how well a simple rule-set can stand in for your model."
    )
    w(f"  Tree depth: {report.surrogate.max_depth}")
    w(f"  Fidelity to black-box model: {report.surrogate.fidelity:.2%}")
    if report.surrogate.fidelity < 0.80:
        w(
            "  NOTE: fidelity below 80% means the readable tree meaningfully\n"
            "  disagrees with your actual model on a substantial fraction of\n"
            "  cases — treat the tree as a rough sketch, not a faithful summary."
        )
    w("")

    # ---------------- Section 3: LLM narration ----------------
    w(SUBHR)
    w("3. PLAIN-ENGLISH NARRATION (LLM)")
    w(SUBHR)
    if report.llm_enabled:
        for i, expl in enumerate(report.sample_narrations, start=1):
            w(f"  Sample explanation {i}:")
            w(f"    completeness: {expl.completeness_ratio():.0%} of given features mentioned")
            for line in expl.text.strip().splitlines():
                w(f"    {line}")
            w("")
    else:
        w(f"  SKIPPED — {report.llm_disabled_reason}")
    w("")

    # ---------------- Section 4: Adversarial audit ----------------
    w(SUBHR)
    w("4. ADVERSARIAL AUDIT")
    w(SUBHR)
    w("")
    w("  4a. Evasion attack (changing the actual decision)")
    w(
        "      Question answered: can a real decision be flipped by nudging only\n"
        "      the features the explainer says matter most?"
    )
    ev = report.evasion
    ev_sev = _severity_label(ev.success_rate)
    w(f"      Tested: {ev.n_tested} borderline-confidence examples")
    w(f"      Flipped: {ev.n_success} ({ev.success_rate:.1%})  ->  severity: {ev_sev}")
    w("")
    w("  4b. Explanation manipulation attack (changing the STATED REASON only)")
    w(
        "      Question answered: while the decision stays fixed, can the\n"
        "      explanation be hijacked to blame a different, irrelevant feature?\n"
        "      This is the more dangerous attack — the decision looks unchanged,\n"
        "      but the audit trail an analyst would trust is now false."
    )
    mn = report.manipulation
    mn_sev = _severity_label(mn.success_rate)
    w(f"      Tested: {mn.n_tested}  |  decision-stable: {mn.n_decision_stable}  "
      f"|  excluded (decision flipped): {mn.n_contaminated}")
    w(
        f"      Explanation hijacked: {mn.n_success_among_stable}/"
        f"{mn.n_decision_stable} stable trials ({mn.success_rate:.1%})  ->  "
        f"severity: {mn_sev}"
    )
    w("")

    # ---------------- Section 5: Defenses ----------------
    w(SUBHR)
    w("5. DEFENSE EVALUATION")
    w(SUBHR)
    w(
        "  Each defense below was evaluated against the explanation-manipulation\n"
        "  attack (4b). 'Attack success rate' is the same metric as above,\n"
        "  measured AFTER the defense is applied — lower is better, and it\n"
        "  should be compared against the undefended baseline in 4b."
    )
    w("")
    w(f"  {'Defense':<28}{'Tested':<10}{'Stable':<10}{'Attack Success':<16}{'vs. Baseline'}")
    baseline = mn.success_rate
    for d in report.defenses:
        delta = d.attack_success_rate - baseline
        arrow = "better" if delta < -0.02 else ("worse" if delta > 0.02 else "≈ no change")
        w(
            f"  {d.name:<28}{d.n_tested:<10}{d.n_decision_stable:<10}"
            f"{d.attack_success_rate:<16.1%}{arrow}"
        )
    w("")
    if all(d.attack_success_rate >= baseline - 0.02 for d in report.defenses):
        w(
            "  HONEST CONCLUSION: no tested defense reduced explanation-\n"
            "  manipulation success below the undefended baseline. This is a\n"
            "  legitimate finding, not a tool failure — adversarial robustness\n"
            "  in explainable AI is, as of this writing, an open research\n"
            "  problem. See README.md's research section for related work."
        )
    w("")
    w(HR)
    w("SUMMARY TABLE")
    w(HR)
    w(f"  {'Check':<40}{'Result'}")
    w(f"  {'Surrogate fidelity':<40}{report.surrogate.fidelity:.1%}")
    w(f"  {'Evasion attack success':<40}{ev.success_rate:.1%} ({ev_sev})")
    w(f"  {'Explanation manipulation success':<40}{mn.success_rate:.1%} ({mn_sev})")
    best_defense = min(report.defenses, key=lambda d: d.attack_success_rate, default=None)
    if best_defense:
        w(
            f"  {'Best defense found':<40}"
            f"{best_defense.name} ({best_defense.attack_success_rate:.1%})"
        )
    w(HR)

    return "\n".join(lines)


def report_to_dict(report: AuditReport) -> Dict[str, Any]:
    """JSON-serializable dump of every number in the report."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_rows_explained": report.n_rows_explained,
        "feature_names": report.feature_names,
        "attribution_method": report.attribution.method,
        "global_feature_ranking": report.attribution.global_ranking(),
        "surrogate": {
            "fidelity": report.surrogate.fidelity,
            "max_depth": report.surrogate.max_depth,
            "rules": report.surrogate.rules_as_text(),
        },
        "llm_enabled": report.llm_enabled,
        "llm_disabled_reason": report.llm_disabled_reason,
        "narrations": [
            {
                "text": e.text,
                "model_used": e.model_used,
                "completeness_ratio": e.completeness_ratio(),
            }
            for e in report.sample_narrations
        ],
        "evasion_attack": {
            "n_tested": report.evasion.n_tested,
            "n_success": report.evasion.n_success,
            "success_rate": report.evasion.success_rate,
            "per_example": report.evasion.per_example,
        },
        "explanation_manipulation_attack": {
            "n_tested": report.manipulation.n_tested,
            "n_decision_stable": report.manipulation.n_decision_stable,
            "n_contaminated": report.manipulation.n_contaminated,
            "success_rate": report.manipulation.success_rate,
            "per_example": report.manipulation.per_example,
        },
        "defenses": [
            {
                "name": d.name,
                "n_tested": d.n_tested,
                "n_decision_stable": d.n_decision_stable,
                "attack_success_rate": d.attack_success_rate,
            }
            for d in report.defenses
        ],
    }


def save_report(report: AuditReport, output_dir: str) -> None:
    """
    Writes three files to output_dir:
      - report.txt   (identical to what was printed to the terminal)
      - report.json  (full machine-readable dump)
      - surrogate_rules.txt (the distilled tree's rules, standalone)
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "report.txt").write_text(render_terminal_report(report), encoding="utf-8")
    (out / "report.json").write_text(
        json.dumps(report_to_dict(report), indent=2), encoding="utf-8"
    )
    (out / "surrogate_rules.txt").write_text(
        report.surrogate.rules_as_text(), encoding="utf-8"
    )
