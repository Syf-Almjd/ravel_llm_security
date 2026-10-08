"""
Unit tests for the Agent Memory System.
"""

from memory import (
    export_memories_markdown,
    format_memories_for_prompt,
    import_memories_markdown,
    retrieve_memories,
    save_extracted_memories,
    save_memory,
)


def test_save_and_retrieve_memories(db_session, regular_user):
    user, _ = regular_user
    mem = save_memory(
        db=db_session,
        user_id=user.id,
        memory_type="fact",
        content="User prefers Python over JavaScript",
        importance=0.8,
    )
    assert mem.id is not None
    assert mem.is_active is True

    retrieved = retrieve_memories(db_session, user_id=user.id)
    assert len(retrieved) >= 1
    assert retrieved[0].content == "User prefers Python over JavaScript"


def test_format_memories_for_prompt(db_session, regular_user):
    user, _ = regular_user
    mem1 = save_memory(db=db_session, user_id=user.id, memory_type="preference", content="Concise answers")
    mem2 = save_memory(db=db_session, user_id=user.id, memory_type="instruction", content="Use type hints")

    formatted = format_memories_for_prompt([mem1, mem2])
    assert "[Agent Memory — Things you remember about this user:]" in formatted
    assert "(preference) Concise answers" in formatted
    assert "(instruction) Use type hints" in formatted


def test_save_extracted_memories_deduplication(db_session, regular_user):
    user, _ = regular_user
    extracted = [
        {"type": "fact", "content": "Works on Kubernetes"},
        {"type": "fact", "content": "Works on Kubernetes"},  # Duplicate
        {"type": "preference", "content": "Uses dark mode"},
    ]
    saved = save_extracted_memories(db_session, user_id=user.id, extracted=extracted)
    assert saved == 2


def test_export_and_import_memories_markdown(db_session, regular_user):
    user, _ = regular_user
    save_memory(db=db_session, user_id=user.id, memory_type="fact", content="Developer at startup", importance=0.9)
    save_memory(db=db_session, user_id=user.id, memory_type="preference", content="Fast response time", importance=0.7)

    md = export_memories_markdown(db_session, user_id=user.id, user_email=user.email)
    assert "# Ravel Agent Memory Export" in md
    assert "Developer at startup" in md
    assert "Fast response time" in md

    # Now import into another context/verify count
    imported = import_memories_markdown(db_session, user_id=user.id, md_content=md)
    assert imported >= 2
