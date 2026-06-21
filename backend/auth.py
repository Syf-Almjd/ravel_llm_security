"""
Ravel — Authentication Routes
Handles user registration, login, logout, and profile updates.
All routes are prefixed with /api/auth.
"""

import uuid   # For generating unique user IDs
import re     # For email validation regex
from datetime import datetime

import bcrypt  # For secure password hashing (industry standard)
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DBSession

from database import get_db, User, Session as SessionModel
from middleware import create_jwt, check_rate_limit, require_auth

# This groups all auth routes under /api/auth/*
router = APIRouter(prefix="/api/auth", tags=["auth"])


# ─── Request/Response Models ─────────────────────────────────
# These define what data the API expects and returns.
# Pydantic automatically validates the data types.

class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateProfileRequest(BaseModel):
    display_name: str = None
    avatar_initials: str = None
    current_password: str = None      # Required if changing password
    new_password: str = None


class UserResponse(BaseModel):
    """What we send back when someone asks about a user."""
    id: str
    email: str
    display_name: str
    role: str                          # "admin" or "user"
    avatar_initials: str | None       # e.g. "SA" for "Saif Almajd"
    is_active: bool                    # False = banned/suspended
    created_at: str
    last_login: str | None


class AuthResponse(BaseModel):
    """What we send back after login/register — the user info + their auth token."""
    user: UserResponse
    token: str                         # JWT token for future API calls


# ─── Helpers ─────────────────────────────────────────────────
# Internal utility functions used by the route handlers below.

def _hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 rounds of salting.
    This is one-way — you can't reverse it to get the original password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Check if a plain password matches the stored hash. Returns True if correct."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _validate_email(email: str) -> bool:
    """Basic email format check using regex. Returns True if it looks like an email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_password(password: str) -> tuple[bool, str]:
    """Check if a password meets minimum requirements. Returns (is_valid, error_message)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""


def _user_to_response(user: User) -> UserResponse:
    """Convert a database User object into a safe API response (removes password hash, etc.)."""
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        avatar_initials=user.avatar_initials,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login=user.last_login.isoformat() if user.last_login else None,
    )


# ─── Routes ──────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse)
async def register(body: RegisterRequest, request: Request, db: DBSession = Depends(get_db)):
    """Create a new account. The very first user automatically becomes admin."""
    # Prevent spam — limit how many registrations per IP
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    # Make sure the email looks valid
    if not _validate_email(body.email):
        raise HTTPException(400, "Invalid email address")

    # Make sure the password is strong enough
    valid, msg = _validate_password(body.password)
    if not valid:
        raise HTTPException(400, msg)

    # Display name can't be empty
    if not body.display_name or len(body.display_name.strip()) < 1:
        raise HTTPException(400, "Display name is required")

    # Check if someone already registered with this email
    existing = db.query(User).filter_by(email=body.email.lower().strip()).first()
    if existing:
        raise HTTPException(409, "An account with this email already exists")

    # Special rule: the very first user to register becomes admin automatically
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"

    # Build the user object
    display_name = body.display_name.strip()
    # Generate avatar initials from first letters of first/last name (e.g. "Saif Al" → "SA")
    initials = "".join([n[0].upper() for n in display_name.split()[:2]]) if display_name else "U"

    user = User(
        id=str(uuid.uuid4()),              # Random unique ID
        email=body.email.lower().strip(),
        password_hash=_hash_password(body.password),  # Never store plain passwords!
        display_name=display_name,
        role=role,
        avatar_initials=initials[:2],
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # Reload to get the auto-generated fields

    # Create a JWT token so the user stays logged in
    token, jti, exp = create_jwt(user.id, user.role)

    # Save the session to database so we can revoke it later if needed
    session = SessionModel(token_jti=jti, user_id=user.id, expires_at=exp)
    db.add(session)
    db.commit()

    return AuthResponse(
        user=_user_to_response(user),
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, request: Request, db: DBSession = Depends(get_db)):
    """Authenticate with email and password. Returns a JWT token on success."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)  # Prevent brute force attacks

    # Look up the user by email
    user = db.query(User).filter_by(email=body.email.lower().strip()).first()
    if not user:
        raise HTTPException(401, "Invalid email or password")  # Vague message to avoid leaking info

    # Check if the password matches the stored hash
    if not _verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    # Check if the account was suspended by an admin
    if not user.is_active:
        raise HTTPException(403, "Account has been suspended")

    # Update the last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate a fresh JWT token for this session
    token, jti, exp = create_jwt(user.id, user.role)

    # Save the session so we can track/revoke it
    session = SessionModel(token_jti=jti, user_id=user.id, expires_at=exp)
    db.add(session)
    db.commit()

    return AuthResponse(
        user=_user_to_response(user),
        token=token,
    )


@router.post("/logout")
async def logout(request: Request, user: User = Depends(require_auth), db: DBSession = Depends(get_db)):
    """Log out by revoking the JWT token so it can't be used again."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        from middleware import decode_jwt
        try:
            payload = decode_jwt(auth_header[7:])  # Decode the JWT (skip "Bearer ")
            jti = payload.get("jti")  # jti = unique token ID
            if jti:
                # Mark this session as revoked in the database
                session = db.query(SessionModel).filter_by(token_jti=jti).first()
                if session:
                    session.revoked = True
                    db.commit()
        except Exception:
            pass  # If decoding fails, just say logout succeeded anyway

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(require_auth)):
    """Return the profile of the currently logged-in user."""
    return _user_to_response(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    user: User = Depends(require_auth),
    db: DBSession = Depends(get_db),
):
    """Update the current user's display name, avatar initials, or password."""
    # Update display name if provided
    if body.display_name:
        user.display_name = body.display_name.strip()
        initials = "".join([n[0].upper() for n in user.display_name.split()[:2]])
        user.avatar_initials = initials[:2]

    # Update avatar initials if provided
    if body.avatar_initials:
        user.avatar_initials = body.avatar_initials[:2].upper()

    # Change password — requires the current password as verification
    if body.new_password:
        if not body.current_password:
            raise HTTPException(400, "Current password is required to set a new password")
        if not _verify_password(body.current_password, user.password_hash):
            raise HTTPException(400, "Current password is incorrect")
        valid, msg = _validate_password(body.new_password)
        if not valid:
            raise HTTPException(400, msg)
        user.password_hash = _hash_password(body.new_password)

    db.commit()
    db.refresh(user)

    return _user_to_response(user)
