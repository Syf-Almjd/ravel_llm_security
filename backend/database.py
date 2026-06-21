"""
Ravel — Database Layer
Uses SQLAlchemy ORM with SQLite (a lightweight file-based database).
Defines all tables and provides session management for the API.
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Text, Boolean, Float, Integer,
    DateTime, ForeignKey, Index, event
)
from sqlalchemy.orm import (
    declarative_base, sessionmaker, scoped_session, relationship
)

# ─── Database Path ───────────────────────────────────────────
# We store the database file in backend/data/ravel.db

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Create the data folder if it doesn't exist

DB_PATH = os.path.join(DATA_DIR, "ravel.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"  # SQLite connection string (points to a local file)

# The engine is SQLAlchemy's connection to the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite + FastAPI (multi-threaded)
    echo=False,  # Set to True to see all SQL queries printed (useful for debugging)
)

# SessionLocal creates database sessions — each API request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)  # Thread-safe version

# Base is the parent class for all database models (tables)
Base = declarative_base()


# ─── Models (Database Tables) ────────────────────────────────
# Each class below maps to a table in the SQLite database.
# SQLAlchemy automatically creates these tables on startup.

class User(Base):
    """Stores user accounts — email, password hash, role, etc."""
    __tablename__ = "users"

    id = Column(String, primary_key=True)          # UUID
    email = Column(String, unique=True, nullable=False, index=True)  # index for fast lookup
    password_hash = Column(String, nullable=False)  # bcrypt hash (never store plain passwords!)
    display_name = Column(String, nullable=False)
    role = Column(String, default="user")           # 'admin' | 'user'
    avatar_initials = Column(String(2))             # e.g. "SA"
    is_active = Column(Boolean, default=True)       # False = suspended/banned
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships — these let us access related records easily
    # cascade="all, delete-orphan" means: if user is deleted, delete their stuff too
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    threat_events = relationship("ThreatEvent", back_populates="user", cascade="all, delete-orphan")
    request_logs = relationship("RequestLog", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Stores active login sessions (JWT tokens). Used to revoke tokens on logout."""
    __tablename__ = "sessions"

    token_jti = Column(String, primary_key=True)    # Unique token ID from JWT
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime)                    # When this token expires
    revoked = Column(Boolean, default=False)         # True = user logged out


class AgentTemplate(Base):
    """Persona 'Skins' — pre-built AI assistant configurations with system prompts."""
    __tablename__ = "agent_templates"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)            # e.g. "Red Team Operator"
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)     # The AI's personality instructions
    category = Column(String)                        # e.g. "Security", "Engineering"
    icon = Column(String)                            # Icon name for the UI
    guardrail_config = Column(Text)                  # JSON — which pipeline stages are on/off
    suggested_prompts = Column(Text)                 # JSON array — starter prompts for this persona
    is_builtin = Column(Boolean, default=False)      # True = shipped with Ravel, not user-created
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    """A chat session between a user and the AI."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(String, nullable=True)      # Which persona was used
    title = Column(String, default="New Session")
    category = Column(String, default="General")
    pinned = Column(Boolean, default=False)           # User can pin important chats
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.created_at")  # Messages ordered by time


class Message(Base):
    """A single message in a conversation (either from user or AI)."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False)           # 'user' | 'assistant'
    text = Column(Text, nullable=False)               # The message content
    metrics = Column(Text)                            # JSON — security scores, latencies, etc.
    token_stats = Column(Text)                        # JSON — token counts for billing/monitoring
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Memory(Base):
    """Long-term memories the AI can recall across conversations.
    Think of these as 'things the AI knows about this user'."""
    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(String, nullable=True)       # If set, memory only applies to this persona
    memory_type = Column(String, nullable=False)      # fact, preference, instruction, correction, episode, context
    content = Column(Text, nullable=False)            # The actual memory text
    source_conversation_id = Column(String, nullable=True)  # Where this memory came from
    source_message_id = Column(String, nullable=True)
    importance = Column(Float, default=0.5)           # 0-1, higher = more important
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime)                  # When was this memory last used
    access_count = Column(Integer, default=0)         # How many times it's been referenced
    is_active = Column(Boolean, default=True)         # False = soft-deleted

    user = relationship("User", back_populates="memories")

    # Indexes make queries faster on these columns
    __table_args__ = (
        Index("idx_memories_user", "user_id"),
        Index("idx_memories_type", "memory_type"),
        Index("idx_memories_template", "template_id"),
    )


class ApiKey(Base):
    """API keys for programmatic access to Ravel."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)             # User-friendly label like "My App Key"
    key_hash = Column(String, nullable=False)         # Hashed version of the key (we don't store raw keys)
    key_prefix = Column(String, nullable=False)       # First 7 chars for display (e.g. "rv_abc**")
    request_count = Column(Integer, default=0)        # How many times this key has been used
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")


class ThreatEvent(Base):
    """Log of every security threat detected by the pipeline.
    Used for the Security dashboard and admin analytics."""
    __tablename__ = "threat_events"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    conversation_id = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)             # The malicious input that was caught
    threat_type = Column(String)                      # injection, jailbreak, pii, toxicity
    severity = Column(String, default="CRITICAL")     # LOW, MEDIUM, HIGH, CRITICAL
    guard_latency_ms = Column(Float)                  # How fast the guard caught it
    blocked = Column(Boolean, default=True)           # Was it blocked?
    metadata_json = Column(Text)                      # Full pipeline metrics as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="threat_events")

    __table_args__ = (
        Index("idx_threats_user", "user_id"),
        Index("idx_threats_time", "created_at"),
    )


class RequestLog(Base):
    """Log of every query that goes through the pipeline.
    Used for analytics and debugging."""
    __tablename__ = "request_log"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    conversation_id = Column(String, nullable=True)
    template_id = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)             # What the user asked
    response = Column(Text)                           # What the AI replied
    metrics = Column(Text)                            # JSON — all pipeline scores
    token_stats = Column(Text)                        # JSON — token usage stats
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="request_logs")

    __table_args__ = (
        Index("idx_requests_user", "user_id"),
        Index("idx_requests_time", "created_at"),
    )


# ─── System Settings (key-value store) ───────────────────────
# A simple key-value table for storing global settings like security policy.

class SystemSetting(Base):
    """General-purpose key-value store for system-wide settings."""
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True)            # e.g. "security_policy"
    value = Column(Text)                              # JSON string with the setting value
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Database Initialization ─────────────────────────────────

def init_db():
    """Create all tables if they don't exist yet. Called once on server startup."""
    Base.metadata.create_all(bind=engine)
    print("  Database initialized at:", DB_PATH)


def get_db():
    """FastAPI dependency that provides a database session per request.
    Usage: `db: DBSession = Depends(get_db)` in route handlers."""
    db = SessionLocal()
    try:
        yield db     # Give the session to the route handler
    finally:
        db.close()   # Always close the session when done (even if error occurs)
