"""
Ravel — Configuration
All tuneable constants in one place.
Think of this as the "control panel" for the entire system.
Change any value here and it affects the whole pipeline.
"""

# ─── SLM Backend ─────────────────────────────────────────────
# These control which AI model Ravel talks to for generating responses.
# Ollama is a local model runner — you can swap to any model it supports.
OLLAMA_BASE_URL = "http://localhost:11434"  # Where the Ollama server lives
MODEL_NAME = "gemma3:1b"  # Which model to use (Gemma 3 1B is small & fast)
MODEL_TEMPERATURE = 0.3   # How creative the model is (0=boring, 1=creative)
MODEL_MAX_TOKENS = 2048   # Max length of the model's response

# ─── Sanitizer (Step 1) ─────────────────────────────────────
# Limits to prevent abuse — if someone sends a huge input, we reject it.
MAX_INPUT_TOKENS = 4096   # Max tokens a user can send in one message
MAX_INPUT_BYTES = 16_384  # Max size in bytes (16 KB) for the raw input

# ─── GUARD-SLM (Step 2) ─────────────────────────────────────
# The Guard is an ML model that checks if input looks like a prompt injection.
# It uses an SVM (a fast ML classifier) trained on malicious vs. safe prompts.
GUARD_CONFIDENCE_THRESHOLD = 0.50  # If confidence < 50%, treat input as unsafe
BLOCKLIST_PATH = "data/keyword_blocklist.json"  # Extra keywords to always block
GUARD_MODEL_PATH = "models/guard_svm.pkl"       # The trained SVM model file
GUARD_VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"  # Converts text to numbers for the SVM

# ─── EASE Router (Step 3) ────────────────────────────────────
# EASE decides how "hard" a question is and routes it accordingly.
# DIRECT = simple question, answer directly (saves compute)
# COT = complex question, use chain-of-thought reasoning
# BORDERLINE = suspicious question, be extra careful
EASE_DIRECT_THRESHOLD = 0.30   # Score below 0.3 → simple question → DIRECT
EASE_COT_THRESHOLD = 0.70      # Score below 0.7 → complex → COT; above → BORDERLINE

# ─── DRAG / RAG (Step 4) ─────────────────────────────────────
# DRAG fetches relevant knowledge from a vector database (ChromaDB)
# to give the model extra context so it doesn't hallucinate.
CHROMA_PERSIST_DIR = "data/chroma_db"  # Where ChromaDB stores its data on disk
CHROMA_COLLECTION = "fact_cards"        # The name of our knowledge collection
RAG_TOP_K = 3                  # How many relevant documents to fetch
RAG_MIN_RELEVANCE = 0.65       # Only use documents that are 65%+ similar to the query

# ─── DoLa (Step 5) ───────────────────────────────────────────
# DoLa detects hallucinations by looking at how "confident" the model is
# about each word it generates. Low confidence = likely making things up.
DOLA_LOGPROB_THRESHOLD = -2.5  # Log probability below this = model is unsure
DOLA_HALLUCINATION_RATIO = 0.30  # If 30%+ of tokens are low-confidence → flag as hallucination

# ─── RIS Scoring (Step 6) ────────────────────────────────────
# RIS = Response Integrity Score. It grades the model's output on 4 dimensions.
# Each dimension gets a weight (they must add up to 1.0).
RIS_WEIGHTS = {
    "safety": 0.25,       # Is the response free of harmful content?
    "grounding": 0.30,    # Is the response based on facts (not made up)?
    "coherence": 0.25,    # Does the response make logical sense?
    "consistency": 0.20,  # Is the response internally consistent?
}
RIS_HIGH_THRESHOLD = 80   # Score ≥ 80 → PASS (response is good)
RIS_LOW_THRESHOLD = 50    # Score < 50 → BLOCK (response is bad), between = WARN

# ─── Telemetry ───────────────────────────────────────────────
# Controls whether we track metrics (query counts, latencies, scores).
TELEMETRY_ENABLED = True  # Set to False to disable all tracking

# ─── Server ──────────────────────────────────────────────────
# Where the FastAPI server listens and where to find the frontend files.
HOST = "0.0.0.0"          # 0.0.0.0 means "listen on all network interfaces"
PORT = 8000                # The port the API runs on
FRONTEND_DIR = "../frontend"  # Path to the Nuxt frontend (for serving static files)

# ─── Auth & Database ──────────────────────────────────────────
DATABASE_URL = "sqlite:///data/ravel.db"  # SQLite database file location
JWT_EXPIRY_HOURS = 24       # How long a login token stays valid (24 hours)
RATE_LIMIT_AUTH = 5         # Max login attempts per minute (prevents brute force)
MEMORY_EXTRACTION_ENABLED = True   # Whether to auto-extract memories from chats
MAX_MEMORIES_PER_USER = 500        # Cap on how many memories a user can store

