"""
Pytest configuration and shared fixtures for Ravel LLM Security.
"""

import os
import sys

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest
from app import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
from database import Base, User, get_db
from middleware import create_jwt

# Use an in-memory SQLite database for isolated fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a fresh transactional database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user and return (user, auth_headers)."""
    user = User(
        id="test-admin-id",
        email="admin@example.com",
        password_hash="$2b$12$e80y9m8L88Q4e7lqD6097e3gH.55vBfX2kC0eC5jQ6k8yE5yZq8yG",
        display_name="Admin User",
        role="admin",
        avatar_initials="AU",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    token, jti, exp = create_jwt(user.id, user.role)
    session = database.Session(token_jti=jti, user_id=user.id, expires_at=exp)
    db_session.add(session)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


@pytest.fixture
def regular_user(db_session):
    """Create a regular user and return (user, auth_headers)."""
    user = User(
        id="test-user-id",
        email="user@example.com",
        password_hash="$2b$12$e80y9m8L88Q4e7lqD6097e3gH.55vBfX2kC0eC5jQ6k8yE5yZq8yG",
        display_name="Standard User",
        role="user",
        avatar_initials="SU",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    token, jti, exp = create_jwt(user.id, user.role)
    session = database.Session(token_jti=jti, user_id=user.id, expires_at=exp)
    db_session.add(session)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    return user, headers
