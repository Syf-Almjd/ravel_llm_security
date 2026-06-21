# ═══════════════════════════════════════════════════════════════
# ease.py — The Smart Traffic Controller
# ═══════════════════════════════════════════════════════════════
# Not every question needs a super-smart, slow brain. If a user
# asks something simple like "What time is it?", this file routes
# it directly to a fast, cheap processing path. If the question
# is a complex math or logic problem, it turns on advanced
# reasoning ("Chain of Thought"). This saves massive amounts of
# computer power and money.
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 3: EASE (Extractive Adaptive Selection Engine)
Routes queries based on how complex they are. Runs in < 2ms.

Why route by complexity?
- Simple questions ("What is 2+2?") don't need chain-of-thought reasoning
- Complex questions ("Explain why...") benefit from step-by-step thinking
- Suspicious/ambiguous queries get extra scrutiny

Three routes:
  DIRECT     — Simple question, answer directly (saves compute)
  COT        — Complex question, use chain-of-thought reasoning
  BORDERLINE — Suspicious/ambiguous, apply extra caution
"""

import re
from pipeline import PipelineContext
import config

# ── Complexity signals ───────────────────────────────────────
# These regex patterns help classify how complex a question is.

# Simple question starters (e.g., "What is X?", "Define Y", "List Z")
SIMPLE_PATTERNS = re.compile(
    r"^(?:what\s+is|who\s+is|define|list|name)\b", re.IGNORECASE
)

# Complex question markers (e.g., "Why does...", "Explain how...", "Compare X and Y")
COMPLEX_PATTERNS = re.compile(
    r"\b(?:why|how\s+does|how\s+would|explain|compare|contrast|analyze|evaluate)\b",
    re.IGNORECASE,
)

# Conditional / hypothetical markers (e.g., "What if...", "Suppose that...", "Imagine...")
CONDITIONAL_PATTERNS = re.compile(
    r"\b(?:if|suppose|assume|imagine|hypothetically|what\s+would\s+happen|could\s+it)\b",
    re.IGNORECASE,
)

# Multi-step reasoning markers (e.g., "First do X, then do Y", "Step by step")
MULTI_STEP_PATTERNS = re.compile(
    r"\b(?:first.*then|step\s+by\s+step|and\s+then|after\s+that|finally)\b",
    re.IGNORECASE,
)


class EASERouter:
    """Stage 3: Classifies query complexity and picks the best processing route."""

    def _length_score(self, text: str) -> float:
        """Longer queries tend to be more complex. Returns 0-1 score."""
        words = len(text.split())
        return min(words / 60.0, 1.0)  # Normalize: 60+ words = max complexity

    def _question_complexity(self, text: str) -> float:
        """Score based on the type of question being asked."""
        if SIMPLE_PATTERNS.search(text):
            return 0.1   # Very simple
        if COMPLEX_PATTERNS.search(text):
            return 0.8   # Very complex
        return 0.4       # Neutral/medium

    def _conditional_score(self, text: str) -> float:
        """Hypothetical language ("what if...") implies higher complexity."""
        matches = CONDITIONAL_PATTERNS.findall(text)
        return min(len(matches) * 0.4, 1.0)  # Each "if" adds 0.4 to the score

    def _multi_step_score(self, text: str) -> float:
        """Questions asking for multiple steps are more complex."""
        matches = MULTI_STEP_PATTERNS.findall(text)
        return min(len(matches) * 0.5, 1.0)

    def _clause_count(self, text: str) -> float:
        """More commas/semicolons/conjunctions = more complex sentence structure."""
        separators = len(re.findall(r"[,;]|\band\b|\bbut\b|\bor\b|\bhowever\b", text))
        return min(separators / 5.0, 1.0)  # 5+ separators = max

    def _compute_score(self, text: str) -> float:
        """Combine all complexity signals into a single score (0-1).
        Each signal gets a weight based on how important it is."""
        score = (
            self._length_score(text) * 0.15          # 15% weight for length
            + self._question_complexity(text) * 0.30  # 30% weight for question type
            + self._conditional_score(text) * 0.20    # 20% weight for hypotheticals
            + self._multi_step_score(text) * 0.15     # 15% weight for multi-step
            + self._clause_count(text) * 0.20         # 20% weight for sentence structure
        )
        return round(min(score, 1.0), 3)

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Score the query and route it to the appropriate path."""
        text = ctx.sanitized_input
        score = self._compute_score(text)

        # Pick the route based on the complexity score thresholds
        if score < config.EASE_DIRECT_THRESHOLD:     # Default: < 0.30
            route = "DIRECT"       # Simple — just answer directly
        elif score < config.EASE_COT_THRESHOLD:       # Default: < 0.70
            route = "COT"          # Complex — use chain-of-thought reasoning
        else:
            route = "BORDERLINE"   # Very complex or suspicious — be extra careful

        ctx.ease_route = route
        ctx.ease_score = score
        return ctx
