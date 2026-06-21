# Ravel — Runtime Security Platform for AI Agents

> **Protect agents, tools, memory, RAG, and workflows. Not just prompts.**

Ravel is an runtime security platform designed specifically to secure Small Language Models (SLMs) and AI agents without destroying their latency advantages. Instead of statically applying heavy safety checks to every single query (which destroys baseline SLM latency), Ravel dynamically routes queries through only the safety layers they need using selective compute.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Ollama** — [Install here](https://ollama.com/download)

### 1. Pull the Default SLM and init venv

```bash
ollama pull gemma3:1b
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
cd ravel/backend
pip install -r requirements.txt
```

### 3. Train the GUARD-SLM Classifier

```bash
python scripts/train_guard.py
```

### 4. Seed the Knowledge Base

```bash
python scripts/seed_chromadb.py
python scripts/generate_templates.py
```

### 5. Start the Server

```bash
python app.py
```

Open **http://localhost:8000** in your browser.

---

## 🛡 Security Architecture

```
Query ➔ Sanitizer ➔ GUARD ➔ EASE Router ➔ DRAG (RAG) ➔ SLM ➔ DoLa ➔ RIS ➔ Response
         (1ms)       (3ms)     (2ms)          (15ms)      (var)   (3ms)  (2ms)
```

### Pipeline Steps

| Step | Component | Purpose | Target Latency |
|------|-----------|---------|----------------|
| 1 | **Sanitizer** | Unicode normalization & script tag stripping | < 1ms |
| 2 | **GUARD-SLM** | Keyword blocklist & SVM activation classifier | < 5ms |
| 3 | **EASE** | Entropy-Aware Selective Routing (Direct vs. CoT) | < 2ms |
| 4 | **DRAG** | Distilled RAG with compressed fact-cards | < 15ms |
| 5 | **Inference** | SLM generation loop via Ollama | Variable |
| 6 | **DoLa** | Contrastive layer decoding to check truthfulness | < 3ms |
| 7 | **RIS** | Reasoning Integrity Score validation (0.00-1.00) | < 3ms |

---

## ⚡ API Reference

Ravel is designed to support a hybrid SaaS structure where the security policy plane is centralized, but inference execution endpoints (e.g. Ollama) can run on client localhost. All main endpoints accept connection configurations in the request body.

| Method | Endpoint | Request Fields | Description |
|--------|----------|----------------|-------------|
| POST | `/api/chat` | `prompt`, `ollama_endpoint`, `model_name`, `enable_guard` | Main interactive chat route with custom toggle flags |
| POST | `/api/query` | `query`, `ollama_endpoint`, `model_name`, `bypass_guard` | Synchronous prompt execution route |
| POST | `/api/query/raw` | `query`, `ollama_endpoint`, `model_name` | Raw prompt execution bypassing guardrails |
| GET | `/api/health` | None | Service health status and Ollama availability |
| GET | `/api/telemetry` | None | Platform performance and latency telemetry list |
| GET | `/api/requests/history` | None | Transaction request logs list |
| GET | `/api/metrics` | None | Aggregated dashboard stats |
| POST | `/api/benchmark` | `suite` | Run automated Red-Team test suite |
| POST | `/api/reset` | None | Clear platform telemetry & request history |

### Example Client Connection (SaaS Bridge to Local Ollama)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Python?",
    "ollama_endpoint": "http://localhost:11434",
    "model_name": "gemma3:1b",
    "enable_guard": true
  }'
```

---

## 💎 The Billion-Dollar Enterprise SaaS Vision

In modern enterprise workflows, LLMs are not isolated chat components; they are autonomous agents executing tool calls, database operations, and file queries. Ravel is positioned to lead the transition from simple text moderation to a comprehensive **Runtime Security Operations Center (SOC) for AI Agents**.

Our platform roadmap expands upon five enterprise capabilities:

### 1. Agent Runtime Firewall
Instead of only analyzing text prompts, Ravel monitors tool calls. The platform hooks into agent frameworks (e.g., CrewAI, LangGraph, MCP) and intercepts outgoing tool schema requests (e.g., `execute_sql`, `read_file`, `send_email`). Ravel evaluates the tool arguments against the enterprise compliance matrix in real-time, blocking unauthorized command parameters.

### 2. Context Drift & Semantic Displacement Detection
In multi-turn conversations, attackers use gradual prompting to push an agent away from its system boundaries. Ravel calculates semantic vector trajectories across conversation steps, alerting security teams when the conversation moves from user support to administrative instruction injection.

### 3. Direct & Indirect RAG Poisoning Scanners
Enterprise data sources (Notion databases, Confluence, Confluence pages, PDF attachments) can contain hidden instruction payloads designed to execute whenever an agent indexes them. Ravel acts as a document quarantine layer, scanning files at ingestion time for adversarial system command templates.

### 4. Decentralized Threat Signature Network
Ravel aggregates anonymized security events across tenants. If Tenant A is attacked with a novel jailbreak prompt, Ravel extracts the signature vector and publishes it to all active security nodes globally, providing immediate immunization for all enterprise customers.

### 5. Conversation Replay & Incident Forensics
When a model outputs sensitive data or runs a destructive script, security operations centers need to audit the event sequence. Ravel records full conversation graphs (inputs, vector matches, reasoning chains, and tool responses) as forensic logs, offering interactive replay timelines for audits.

---

## 📂 Project Structure

```
ravel/
├── backend/
│   ├── app.py                # FastAPI application
│   ├── config.py             # Configuration constants
│   ├── pipeline/             # 6-stage selective compute pipeline
│   ├── data/                 # Datasets and keyword blocklists
│   ├── scripts/              # Offline training & vector seeding scripts
│   └── telemetry/            # Prometheus counters
├── frontend/
│   ├── index.html            # SPA entry HTML
│   ├── style.css             # Main styling sheet
│   └── js/                   # SPA Client router, store, pages, and components
├── benchmarks/               # Performance and load testing
├── research/                 # Academic paper draft
├── Dockerfile
└── docker-compose.yml
```

---

## 📄 License

MIT
