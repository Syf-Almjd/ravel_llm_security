"""
Unit tests for Stage 3: EASE (Adaptive Complexity Router).
"""

import pytest
from pipeline import PipelineContext
from pipeline.ease import EASERouter


@pytest.mark.asyncio
async def test_ease_routes_simple_questions_to_direct():
    router = EASERouter()
    simple_queries = [
        "What is the capital of France?",
        "Define polymorphism.",
        "List 3 primary colors.",
        "Who is Alan Turing?",
    ]

    for q in simple_queries:
        ctx = PipelineContext(raw_input=q, sanitized_input=q)
        result = await router.process(ctx)
        assert result.ease_route == "DIRECT"
        assert result.ease_score < 0.35


@pytest.mark.asyncio
async def test_ease_routes_complex_questions_to_cot():
    router = EASERouter()
    complex_queries = [
        "Explain step by step why inflation occurs and how interest rates mitigate it, comparing monetary and fiscal mechanisms.",
        "Compare and contrast microservices versus monolithic architecture, analyzing scalability, fault isolation, and deployment complexity.",
    ]

    for q in complex_queries:
        ctx = PipelineContext(raw_input=q, sanitized_input=q)
        result = await router.process(ctx)
        assert result.ease_route in ("COT", "BORDERLINE")
        assert result.ease_score >= 0.30
