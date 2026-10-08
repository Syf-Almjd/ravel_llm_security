"""
Unit tests for Stage 6: DoLa (Hallucination Detector).
"""

import pytest

from pipeline import PipelineContext
from pipeline.dola import DoLaDecoder


@pytest.mark.asyncio
async def test_dola_analyze_logprobs():
    decoder = DoLaDecoder()

    # Confident logprobs (near 0)
    high_conf = [-0.1, -0.2, -0.15, -0.05]
    res_high = decoder._analyze_logprobs(high_conf)
    assert res_high["risk_score"] == 0.0
    assert not res_high["flagged"]

    # Low confidence logprobs (less than threshold -2.5)
    low_conf = [-3.0, -3.5, -4.0, -0.1]
    res_low = decoder._analyze_logprobs(low_conf)
    assert res_low["risk_score"] > 0.5
    assert res_low["flagged"] is True


@pytest.mark.asyncio
async def test_dola_estimate_logprobs_from_text():
    decoder = DoLaDecoder()
    hedged_text = "Perhaps maybe it might be approximately 1984"
    logprobs = decoder._estimate_logprobs(hedged_text)
    assert len(logprobs) > 0
    # At least some hedged words should receive low probabilities
    assert any(lp <= -2.0 for lp in logprobs)


@pytest.mark.asyncio
async def test_dola_process():
    decoder = DoLaDecoder()
    ctx = PipelineContext(
        raw_input="Tell me about Python",
        slm_response="Python is a popular programming language.",
    )
    result = await decoder.process(ctx)
    assert hasattr(result, "dola_risk")
    assert isinstance(result.dola_risk, float)
