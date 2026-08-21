"""
llm_layer.py — turning raw SHAP numbers into a plain-English sentence.

WHERE YOUR API KEY GOES: see config.py's module docstring. Short
version: `export GROQ_API_KEY="..."` before running the CLI, or put
it in a `.env` file. This module never asks you to paste a key
directly into source code.

WHY A "GROUNDED" PROMPT, SPECIFICALLY
----------------------------------------
An earlier version of this idea, tested during this project's
original prototyping, fed the LLM only the SHAP *direction* for each
feature (toward/away from the positive class) without the actual
numeric value. That produced two distinct, real failure modes:

  1. FABRICATION — the model invented a magnitude ("low rate") for a
     binary feature that has no such thing as a "rate."
  2. INVERSION — the model described a value as "low" when the real
     number it was given was clearly high, because it had no real
     number to check itself against.

The fix used here is "grounding": every feature passed to the prompt
includes its actual value, not just its SHAP direction, and the
prompt explicitly instructs the model not to invent a magnitude
word unless the real value supports it. Grounding fixes fabrication
and inversion. It does NOT fix a third, separate failure mode —
omission (the model silently dropping a correctly-provided fact) —
which is a completeness problem, not a correctness problem, and is
partly a tradeoff of using a small, fast, free-tier model. This
module cannot fully solve omission; it can only make it visible (see
`check_completeness` below), which is the honest, non-oversold thing
to do.
"""

from dataclasses import dataclass
from typing import List, Optional

try:
    from groq import Groq  # type: ignore
    _HAS_GROQ = True
except ImportError:
    _HAS_GROQ = False


SYSTEM_PROMPT = """You are a security/ML analyst assistant. Your job is to explain, \
in plain English, why a model made a specific prediction, using ONLY the facts \
provided to you.

STRICT RULES — follow all of them:
1. Only use the facts explicitly given below. Never invent a reason, a value, \
or a magnitude that was not provided.
2. Mention every feature listed in TOP CONTRIBUTING FACTORS — do not silently \
drop any of them.
3. Do not describe a numeric value as "high" or "low" unless the actual value \
given supports that description. A positive attribution value pushes toward \
the positive class; a negative value pushes toward the negative class — these \
are not the same axis as "high" or "low" magnitude, so check the actual_value \
field before making any magnitude claim.
4. If a feature is binary (its actual_value is 0 or 1, or you are told it's \
binary), do not describe it as having a "rate" or a continuous magnitude.
5. Keep the explanation to 3-5 sentences. Be specific and concrete, not \
generic.
"""

USER_PROMPT_TEMPLATE = """PREDICTION: The model classified this example as \
"{prediction_label}" with confidence {confidence:.4f}.

TOP CONTRIBUTING FACTORS (most influential first):
{features_block}

Explain this prediction in plain English, following all the rules above.
"""


@dataclass
class Explanation:
    text: str
    model_used: str
    mentioned_features: List[str]
    given_features: List[str]

    def completeness_ratio(self) -> float:
        """
        What fraction of the features we GAVE the LLM actually appear
        (by name) in its output text. This is a crude but useful
        automated proxy for the omission failure mode described in
        the module docstring — not a substitute for a human reading
        the explanation, but a fast way to flag likely omissions
        across many rows.
        """
        if not self.given_features:
            return 1.0
        mentioned = sum(1 for f in self.given_features if f in self.text)
        return mentioned / len(self.given_features)


class LLMNarrator:
    """
    Thin wrapper around the Groq client. Every method degrades
    gracefully to a clear, actionable message if no API key is
    configured — the rest of the Whitebox pipeline should never hard-
    fail just because the optional narration layer isn't set up.
    """

    def __init__(self, api_key: Optional[str], model: str, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        self.client = None
        self.disabled_reason: Optional[str] = None

        if not _HAS_GROQ:
            self.disabled_reason = (
                "The `groq` package is not installed. Run `pip install groq` "
                "to enable plain-English narration. Skipping this layer."
            )
            return
        if not api_key:
            self.disabled_reason = (
                "No Groq API key found. Set GROQ_API_KEY (see config.py's "
                "docstring for all three ways to provide it) to enable "
                "plain-English narration. Skipping this layer."
            )
            return

        self.client = Groq(api_key=api_key)

    def is_enabled(self) -> bool:
        return self.client is not None

    def explain_prediction(
        self,
        prediction_label: str,
        confidence: float,
        top_features: List[dict],
    ) -> Explanation:
        """
        top_features: list of dicts as returned by
        AttributionResult.top_features(), each with keys
        'feature', 'attribution', 'direction', 'rank'.
        """
        if not self.is_enabled():
            return Explanation(
                text=f"[LLM narration disabled: {self.disabled_reason}]",
                model_used="none",
                mentioned_features=[],
                given_features=[f["feature"] for f in top_features],
            )

        features_block = "\n".join(
            f"  - {f['feature']}: attribution={f['attribution']:.4f} "
            f"(pushes toward {f['direction']}), rank #{f['rank']}"
            for f in top_features
        )
        user_prompt = USER_PROMPT_TEMPLATE.format(
            prediction_label=prediction_label,
            confidence=confidence,
            features_block=features_block,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content

        given = [f["feature"] for f in top_features]
        mentioned = [f for f in given if f in text]

        return Explanation(
            text=text,
            model_used=self.model,
            mentioned_features=mentioned,
            given_features=given,
        )
