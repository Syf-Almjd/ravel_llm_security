"""
Ravel — Auth Middleware
Handles JWT token creation/validation, rate limiting, and route protection.
This is the "gatekeeper" — it checks who you are before letting you access routes.
"""

import os
import time
import uuid
import secrets  # For generating cryptographically secure random values
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import jwt  # PyJWT — JSON Web Token library for creating/verifying tokens
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from database import get_db, User, Session as SessionModel

# ─── JWT Configuration ───────────────────────────────────────
# JWT tokens are how we keep users logged in without storing passwords in cookies.

JWT_ALGORITHM = "HS256"       # HMAC-SHA256 (standard signing algorithm)
JWT_EXPIRY_HOURS = 24          # Tokens expire after 24 hours

# The secret key is used to sign tokens — if someone gets it, they can forge tokens.
# We auto-generate it on first run and save it to a file so it survives restarts.
SECRET_KEY_PATH = os.path.join(os.path.dirname(__file__), "data", ".secret_key")

def _load_or_create_secret():
    """Load the signing secret from file, or generate a new one if it doesn't exist."""
    os.makedirs(os.path.dirname(SECRET_KEY_PATH), exist_ok=True)
    if os.path.exists(SECRET_KEY_PATH):
        with open(SECRET_KEY_PATH, "r") as f:
            return f.read().strip()
    # First run — generate a random 64-character hex string as the secret
    secret = secrets.token_hex(32)
    with open(SECRET_KEY_PATH, "w") as f:
        f.write(secret)
    return secret

JWT_SECRET = _load_or_create_secret()


# ─── JWT Token Operations ────────────────────────────────────

def create_jwt(user_id: str, role: str) -> tuple[str, str]:
    """Create a signed JWT token for a user.
    Returns (token_string, unique_token_id, expiry_datetime)."""
    jti = str(uuid.uuid4())  # Unique ID for this token (used for revocation)
    exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {
        "sub": user_id,       # "subject" — who this token belongs to
        "role": role,          # Their role (admin/user) — checked by require_admin
        "jti": jti,            # Unique token ID — checked during revocation
        "exp": exp,            # Expiry time — token is invalid after this
        "iat": datetime.utcnow(),  # "issued at" — when was this token created
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, jti, exp


def decode_jwt(token: str) -> dict:
    """Decode and verify a JWT token. Returns the payload dict.
    Raises HTTP 401 if token is expired or tampered with."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─── Rate Limiter ────────────────────────────────────────────
# Prevents brute force attacks by limiting how many login attempts per IP.

_rate_limit_store: dict[str, list[float]] = {}  # IP → list of timestamps
RATE_LIMIT_MAX = 5       # Max 5 attempts per window
RATE_LIMIT_WINDOW = 60   # Within 60 seconds

def check_rate_limit(ip: str):
    """Check if this IP has made too many requests recently. Raises 429 if limit exceeded."""
    now = time.time()
    if ip not in _rate_limit_store:
        _rate_limit_store[ip] = []
    
    # Remove timestamps older than our window (keep only recent attempts)
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]
    
    # If they've hit the limit, block them
    if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Try again in 60 seconds."
        )
    
    # Record this attempt
    _rate_limit_store[ip].append(now)


# ─── FastAPI Dependencies ────────────────────────────────────
# These are used as `Depends()` in route handlers to enforce auth.

def _extract_token(request: Request) -> Optional[str]:
    """Pull the JWT from the Authorization header or a cookie."""
    # Check Authorization header first (standard API approach)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Strip "Bearer " to get just the token
    
    # Fallback: check cookie (for browser-based sessions)
    token = request.cookies.get("ravel_token")
    if token:
        return token
    
    return None


async def get_current_user(
    request: Request,
    db: DBSession = Depends(get_db),
) -> Optional[User]:
    """Extract JWT from request, validate it, and return the User object.
    Returns None if no valid token found (does NOT raise an error).
    Use this for optional auth — routes that work with or without login."""
    token = _extract_token(request)
    if not token:
        return None
    
    try:
        payload = decode_jwt(token)
    except HTTPException:
        return None
    
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id:
        return None
    
    # Check if this token was revoked (e.g. user logged out)
    session = db.query(SessionModel).filter_by(token_jti=jti).first()
    if session and session.revoked:
        return None
    
    # Look up the user and make sure they're not banned
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.is_active:
        return None
    
    return user


async def require_auth(
    request: Request,
    db: DBSession = Depends(get_db),
) -> User:
    """FastAPI dependency — use this to protect a route.
    Returns the authenticated User, or raises 401 if not logged in.
    Usage: `user: User = Depends(require_auth)`"""
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


async def require_admin(
    user: User = Depends(require_auth),
) -> User:
    """FastAPI dependency — use this to restrict a route to admins only.
    Returns the admin User, or raises 403 if they're not an admin.
    Usage: `user: User = Depends(require_admin)`"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
