"""
Ravel — Agent Memory System
Persistent memory that makes agents learn and remember across conversations.

This is what makes Ravel "personal" — the AI remembers things about you:
  - Facts: "I work at Google, using Python and Kubernetes"
  - Preferences: "I prefer concise answers with code examples"
  - Instructions: "Always use type hints in Python code"
  - Corrections: "Don't use print() for logging, use the logging module"
  - Context: "My project is called Ravel, it's an LLM security guard"

Memory lifecycle:
  1. EXTRACT: After each conversation, the AI analyzes what's worth remembering
  2. SAVE: Memories are stored in the database with type, importance, and source
  3. RETRIEVE: Before each new conversation, relevant memories are loaded
  4. FORMAT: Memories are injected into the system prompt so the AI "remembers"
  5. EXPORT/IMPORT: Users can backup and transfer their memories as Markdown
"""

import uuid
import json
import re
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from database import Memory


# ─── Memory Extraction ───────────────────────────────────────
# After each conversation turn, we ask the AI: "What should we remember?"

EXTRACTION_PROMPT = """You are a memory extraction system. Analyze this conversation exchange and extract any facts, preferences, or instructions worth remembering about the user for future conversations.

User said: {user_message}
Assistant said: {assistant_message}

Extract memories as a JSON array. Each memory should have:
- "type": one of "fact", "preference", "instruction", "correction", "context"
- "content": a concise statement about the user (max 100 chars)

Rules:
- Only extract genuinely useful information about the USER (not general knowledge)
- facts = things about the user (their job, company, tech stack, etc.)
- preferences = how they like responses (concise, detailed, with examples, etc.)
- instructions = things they told you to always/never do
- corrections = things the user corrected about your response
- context = project names, team details, environment info
- If nothing worth remembering, return: []

Return ONLY the JSON array, no other text."""


async def extract_memories(
    user_msg: str,
    assistant_msg: str,
    ollama_endpoint: str,
    model: str,
) -> list[dict]:
    """Use the AI model to analyze a conversation and extract things worth remembering.

    How it works:
    1. Send the conversation to the AI with the extraction prompt
    2. The AI returns a JSON array of memories
    3. We parse and validate the response

    Returns list of {"type": str, "content": str} dicts.
    """
    prompt = EXTRACTION_PROMPT.format(
        user_message=user_msg[:500],       # Truncate to keep prompt small
        assistant_message=assistant_msg[:500],
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{ollama_endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 512},  # Low temp = consistent extraction
                },
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            raw_text = data.get("response", "").strip()

            # Parse JSON from the AI's response (it might wrap it in markdown code blocks)
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if not json_match:
                return []

            memories = json.loads(json_match.group())
            if not isinstance(memories, list):
                return []

            # Validate: only keep properly structured memories with valid types
            valid = []
            for m in memories:
                if isinstance(m, dict) and "type" in m and "content" in m:
                    if m["type"] in ("fact", "preference", "instruction", "correction", "context"):
                        valid.append({
                            "type": m["type"],
                            "content": str(m["content"])[:200],  # Cap at 200 chars
                        })
            return valid

    except Exception as e:
        print(f"  Memory extraction failed: {e}")
        return []


# ─── Memory Retrieval ────────────────────────────────────────

def retrieve_memories(
    db: DBSession,
    user_id: str,
    template_id: Optional[str] = None,
    limit: int = 10,
) -> list[Memory]:
    """Load the most relevant memories for this user and persona.

    Memories can be:
    - Global (available for all personas)
    - Scoped (only for a specific persona/template)

    Returns memories sorted by importance and recency.
    Also tracks access count and last access time (for analytics)."""
    query = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.is_active == True,  # Only active (not deleted) memories
    )

    # Get global memories + template-scoped memories
    if template_id:
        query = query.filter(
            (Memory.template_id == template_id) | (Memory.template_id == None)
        )
    else:
        query = query.filter(Memory.template_id == None)

    # Sort by importance (most important first) then by recency
    memories = query.order_by(
        desc(Memory.importance),
        desc(Memory.created_at),
    ).limit(limit).all()

    # Update access tracking (for analytics and memory decay)
    for m in memories:
        m.last_accessed = datetime.utcnow()
        m.access_count = (m.access_count or 0) + 1
    db.commit()

    return memories


