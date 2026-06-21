"""
Ravel — Knowledge Base Seeder
Populates ChromaDB with pre-built fact-cards for DRAG.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

import config


# ── Pre-built fact-cards covering AI safety domain ───────────

FACT_CARDS = [
    {
        "id": "fc_001",
        "topic": "Large Language Model Safety",
        "facts": [
            "LLM safety mechanisms include input/output filtering, RLHF, and constitutional AI.",
            "Common attack vectors include prompt injection, jailbreaking, and adversarial prompts.",
            "Safety guardrails can be applied at the input, model, and output levels.",
            "Red teaming involves systematically testing models for harmful outputs.",
        ],
        "source": "Dong et al., 2025 - Safeguarding large language models: A survey",
    },
    {
        "id": "fc_002",
        "topic": "NeMo Guardrails Framework",
        "facts": [
            "NeMo Guardrails is an open-source toolkit by NVIDIA for adding programmable safety rails to LLM applications.",
            "It uses Colang, a formal modeling language, to define programmatic safety rules.",
            "The toolkit can act as a proxy around any LLM to intercept and filter inputs/outputs.",
            "NeMo includes pre-built rails for fact-checking, hallucination mitigation, and content moderation.",
        ],
        "source": "Rebedea et al., 2023 - NeMo Guardrails toolkit",
    },
    {
        "id": "fc_003",
        "topic": "Red Teaming Language Models",
        "facts": [
            "Red teaming involves human testers attempting to elicit harmful outputs from language models.",
            "Ganguli et al. released a dataset of 38,961 red team attacks for community analysis.",
            "Harmful outputs range from offensive language to subtly harmful non-violent unethical content.",
            "Larger models tend to be more susceptible to sophisticated attacks but also easier to make safe.",
        ],
        "source": "Ganguli et al., 2022 - Red teaming language models",
    },
    {
        "id": "fc_004",
        "topic": "Llama Guard",
        "facts": [
            "Llama Guard is an LLM-based input-output safeguard for human-AI conversations.",
            "It functions as a lightweight classifier for prompt and response safety classification.",
            "Based on LLaMA architecture, fine-tuned specifically for content safety tasks.",
            "Demonstrates strong performance on the OpenAI Moderation Evaluation dataset and ToxicChat.",
        ],
        "source": "Inan et al., 2023 - Llama Guard",
    },
    {
        "id": "fc_005",
        "topic": "Hallucination Mitigation Techniques",
        "facts": [
            "Over 32 techniques have been developed to mitigate hallucination in LLMs.",
            "Methods are categorized by dataset utilization, feedback mechanisms, and retriever types.",
            "Retrieval Augmented Generation (RAG) is one of the most effective anti-hallucination approaches.",
            "Knowledge retrieval systems ground LLM outputs in verified factual sources.",
        ],
        "source": "Tonmoy et al., 2024 - Comprehensive survey of hallucination mitigation",
    },
    {
        "id": "fc_006",
        "topic": "Hallucination Types and Detection",
        "facts": [
            "LLM hallucinations include factual errors, entity confusion, and fabricated citations.",
            "Intrinsic hallucinations contradict the source material; extrinsic ones add unverifiable information.",
            "RAG systems have limitations including retrieval quality, context window constraints, and conflicting sources.",
            "Benchmarks like TruthfulQA and HaluEval are used to quantify hallucination rates.",
        ],
        "source": "Huang et al., 2025 - Survey on hallucination in LLMs",
    },
    {
        "id": "fc_007",
        "topic": "Guardrail Frameworks Comparison",
        "facts": [
            "Major open-source guardrail frameworks include Llama Guard, NVIDIA NeMo, and Guardrails AI.",
            "Guardrails function by filtering inputs or outputs of LLMs to prevent harmful content.",
            "Systematic design methodology is needed for robust safety solutions.",
            "Testing and verification are essential to ensure guardrail quality.",
        ],
        "source": "Dong et al., 2024 / Yi et al., 2024 - Building guardrails for LLMs",
    },
    {
        "id": "fc_008",
        "topic": "Healthcare AI Safety",
        "facts": [
            "Healthcare AI faces unique risks from hallucinations including misdiagnosis and harmful medical advice.",
            "Integrating guardrails like NeMo and Llama Guard addresses healthcare-specific safety requirements.",
            "Retrieval rails accessing trusted medical databases ensure factual grounding in clinical settings.",
            "Regulatory compliance (HIPAA, FDA) adds additional safety requirements for healthcare AI.",
        ],
        "source": "Gangavarapu, 2024 - Enhancing guardrails for healthcare AI",
    },
    {
        "id": "fc_009",
        "topic": "Multi-layer Guardrail Taxonomy",
        "facts": [
            "Guardrails can be categorized into pre-processing, in-processing, and post-processing layers.",
            "Real-time content filtering balances safety with latency requirements.",
            "Privacy-preserving techniques protect user data while maintaining safety.",
            "Domain-specific guardrail solutions outperform generic ones in specialized applications.",
        ],
        "source": "Akheel, 2025 - Guardrails for LLMs: review of techniques",
    },
    {
        "id": "fc_010",
        "topic": "Small Language Models (SLMs)",
        "facts": [
            "SLMs typically have 1-3 billion parameters compared to 70B+ for large LLMs.",
            "SLMs offer 5-20x faster inference than large models on equivalent hardware.",
            "Popular SLMs include Gemma-2B, Phi-3 Mini, Llama-3.2 1B/3B, and TinyLlama.",
            "SLMs are ideal for edge deployment, mobile devices, and latency-sensitive applications.",
            "The main challenge is maintaining safety without negating their speed advantage.",
        ],
        "source": "General SLM research, 2024",
    },
    {
        "id": "fc_011",
        "topic": "Retrieval-Augmented Generation (RAG)",
        "facts": [
            "RAG combines retrieval of relevant documents with LLM generation for grounded responses.",
            "Key components include a retriever, vector database, embedding model, and generator.",
            "ChromaDB and FAISS are popular lightweight vector databases for RAG implementations.",
            "Effective RAG requires high-quality chunking, embedding, and relevance scoring.",
            "RAG significantly reduces hallucination rates compared to pure generation.",
        ],
        "source": "General RAG literature",
    },
    {
        "id": "fc_012",
        "topic": "DoLa Decoding",
        "facts": [
            "DoLa contrasts logits from early and late transformer layers during text generation.",
            "Early layers capture syntax and common patterns; late layers encode factual knowledge.",
            "When early and late layers disagree, the generated token is likely a hallucination.",
            "DoLa penalizes diverging tokens to steer generation toward factually grounded outputs.",
            "This technique requires no additional training and works with any transformer-based model.",
        ],
        "source": "Li et al., 2023 - DoLa: Decoding by Contrasting Layers",
    },
]


def seed():
    """Populate ChromaDB with fact-cards."""
    import chromadb

    persist_dir = os.path.join(BACKEND_DIR, config.CHROMA_PERSIST_DIR)
    os.makedirs(persist_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=persist_dir)

    # Delete existing collection if present
    try:
        client.delete_collection(config.CHROMA_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    print("=" * 50)
    print("  Seeding ChromaDB with Fact-Cards")
    print("=" * 50)

    ids = []
    documents = []
    metadatas = []

    for card in FACT_CARDS:
        ids.append(card["id"])
        documents.append(json.dumps(card))
        metadatas.append({
            "topic": card["topic"],
            "source": card["source"],
            "fact_count": len(card["facts"]),
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"\n  Inserted {collection.count()} fact-cards into '{config.CHROMA_COLLECTION}'")
    print(f"  Persist directory: {persist_dir}")
    print("\n  Topics seeded:")
    for card in FACT_CARDS:
        print(f"    • {card['topic']} ({len(card['facts'])} facts)")
    print("\n✓ Seeding complete!")


if __name__ == "__main__":
    seed()
