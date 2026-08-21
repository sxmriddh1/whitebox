"""
config.py — all user-facing configuration lives here.

WHERE TO PUT YOUR GROQ API KEY
-------------------------------
Whitebox's optional plain-English explanation layer calls Groq's API
(https://console.groq.com) to run an LLM (llama-3.1-8b-instant by
default) that turns raw SHAP numbers into a human-readable sentence.
This step is entirely optional — everything else in Whitebox (SHAP,
surrogate tree, adversarial audit, defenses) runs with zero API key.

To enable it, do ONE of the following:

  Option A (recommended) — environment variable:
      export GROQ_API_KEY="your-key-here"

  Option B — .env file in the directory you run whitebox from:
      1. Copy .env.example to .env
      2. Paste your key into .env
      (python-dotenv, a dependency of this project, loads it
      automatically — see the load_dotenv() call below.)

  Option C — CLI flag, for one-off runs:
      whitebox audit ... --groq-api-key "your-key-here"
      (Not recommended for shared machines — it can be visible in
      shell history. Options A/B are safer.)

NEVER hardcode your API key directly into any .py file in this repo.
A key committed to a public GitHub repo is typically scraped by bots
within minutes of the push.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # silently does nothing if no .env file exists
except ImportError:
    # python-dotenv is a soft dependency — Whitebox still works with
    # a plain `export GROQ_API_KEY=...` even if it's not installed.
    pass


DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


@dataclass
class WhiteboxConfig:
    """
    Central config object threaded through the whole pipeline.

    Every field has a sane default, so `WhiteboxConfig()` with no
    arguments is a valid, runnable configuration (minus the LLM layer,
    which silently disables itself if no key is found — see
    llm_layer.py).
    """

    # --- LLM layer (optional) ---
    groq_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("GROQ_API_KEY")
    )
    groq_model: str = DEFAULT_GROQ_MODEL
    llm_temperature: float = 0.0  # 0 = literal/consistent, not creative

    # --- SHAP layer ---
    shap_background_size: int = 50   # rows sampled for KernelExplainer background
    shap_sample_size: int = 50       # how many test rows to explain

    # --- Surrogate tree ---
    surrogate_max_depth: int = 4

    # --- Adversarial audit ---
    audit_top_k_features: int = 3      # features targeted by evasion attack
    audit_borderline_n: int = 20       # borderline examples tested per audit
    audit_evasion_steps: int = 20      # interpolation steps, 0..1
    audit_decoy_alpha: float = 4.0     # push strength for explanation-manipulation attack
    audit_decoy_batch_n: int = 15      # examples tested for decoy attack

    # --- Defenses ---
    defense_smoothing_small_std: float = 0.1
    defense_smoothing_large_std: float = 0.5
    defense_clip_sigma: float = 3.0

    # --- Output ---
    output_dir: str = "whitebox_report"
    random_seed: int = 42

    def has_llm(self) -> bool:
        """Whether the LLM narration layer can run at all."""
        return bool(self.groq_api_key)
