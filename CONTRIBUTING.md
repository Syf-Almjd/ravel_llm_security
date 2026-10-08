# Contributing to Ravel

Thank you for your interest in contributing to Ravel! Ravel is an open-source zero-trust runtime security platform engineered to protect Small Language Models (SLMs) and autonomous AI agents without sacrificing inference speed.

## Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 20+** and **npm**
- **Git**
- Optional: **Ollama** for local inference testing

### Local Workspace Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/ravel_llm_security.git
   cd ravel_llm_security
   ```

2. **Configure Backend Environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   pip install pytest pytest-asyncio httpx ruff
   ```

3. **Train GUARD Classifier & Seed Data**:
   ```bash
   python backend/scripts/train_guard.py
   python backend/scripts/seed_chromadb.py
   python backend/scripts/generate_templates.py
   ```

4. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm run generate  # Verifies clean static build
   cd ..
   ```

---

## Development Workflow

### Running the Services Locally

1. **Start Backend API Server**:
   ```bash
   source .venv/bin/activate
   cd backend
   uvicorn app:app --reload --port 8000
   ```

2. **Start Frontend Dev Server**:
   ```bash
   cd frontend
   npm run dev -- --port 3000
   ```

Visit `http://localhost:3000` to interact with the web interface.

---

## Testing Guidelines

We enforce automated testing across all security layers and API routes.

```bash
# Run backend test suite
source .venv/bin/activate
pytest backend/tests/ -v

# Run Python linting checks
ruff check backend/
```

- Every bug fix should be accompanied by a regression test in `backend/tests/`.
- Every new pipeline stage or API endpoint must include unit tests with isolated in-memory SQLite fixtures.

---

## Coding Standards

- **Python**:
  - Follow PEP 8 and modern Python conventions (PEP 604 union types `X | None`, timezone-aware UTC `datetime.now(timezone.utc)`).
  - Explicit error handling with FastAPI `HTTPException`.
  - Type annotations on all public functions.
- **Frontend**:
  - Vue 3 Composition API `<script setup>` in Nuxt 3.
  - Defensive rendering: always protect optional object properties with optional chaining (`?.`) and nullish coalescing (`??`).
  - No untyped or unhandled promises; use try/catch or graceful `.catch()` fallbacks.

---

## Branch & Pull Request Conventions

1. Create a descriptive branch from `main`:
   - Feature: `feat/<feature-name>`
   - Bug fix: `fix/<bug-name>`
   - Documentation: `docs/<topic>`
   - Maintenance: `chore/<task>`
2. Write clear, imperative commit messages (e.g. `fix(sanitizer): normalize unicode homoglyphs`).
3. Ensure CI passes cleanly before requesting review.
4. Open a pull request against `main` using our PR template.
