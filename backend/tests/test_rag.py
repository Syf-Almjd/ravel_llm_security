"""
Unit tests for Stage 4: DRAG (Distilled RAG Retriever).
"""

import pytest

from pipeline import PipelineContext
from pipeline.rag import DRAGRetriever


@pytest.mark.asyncio
async def test_drag_build_context():
    retriever = DRAGRetriever()
    cards = [
        {
            "id": "fc_001",
            "topic": "API Security",
            "facts": ["Always use HTTPS", "Rotate keys every 90 days"],
            "source": "handbook.md",
        }
    ]
    ctx_text = retriever._build_context(cards)
    assert "[Verified Facts]" in ctx_text
    assert "API Security:" in ctx_text
    assert "Always use HTTPS" in ctx_text


@pytest.mark.asyncio
async def test_drag_process_without_facts():
    retriever = DRAGRetriever()
    ctx = PipelineContext(raw_input="Tell me a joke", sanitized_input="Tell me a joke")
    # Even if chroma returns empty, augmented prompt should default to query
    result = await retriever.process(ctx)
    assert "Tell me a joke" in result.augmented_prompt
