"""
Unit tests for Stage 7: RIS (Reasoning Integrity Score).
"""

import pytest

from pipeline import PipelineContext
from pipeline.ris import RISScorer


@pytest.mark.asyncio
async def test_ris_blocks_when_guard_blocked():
    scorer = RISScorer()
    ctx = PipelineContext(
        raw_input="hack",
        guard_blocked=True,
        guard_safe=False,
    )
    result = await scorer.process(ctx)
    assert result.ris_score == 0.0
    assert result.ris_verdict == "BLOCK"
    assert result.ris_breakdown["safety"] == 0.0


@pytest.mark.asyncio
async def test_ris_passes_high_quality_response():
    scorer = RISScorer()
    ctx = PipelineContext(
        raw_input="What is HTTPS?",
        sanitized_input="What is HTTPS?",
        guard_safe=True,
        guard_confidence=0.99,
        dola_risk=0.05,
        slm_response="HTTPS is Hypertext Transfer Protocol Secure, an extension of HTTP using TLS encryption to secure communication over computer networks.",
    )
    result = await scorer.process(ctx)
    assert result.ris_score >= 70.0
    assert result.ris_verdict in ("PASS", "WARN")
    assert "safety" in result.ris_breakdown
    assert "grounding" in result.ris_breakdown
    assert "coherence" in result.ris_breakdown
    assert "consistency" in result.ris_breakdown


@pytest.mark.asyncio
async def test_ris_verdicts_thresholds():
    scorer = RISScorer()

    # Empty response leads to low consistency and triggers BLOCK
    ctx_bad = PipelineContext(
        raw_input="test",
        guard_safe=False,
        guard_confidence=0.1,
        dola_risk=0.9,
        slm_response="",
    )
    res_bad = await scorer.process(ctx_bad)
    assert res_bad.ris_verdict == "BLOCK"
