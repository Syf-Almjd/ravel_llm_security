"""
Ravel — Admin Routes
System-wide visibility and management endpoints.
All routes require admin role.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, desc

from database import (
    get_db, User, Conversation, Message, Memory,
    ApiKey, ThreatEvent, RequestLog, SystemSetting,
)
from middleware import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ─── System Stats ────────────────────────────────────────────

@router.get("/stats")
async def get_admin_stats(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """System-wide metrics overview."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
    total_messages = db.query(func.count(Message.id)).scalar() or 0
    total_threats = db.query(func.count(ThreatEvent.id)).scalar() or 0
    total_requests = db.query(func.count(RequestLog.id)).scalar() or 0
    total_memories = db.query(func.count(Memory.id)).filter(Memory.is_active == True).scalar() or 0
    total_api_keys = db.query(func.count(ApiKey.id)).filter(ApiKey.is_active == True).scalar() or 0

    # Template usage — count conversations per template_id
    template_usage = db.query(
        Conversation.template_id,
        func.count(Conversation.id).label("count"),
    ).filter(Conversation.template_id != None).group_by(
        Conversation.template_id
    ).order_by(desc("count")).limit(10).all()

    # Recent registrations (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_this_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar() or 0

    # Threats this week
    threats_this_week = db.query(func.count(ThreatEvent.id)).filter(
        ThreatEvent.created_at >= week_ago
    ).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_this_week": new_users_this_week,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_threats": total_threats,
        "threats_this_week": threats_this_week,
        "total_requests": total_requests,
        "total_memories": total_memories,
        "total_api_keys": total_api_keys,
        "template_usage": [
            {"template_id": t[0], "count": t[1]}
            for t in template_usage
        ],
    }


# ─── User Management ────────────────────────────────────────

@router.get("/users")
async def list_users(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """List all users with activity counts."""
    users = db.query(User).order_by(desc(User.created_at)).all()
    result = []
    for u in users:
        conv_count = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == u.id
        ).scalar() or 0
        threat_count = db.query(func.count(ThreatEvent.id)).filter(
            ThreatEvent.user_id == u.id
        ).scalar() or 0
        memory_count = db.query(func.count(Memory.id)).filter(
            Memory.user_id == u.id, Memory.is_active == True
        ).scalar() or 0

        result.append({
            "id": u.id,
            "email": u.email,
            "display_name": u.display_name,
            "role": u.role,
            "avatar_initials": u.avatar_initials,
            "is_active": u.is_active,
            "conversations": conv_count,
            "threats": threat_count,
            "memories": memory_count,
            "created_at": u.created_at.isoformat() if u.created_at else "",
            "last_login": u.last_login.isoformat() if u.last_login else None,
        })

    return result


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    role: str,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """Change a user's role (admin/user)."""
    if role not in ("admin", "user"):
        raise HTTPException(400, "Role must be 'admin' or 'user'")

    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "User not found")

    if target.id == admin.id:
        raise HTTPException(400, "Cannot change your own role")

    target.role = role
    db.commit()
    return {"message": f"User role updated to {role}"}


@router.put("/users/{user_id}/ban")
async def toggle_ban_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """Ban or unban a user."""
    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "User not found")

    if target.id == admin.id:
        raise HTTPException(400, "Cannot ban yourself")

    target.is_active = not target.is_active
    db.commit()

    status = "unbanned" if target.is_active else "banned"
    return {"message": f"User {status}", "is_active": target.is_active}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """Permanently delete a user and all their data (cascade)."""
    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "User not found")

    if target.id == admin.id:
        raise HTTPException(400, "Cannot delete yourself")

    db.delete(target)
    db.commit()
    return {"message": "User and all associated data deleted"}


# ─── All Conversations ──────────────────────────────────────

