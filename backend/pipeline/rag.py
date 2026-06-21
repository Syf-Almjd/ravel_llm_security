# ═══════════════════════════════════════════════════════════════
# rag.py — The Fact Fetcher
# ═══════════════════════════════════════════════════════════════
# When a user asks a question about company data, this file
# instantly runs over to your secure internal database (ChromaDB)
# and pulls out exactly the right factual information ("fact
# cards"). It hands these facts to the AI so the AI doesn't have
# to guess the answer.
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 4: DRAG (Distilled Retrieval-Augmented Generation)
Fetches relevant knowledge from ChromaDB to give the AI model context. Runs in < 15ms.

Why "Distilled" RAG?
Instead of dumping raw documents into the prompt (which wastes tokens),
DRAG uses pre-compressed "fact cards" — short, curated knowledge entries.
This keeps the prompt small and focused, which is especially important
for small language models (SLMs) that have limited context windows.
"""

import os
import json
from pipeline import PipelineContext
import config

# ChromaDB connection is lazy-loaded (only connects when first needed)
# This avoids slowing down startup if RAG isn't being used
_chroma_client = None
_collection = None


def _get_collection():
    """Connect to ChromaDB on first use (lazy initialization).
    ChromaDB is a vector database — it stores text as mathematical vectors
    so we can search by meaning, not just keywords."""
    global _chroma_client, _collection
    if _collection is not None:
        return _collection

    try:
        import chromadb

        persist_dir = os.path.join(
            os.path.dirname(__file__), "..", config.CHROMA_PERSIST_DIR
        )
        _chroma_client = chromadb.PersistentClient(path=persist_dir)

        # Get or create the collection (like a table in a database)
        # cosine similarity measures how "close" two meanings are (1 = identical)
        _collection = _chroma_client.get_or_create_collection(
            name=config.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity for matching
        )
        return _collection
    except Exception:
        return None  # ChromaDB not available — RAG will be skipped


class DRAGRetriever:
    """Stage 4: Retrieves relevant fact-cards and injects them into the prompt.

    Fact-cards are structured knowledge entries like:
    {
        "id": "fc_001",
        "topic": "Password Security",
        "facts": ["Use bcrypt for hashing", "Minimum 8 characters recommended"],
        "source": "security_handbook.pdf",
        "confidence": 0.95
    }
    """

    def _retrieve(self, query: str, top_k: int = None) -> list[dict]:
        """Search ChromaDB for fact-cards that match the user's query.
        Returns only cards that are relevant enough (above the minimum similarity threshold)."""
        collection = _get_collection()
        if collection is None or collection.count() == 0:
            return []  # No knowledge base available

        k = top_k or config.RAG_TOP_K  # How many cards to fetch (default: 3)

        # Ask ChromaDB: "Find the k most similar documents to this query"
        results = collection.query(
            query_texts=[query],
            n_results=min(k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        cards = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results["distances"] else 1.0
                similarity = 1.0 - distance  # Convert cosine distance → similarity (0-1)

                # Skip cards that aren't relevant enough
                if similarity < config.RAG_MIN_RELEVANCE:  # Default: 0.65 (65% similar)
                    continue

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                try:
                    card = json.loads(doc)  # Parse the stored JSON fact-card
                except (json.JSONDecodeError, TypeError):
                    # If it's not JSON, wrap the raw text as a simple card
                    card = {
                        "topic": metadata.get("topic", "unknown"),
                        "facts": [doc],
                        "source": metadata.get("source", "unknown"),
                    }

                card["relevance"] = round(similarity, 3)
                cards.append(card)

        return cards

    def _build_context(self, cards: list[dict]) -> str:
        """Format fact-cards into a compact text block to inject into the AI's prompt.
        This is kept short to save tokens — the key advantage of DRAG over raw RAG."""
        if not cards:
            return ""

        lines = ["[Verified Facts]"]
        for card in cards:
            facts = card.get("facts", [])
            topic = card.get("topic", "")
            if topic:
                lines.append(f"• {topic}:")
            for fact in facts:
                lines.append(f"  - {fact}")

        return "\n".join(lines)

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Retrieve fact-cards and build the augmented prompt. Called by the Pipeline."""
        query = ctx.sanitized_input

        # Search for relevant knowledge
        cards = self._retrieve(query)
        ctx.fact_cards = cards

        # Build the augmented prompt (original question + retrieved facts)
        context_block = self._build_context(cards)

        if context_block:
            # Inject the facts before the user's question
            ctx.augmented_prompt = (
                f"{context_block}\n\n"
                f"[Query]\n{query}\n\n"
                f"Answer using only the verified facts above when relevant. "
                f"If the facts don't cover the question, answer from your knowledge "
                f"but note that it is not from verified sources."
            )
        else:
            # No relevant facts found — just use the original question
            ctx.augmented_prompt = query

        return ctx
