FROM python:3.11-slim

# update to Node.js v22
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Build Frontend (Nuxt Static Generation)
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npx nuxt generate

# 2. Setup Backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/

# Train the GUARD-SLM model
RUN cd backend && python scripts/train_guard.py

# Seed ChromaDB
RUN cd backend && python scripts/seed_chromadb.py

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