@router.get("/conversations")
async def list_all_conversations(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """List all conversations across all users."""
    conversations = db.query(Conversation).order_by(
        desc(Conversation.updated_at)
    ).limit(200).all()

    result = []
    for c in conversations:
        owner = db.query(User).filter_by(id=c.user_id).first()
        msg_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == c.id
        ).scalar() or 0

        result.append({
            "id": c.id,
            "user_email": owner.email if owner else "unknown",
            "user_name": owner.display_name if owner else "unknown",
            "title": c.title,
            "template_id": c.template_id,
            "category": c.category,
            "message_count": msg_count,
            "pinned": c.pinned,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "updated_at": c.updated_at.isoformat() if c.updated_at else "",
        })

    return result


@router.get("/conversations/{conv_id}")
async def view_conversation(
    conv_id: str,
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """View a specific conversation with all messages (read-only)."""
    conv = db.query(Conversation).filter_by(id=conv_id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")

    import json as json_mod
    messages = db.query(Message).filter_by(
        conversation_id=conv_id
    ).order_by(Message.created_at).all()

    owner = db.query(User).filter_by(id=conv.user_id).first()

    return {
        "id": conv.id,
        "user_email": owner.email if owner else "unknown",
        "title": conv.title,
        "template_id": conv.template_id,
        "category": conv.category,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "text": m.text,
                "metrics": json_mod.loads(m.metrics) if m.metrics else None,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in messages
        ],
    }


# ─── All Threats ─────────────────────────────────────────────

@router.get("/threats")
async def list_all_threats(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """List all threat events across all users."""
    threats = db.query(ThreatEvent).order_by(
        desc(ThreatEvent.created_at)
    ).limit(500).all()

    result = []
    for t in threats:
        owner = db.query(User).filter_by(id=t.user_id).first()
        result.append({
            "id": t.id,
            "user_email": owner.email if owner else "unknown",
            "prompt": t.prompt,
            "threat_type": t.threat_type,
            "severity": t.severity,
            "guard_latency_ms": t.guard_latency_ms,
            "blocked": t.blocked,
            "created_at": t.created_at.isoformat() if t.created_at else "",
        })

    return result


# ─── All Requests ────────────────────────────────────────────

@router.get("/requests")
async def list_all_requests(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """List all request logs across all users."""
    requests = db.query(RequestLog).order_by(
        desc(RequestLog.created_at)
    ).limit(500).all()

    import json as json_mod
    result = []
    for r in requests:
        owner = db.query(User).filter_by(id=r.user_id).first()
        result.append({
            "id": r.id,
            "user_email": owner.email if owner else "unknown",
            "prompt": r.prompt,
            "response": r.response[:200] if r.response else "",
            "template_id": r.template_id,
            "metrics": json_mod.loads(r.metrics) if r.metrics else None,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })

    return result


# ─── System Settings ─────────────────────────────────────────

DEFAULT_SETTINGS = {
    "default_ollama_endpoint": "http://localhost:11434",
    "default_model": "gemma3:1b",
    "registration_enabled": "true",
    "max_conversations_per_user": "100",
    "max_memories_per_user": "500",
    "memory_extraction_enabled": "true",
}


@router.get("/settings")
async def get_system_settings(
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """Get all system settings."""
    settings = {}
    for key, default_val in DEFAULT_SETTINGS.items():
        row = db.query(SystemSetting).filter_by(key=key).first()
        settings[key] = row.value if row else default_val
    return settings


@router.put("/settings")
async def update_system_settings(
    body: dict,
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    """Update system settings."""
    for key, value in body.items():
        if key not in DEFAULT_SETTINGS:
            continue  # Ignore unknown keys

        row = db.query(SystemSetting).filter_by(key=key).first()
        if row:
            row.value = str(value)
            row.updated_at = datetime.utcnow()
        else:
            row = SystemSetting(key=key, value=str(value), updated_at=datetime.utcnow())
            db.add(row)

    db.commit()
    return {"message": "Settings updated"}
