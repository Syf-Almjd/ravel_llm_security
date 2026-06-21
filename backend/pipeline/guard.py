# ═══════════════════════════════════════════════════════════════
# guard.py — The Ultra-Fast Threat Detector
# ═══════════════════════════════════════════════════════════════
# This uses a lightning-fast, lightweight machine learning model
# (called an SVM) to read the message. Instead of using a heavy,
# expensive AI to double-check the safety, it acts like an instant
# reflex test. It flags malicious hacking attempts in under
# 5 milliseconds without slowing down the app.
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 2: Guard (ML Safety Classifier)
Runs in < 5ms — much faster than using another LLM as a guard.

Uses a two-tier approach:
  Tier 1: Keyword blocklist — instant match on obvious harmful requests
  Tier 2: SVM classifier — ML model trained on malicious vs. safe prompts

The SVM (Support Vector Machine) uses TF-IDF features to classify inputs.
It's trained by the train_guard.py script on labeled data.
"""

import json
import os
import re
import numpy as np
from pipeline import PipelineContext
import config


class Guard:
    """Stage 2: ML-based safety check.
    
    Why SVM instead of another LLM?
    - Speed: SVM runs in ~2ms vs. 100-500ms for an LLM guard
    - Cost: No GPU needed, runs on CPU
    - Deterministic: Same input always gives the same result
    """

    def __init__(self):
        self.blocklist_patterns: list[re.Pattern] = []
        self.svm = None           # The trained SVM model (from guard_svm.pkl)
        self.vectorizer = None    # The TF-IDF vectorizer (from tfidf_vectorizer.pkl)
        self._load_blocklist()    # Load keyword patterns
        self._load_model()        # Load ML model

    # ── Setup (runs once on startup) ─────────────────────────

    def _load_blocklist(self):
        """Load keyword blocklist from a JSON file, or use built-in defaults.
        These are regex patterns that catch obviously harmful requests."""
        path = os.path.join(os.path.dirname(__file__), "..", config.BLOCKLIST_PATH)
        if not os.path.exists(path):
            # If no blocklist file exists, use these hardcoded defaults
            defaults = [
                r"\b(?:make|create|build)\s+(?:a\s+)?(?:bomb|weapon|explosive)",
                r"\b(?:how\s+to\s+)?(?:hack|exploit|breach)\s+",
                r"\b(?:generate|write|create)\s+(?:child|minor)\s+(?:porn|sexual)",
                r"\bsynthesize\s+(?:drugs|meth|fentanyl)",
                r"\b(?:kill|murder|assassinate)\s+(?:someone|a\s+person)",
            ]
            self.blocklist_patterns = [re.compile(p, re.IGNORECASE) for p in defaults]
            return

        with open(path, "r") as f:
            data = json.load(f)
        self.blocklist_patterns = [
            re.compile(p, re.IGNORECASE) for p in data.get("patterns", [])
        ]

    def _load_model(self):
        """Load the pre-trained SVM model and TF-IDF vectorizer from disk.
        These are .pkl files trained by the train_guard.py script."""
        svm_path = os.path.join(os.path.dirname(__file__), "..", config.GUARD_MODEL_PATH)
        vec_path = os.path.join(
            os.path.dirname(__file__), "..", config.GUARD_VECTORIZER_PATH
        )

        if os.path.exists(svm_path) and os.path.exists(vec_path):
            import joblib  # joblib loads saved scikit-learn models
            self.svm = joblib.load(svm_path)
            self.vectorizer = joblib.load(vec_path)

    # ── Tier 1: Blocklist (fast, < 0.1ms) ────────────────────

    def _check_blocklist(self, text: str) -> tuple[bool, float]:
        """Check input against keyword patterns. Instantly catches obvious bad requests.
        Returns (is_safe, confidence_score)."""
        text_lower = text.lower()
        for pattern in self.blocklist_patterns:
            if pattern.search(text_lower):
                return False, 0.99  # 99% confident this is unsafe
        return True, 1.0  # Passed blocklist, no issues found

    # ── Tier 2: SVM Classifier (~2ms) ────────────────────────

    def _check_svm(self, text: str) -> tuple[bool, float]:
        """Run the ML classifier on the input.
        
        How it works:
        1. Convert text → numbers using TF-IDF (measures word importance)
        2. Feed those numbers into the SVM (finds the boundary between safe/unsafe)
        3. Get a probability score (how likely is this input safe vs. unsafe?)
        
        Returns (is_safe, confidence_score)."""
        if self.svm is None or self.vectorizer is None:
            # No model loaded yet — be permissive but flag low confidence
            return True, 0.5

        # Convert text to TF-IDF feature vector (a mathematical representation)
        features = self.vectorizer.transform([text])
        # Get probability estimates from the SVM
        proba = self.svm.predict_proba(features)[0]

        # proba[0] = P(safe), proba[1] = P(unsafe)
        safe_prob = float(proba[0]) if len(proba) > 1 else float(proba[0])
        is_safe = safe_prob >= config.GUARD_CONFIDENCE_THRESHOLD

        return is_safe, safe_prob

    # ── Pipeline Interface ───────────────────────────────────

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Run the guard check. Called by the Pipeline orchestrator."""
        # If the Sanitizer already blocked this, don't bother checking again
        if ctx.guard_blocked:
            return ctx

        text = ctx.sanitized_input

        # Tier 1: Fast keyword check (catches obvious attacks instantly)
        safe, confidence = self._check_blocklist(text)
        if not safe:
            ctx.guard_safe = False
            ctx.guard_confidence = confidence
            ctx.guard_method = "blocklist"
            ctx.guard_blocked = True
            ctx.slm_response = (
                "I cannot process this request. "
                "It has been flagged by our safety system."
            )
            return ctx

        # Tier 2: ML check (catches sneaky/obfuscated attacks)
        safe, confidence = self._check_svm(text)
        ctx.guard_safe = safe
        ctx.guard_confidence = confidence
        ctx.guard_method = "svm"

        if not safe:
            ctx.guard_blocked = True
            ctx.slm_response = (
                "I cannot process this request. "
                "It has been flagged by our safety classifier."
            )

        return ctx
