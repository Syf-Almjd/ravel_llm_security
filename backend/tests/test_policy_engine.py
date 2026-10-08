"""
Unit tests for Dynamic Policy Engine.
"""

import config
import policy_engine


def test_apply_policy_to_runtime():
    test_policy = {
        "guard_slm": {
            "threat_threshold": 0.65,
        },
        "ease_routing": {
            "trigger_complexity_threshold": 0.85,
        },
        "drag_rag": {
            "similarity_k": 5,
            "confidence_cutoff": 0.75,
        },
        "dola_decoding": {
            "hallucination_penalty": 0.40,
        },
    }

    policy_engine.apply_policy_to_runtime(test_policy)

    assert config.GUARD_CONFIDENCE_THRESHOLD == 0.65
    assert config.EASE_COT_THRESHOLD == 0.85
    assert config.RAG_TOP_K == 5
    assert config.RAG_MIN_RELEVANCE == 0.75
    assert config.DOLA_HALLUCINATION_RATIO == 0.40

    # Reset back to defaults
    config.GUARD_CONFIDENCE_THRESHOLD = 0.50
    config.EASE_COT_THRESHOLD = 0.70
    config.RAG_TOP_K = 3
    config.RAG_MIN_RELEVANCE = 0.65
    config.DOLA_HALLUCINATION_RATIO = 0.30