def format_memories_for_prompt(memories: list[Memory]) -> str:
    """Convert memories into a text block that gets injected into the AI's system prompt.

    Example output:
    [Agent Memory — Things you remember about this user:]
    - (fact) Works at Google, using Python and Kubernetes
    - (preference) Prefers concise answers with code examples
    [End of memory. Use this context naturally in your responses.]"""
    if not memories:
        return ""

    lines = ["\n[Agent Memory — Things you remember about this user:]"]
    for m in memories:
        lines.append(f"- ({m.memory_type}) {m.content}")
    lines.append("[End of memory. Use this context naturally in your responses. Do not explicitly mention reading from memory.]\n")
    return "\n".join(lines)


# ─── Memory CRUD (Create, Read, Update, Delete) ──────────────

def save_memory(
    db: DBSession,
    user_id: str,
    memory_type: str,
    content: str,
    template_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    message_id: Optional[str] = None,
    importance: float = 0.5,
) -> Memory:
    """Create a new memory record in the database."""
    memory = Memory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        template_id=template_id,
        memory_type=memory_type,
        content=content,
        source_conversation_id=conversation_id,
        source_message_id=message_id,
        importance=importance,
        created_at=datetime.utcnow(),
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def save_extracted_memories(
    db: DBSession,
    user_id: str,
    extracted: list[dict],
    template_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
):
    """Save a batch of extracted memories, skipping duplicates.

    Compares against existing memories (case-insensitive) to avoid
    storing the same fact twice."""
    existing = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.is_active == True,
    ).all()
    existing_contents = {m.content.lower().strip() for m in existing}

    saved_count = 0
    for mem_dict in extracted:
        content = mem_dict["content"].strip()
        if content.lower() in existing_contents:
            continue  # Skip duplicate — we already know this

        save_memory(
            db=db,
            user_id=user_id,
            memory_type=mem_dict["type"],
            content=content,
            template_id=template_id,
            conversation_id=conversation_id,
        )
        saved_count += 1

    return saved_count


# ─── Markdown Export/Import ──────────────────────────────────
# Users can export their memories as a Markdown file for backup,
# or import memories from a file (useful for migrating between instances).

def export_memories_markdown(db: DBSession, user_id: str, user_email: str = "") -> str:
    """Export all active memories as a formatted Markdown file.

    Groups memories by type (Facts, Preferences, Instructions, etc.)
    and includes importance scores."""
    memories = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.is_active == True,
    ).order_by(Memory.memory_type, desc(Memory.importance)).all()

    lines = [
        "# Ravel Agent Memory Export",
        f"## User: {user_email}",
        f"## Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"## Total Memories: {len(memories)}",
        "",
    ]

    # Group by type for organized output
    type_groups = {}
    for m in memories:
        if m.memory_type not in type_groups:
            type_groups[m.memory_type] = []
        type_groups[m.memory_type].append(m)

    type_labels = {
        "fact": "Facts",
        "preference": "Preferences",
        "instruction": "Instructions",
        "correction": "Corrections",
        "episode": "Episodes",
        "context": "Context",
    }

    for mem_type, label in type_labels.items():
        if mem_type in type_groups:
            lines.append(f"### {label}")
            for m in type_groups[mem_type]:
                importance_str = f" [importance: {m.importance:.1f}]" if m.importance != 0.5 else ""
                lines.append(f"- {m.content}{importance_str}")
            lines.append("")

    lines.append("---")
    lines.append("*Exported from Ravel — Secure Skin for AI Agents*")

    return "\n".join(lines)


def import_memories_markdown(
    db: DBSession,
    user_id: str,
    md_content: str,
) -> int:
    """Import memories from a Markdown file (previously exported).

    Parses the ### section headers to determine memory type,
    then imports each - bullet point as a memory.
    Returns the count of successfully imported memories."""
    imported = 0
    current_type = None

    # Map section headers to memory types
    type_map = {
        "facts": "fact",
        "preferences": "preference",
        "instructions": "instruction",
        "corrections": "correction",
        "episodes": "episode",
        "context": "context",
    }

    for line in md_content.split("\n"):
        line = line.strip()

        # Detect section headers (### Facts, ### Preferences, etc.)
        if line.startswith("### "):
            header = line[4:].strip().lower()
            current_type = type_map.get(header)
            continue

        # Parse bullet points as memories
        if current_type and line.startswith("- "):
            content = line[2:].strip()
            # Extract importance annotation if present
            importance = 0.5
            imp_match = re.search(r'\[importance:\s*([\d.]+)\]', content)
            if imp_match:
                importance = float(imp_match.group(1))
                content = re.sub(r'\s*\[importance:\s*[\d.]+\]', '', content).strip()

            if content:
                save_memory(db, user_id, current_type, content, importance=importance)
                imported += 1

    return imported
