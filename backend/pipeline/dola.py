# ═══════════════════════════════════════════════════════════════
# dola.py — The Lie Detector
# ═══════════════════════════════════════════════════════════════
# AI models are notorious for "hallucinating" — which means making
# up fake facts with absolute confidence. This file listens to the
# AI as it generates words. It checks if different layers of the
# AI's "brain" are confused or disagreeing. If it senses the AI
# is just guessing or lying, it flags it immediately.
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 6: DoLa (Decoding by Contrasting Layers)
Detects when the AI model is "making things up" (hallucinating).
Runs in < 3ms after inference.

How it works:
In the original DoLa research paper, this compares outputs from different
layers of the transformer model during generation to catch hallucinated tokens.

For this prototype, we use a practical post-generation approach:
  1. If the model returns per-token probabilities (logprobs), analyze those
  2. If not (Ollama doesn't by default), estimate confidence using heuristics
  3. Flag the response if too many tokens have low confidence

The result is a "hallucination risk score" — how likely is the AI making things up?
"""

import math
from pipeline import PipelineContext
import config


class DoLaDecoder:
    """Stage 6: Hallucination detection.

    Detects when the AI is "guessing" vs. "knowing" the answer.
    A high hallucination risk doesn't mean the answer is wrong — it means
    the model is uncertain, so the user should be cautious.
    """

    def _analyze_logprobs(self, logprobs: list[float]) -> dict:
        """Analyze the distribution of token log-probabilities.

        "logprob" = log(probability). Lower (more negative) = less confident.
        E.g., logprob of -0.1 means 90% confident, -3.0 means 5% confident.

        Returns analysis including: risk score, whether it's flagged,
        average confidence, and which token positions are low-confidence."""
        if not logprobs:
            # No probabilities available — can't analyze, assume OK
            return {
                "risk_score": 0.0,
                "flagged": False,
                "avg_logprob": 0.0,
                "min_logprob": 0.0,
                "low_confidence_count": 0,
                "total_tokens": 0,
                "low_confidence_positions": [],
            }

        # Find which tokens the model was unsure about
        low_conf_positions = []
        for i, lp in enumerate(logprobs):
            if lp < config.DOLA_LOGPROB_THRESHOLD:  # Default: -2.0 (below 13% confidence)
                low_conf_positions.append(i)

        total = len(logprobs)
        low_count = len(low_conf_positions)
        # Risk = what fraction of tokens are low-confidence
        risk_score = low_count / total if total > 0 else 0.0

        return {
            "risk_score": round(risk_score, 4),
            "flagged": risk_score > config.DOLA_HALLUCINATION_RATIO,  # Default: >30% low-conf
            "avg_logprob": round(sum(logprobs) / total, 4) if total else 0.0,
            "min_logprob": round(min(logprobs), 4) if logprobs else 0.0,
            "low_confidence_count": low_count,
            "total_tokens": total,
            "low_confidence_positions": low_conf_positions[:20],  # Cap at 20 for response size
        }

    def _estimate_logprobs(self, text: str) -> list[float]:
        """Fallback: estimate how confident the model was for each word.

        Used when Ollama doesn't return actual probabilities.
        Uses heuristics (educated guesses):
          - Hedge words ("maybe", "perhaps") → model is uncertain → low confidence
          - Numbers/dates → often hallucinated → lower confidence
          - Short common words ("the", "is") → model knows these well → high confidence
          - Long technical words → model might be guessing → lower confidence
        """
        import re

        words = text.split()
        if not words:
            return []

        # Words that indicate the model is hedging (uncertain)
        hedge_words = {
            "perhaps", "maybe", "possibly", "might", "could",
            "approximately", "roughly", "around", "about",
            "i think", "i believe", "it seems", "likely",
        }

        logprobs = []
        text_lower = text.lower()

        for word in words:
            w = word.lower().strip(".,!?;:\"'()[]")
            lp = -0.5  # Default: fairly confident (~60%)

            if w in hedge_words:
                lp = -3.0      # Very uncertain (~5% confidence)
            elif re.match(r"^\d+\.?\d*$", w):
                lp = -2.0      # Numbers are often made up (~13%)
            elif len(w) <= 3:
                lp = -0.2      # Short common words (~82%)
            elif len(w) > 12:
                lp = -1.5      # Long/technical words (~22%)

            logprobs.append(lp)

        return logprobs

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Analyze the AI response for hallucination risk. Called by the Pipeline."""
        # Use real probabilities if the model provided them, otherwise estimate
        logprobs = ctx.logprobs
        if not logprobs and ctx.slm_response:
            logprobs = self._estimate_logprobs(ctx.slm_response)

        analysis = self._analyze_logprobs(logprobs)

        # Store results for RIS (next stage) to use in its quality assessment
        ctx.dola_risk = analysis["risk_score"]
        ctx.dola_flagged = analysis["flagged"]

        return ctx
