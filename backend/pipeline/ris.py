# ═══════════════════════════════════════════════════════════════
# ris.py — The Final Quality Grader
# ═══════════════════════════════════════════════════════════════
# Before the user sees the answer, this file scores the AI's
# response on a scale of 0 to 100. It looks at four metrics:
# Is it safe? Is it actually backed up by facts? Does it make
# sense? Is it the right length? If the score is too low, it
# blocks the answer and says, "Sorry, I cannot safely answer that."
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 7: RIS (Reasoning Integrity Score)
The final quality gate — scores every AI response from 0–100. Runs in < 3ms.

This is the "quality inspector" of the pipeline. After all the previous stages
have processed the request, RIS looks at the final response and asks:

  "Is this answer actually good?"

It combines four metrics into one score:
  Safety (25%)      — Did the Guard flag any issues? (from Stage 2)
  Grounding (30%)   — Does the answer use the retrieved facts? (from Stage 4)
  Coherence (25%)   — Is the AI confident in what it said? (from Stage 6)
  Consistency (20%) — Is the response a reasonable length?

Score → Verdict:
  ≥ 80  → PASS   (send to user with confidence)
  50–79 → WARN   (send to user but flag as uncertain)
  < 50  → BLOCK  (don't send — replace with a safe fallback message)
"""

import re
import math
from pipeline import PipelineContext
import config


class RISScorer:
    """Stage 7: The final quality gate.

    Every response gets a RIS score before it reaches the user.
    This ensures that even if an AI generates something, it's checked
    for quality before being shown.
    """

    def _safety_score(self, ctx: PipelineContext) -> float:
        """Score 0–100 based on Guard confidence.
        If the Guard flagged the input, safety is 0."""
        if not ctx.guard_safe:
            return 0.0
        return ctx.guard_confidence * 100.0

    def _grounding_score(self, ctx: PipelineContext) -> float:
        """Score 0–100 based on how well the response uses the retrieved facts.

        If the AI's answer shares words with the fact-cards from RAG,
        it's considered "grounded" (based on real information).
        If it doesn't overlap at all, it might be making things up."""
        if not ctx.fact_cards or not ctx.slm_response:
            return 50.0  # No facts available — neutral score (not penalized)

        response_lower = ctx.slm_response.lower()
        # Extract significant words (4+ chars) from the response
        response_words = set(re.findall(r"\b\w{4,}\b", response_lower))

        if not response_words:
            return 50.0

        # Extract significant words from the fact-cards
        fact_words = set()
        for card in ctx.fact_cards:
            for fact in card.get("facts", []):
                fact_words.update(re.findall(r"\b\w{4,}\b", fact.lower()))

        if not fact_words:
            return 50.0

        # How much do the response and facts overlap?
        overlap = response_words & fact_words
        overlap_ratio = len(overlap) / max(len(response_words), 1)

        # Scale to 0–100 (with a boost — even partial overlap is good)
        score = min(overlap_ratio * 150.0, 100.0)
        return round(score, 1)

    def _coherence_score(self, ctx: PipelineContext) -> float:
        """Score 0–100 based on DoLa hallucination analysis.
        Low hallucination risk = high coherence = good score."""
        risk = ctx.dola_risk
        score = (1.0 - risk) * 100.0  # Invert: low risk → high score
        return round(max(0.0, min(score, 100.0)), 1)

    def _consistency_score(self, ctx: PipelineContext) -> float:
        """Score 0–100 based on response length.

        Why does length matter?
        - Very short (< 10 words) → probably not a real answer
        - Sweet spot (20–200 words) → well-formed answer
        - Very long (> 400 words) → might be rambling or hallucinating"""
        response = ctx.slm_response
        if not response:
            return 0.0

        word_count = len(response.split())

        if 20 <= word_count <= 200:
            return 90.0    # Ideal length
        elif 10 <= word_count < 20:
            return 70.0    # A bit short but OK
        elif 200 < word_count <= 400:
            return 75.0    # A bit long but OK
        elif word_count < 10:
            return 40.0    # Suspiciously short
        else:
            return 60.0    # Very long — might be rambling

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Calculate the composite RIS score and determine the final verdict."""
        # If the Guard blocked this request, the score is automatically 0
        if ctx.guard_blocked:
            ctx.ris_score = 0.0
            ctx.ris_verdict = "BLOCK"
            ctx.ris_breakdown = {
                "safety": 0.0,
                "grounding": 0.0,
                "coherence": 0.0,
                "consistency": 0.0,
            }
            return ctx

        # Calculate each component score
        safety = self._safety_score(ctx)
        grounding = self._grounding_score(ctx)
        coherence = self._coherence_score(ctx)
        consistency = self._consistency_score(ctx)

        # Combine with configurable weights (from config.py)
        weights = config.RIS_WEIGHTS
        ris = (
            safety * weights["safety"]           # 25% weight
            + grounding * weights["grounding"]    # 30% weight
            + coherence * weights["coherence"]    # 25% weight
            + consistency * weights["consistency"]  # 20% weight
        )

        ctx.ris_score = round(ris, 1)
        ctx.ris_breakdown = {
            "safety": round(safety, 1),
            "grounding": round(grounding, 1),
            "coherence": round(coherence, 1),
            "consistency": round(consistency, 1),
        }

        # Determine the final verdict based on score thresholds
        if ris >= config.RIS_HIGH_THRESHOLD:    # Default: ≥ 80
            ctx.ris_verdict = "PASS"    # Good to go!
        elif ris >= config.RIS_LOW_THRESHOLD:   # Default: ≥ 50
            ctx.ris_verdict = "WARN"    # Send but flag as uncertain
        else:
            ctx.ris_verdict = "BLOCK"   # Don't send — replace with fallback
            ctx.slm_response = (
                "This response did not meet our quality threshold. "
                "Please try rephrasing your question for better results."
            )

        return ctx
