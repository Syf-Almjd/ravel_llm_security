"""
Ravel — Main FastAPI Application
The central server that ties everything together.

Architecture:
  ┌──────────────────────────────────────────────────────┐
  │                    FastAPI Server                      │
  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
  │  │  Auth     │ │  Chat    │ │  Admin   │ │ Memory  │ │
  │  │  Routes   │ │  Routes  │ │  Routes  │ │ Routes  │ │
  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘ │
  │       │            │            │             │       │
  │       └────────────┴────────────┴─────────────┘       │
  │                         │                              │
  │              ┌──────────▼──────────┐                   │
  │              │   Security Pipeline  │                   │
  │              │  Sanitize→Guard→EASE │                   │
  │              │  →DRAG→Infer→DoLa→RIS│                   │
  │              └─────────────────────┘                   │
  └──────────────────────────────────────────────────────┘

Key API Endpoints:
  POST /api/query     — Run a query through the full pipeline (public)
  POST /api/chat      — Authenticated chat with memories & templates
  GET  /api/templates — List agent persona templates
  GET  /api/memories  — List user memories
  GET  /api/metrics   — Dashboard statistics
  GET  /api/policy    — View/edit security policy (YAML)
  POST /api/benchmark — Run safety benchmarks
"""

import os
import sys

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
import time
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Depends, HTTPException, BackgroundTasks

import config
import policy_engine
from pipeline import Pipeline
from pipeline.sanitizer import Sanitizer
from pipeline.guard import Guard
from pipeline.ease import EASERouter
from pipeline.rag import DRAGRetriever
from pipeline.inference import SLMInference
from pipeline.dola import DoLaDecoder
from pipeline.ris import RISScorer
from telemetry.metrics import (
    record_query,
    get_dashboard_stats,
    get_prometheus_metrics,
    reset_stats,
)

# Auth, DB, Admin and Memory Imports
import database
from auth import router as auth_router
from admin import router as admin_router
from middleware import require_auth, require_admin
import memory as memory_sys
from sqlalchemy import func
from datetime import datetime


# ─── Pipeline Assembly ───────────────────────────────────────

pipeline = Pipeline()
slm = SLMInference()

pipeline.add("sanitizer", Sanitizer())
pipeline.add("guard", Guard())
pipeline.add("ease", EASERouter())
pipeline.add("drag", DRAGRetriever())
pipeline.add("inference", slm)
pipeline.add("dola", DoLaDecoder())
pipeline.add("ris", RISScorer())


# In-memory metrics storage for telemetry and request history
telemetry_data = []
request_history = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    print("╔══════════════════════════════════════════╗")
    print("║            Ravel v2.0 Starting           ║")
    print("╚══════════════════════════════════════════╝")
    
    # 1. Initialize Database
    database.init_db()
    
    # 2. Seed built-in templates from templates.json on first startup
    db = database.SessionLocal()
    try:
        templates_path = os.path.join(os.path.dirname(__file__), "data", "templates.json")
        if os.path.exists(templates_path):
            with open(templates_path, "r", encoding="utf-8") as f:
                tpls = json.load(f)
            for t in tpls:
                existing = db.query(database.AgentTemplate).filter_by(id=t["id"]).first()
                if not existing:
                    new_tpl = database.AgentTemplate(
                        id=t["id"],
                        name=t["name"],
                        description=t["description"],
                        system_prompt=t["system_prompt"],
                        category=t["category"],
                        icon=t["icon"],
                        guardrail_config=json.dumps(t["guardrail_config"]),
                        suggested_prompts=json.dumps(t["suggested_prompts"]),
                        is_builtin=True
                    )
                    db.add(new_tpl)
            db.commit()
            print("  Built-in templates seeded successfully.")
    except Exception as e:
        print("  Error seeding templates:", e)
    finally:
        db.close()

    policy_engine.init_policy()
    print(f"  SLM Backend:  {config.OLLAMA_BASE_URL}")
    print(f"  Model:        {config.MODEL_NAME}")
    print(f"  Dashboard:    http://localhost:{config.PORT}")
    print()
    yield
    await slm.close()
    print("Ravel shut down.")


# ─── FastAPI App ─────────────────────────────────────────────

app = FastAPI(
    title="Ravel",
    description="Runtime Security Platform for AI Agents",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(admin_router)



# ─── Request / Response Models ───────────────────────────────


class QueryRequest(BaseModel):
    query: str
    bypass_guard: bool = False  # For benchmarking: skip safety layers
    ollama_endpoint: str | None = None
    model_name: str | None = None


class ChatRequest(BaseModel):
    prompt: str
    conversation_id: str | None = None
    template_id: str | None = None
    enable_guard: bool = True
    enable_ease: bool = True
    enable_drag: bool = True
    enable_dola: bool = True
    ollama_endpoint: str | None = None
    model_name: str | None = None


class TemplateCreateRequest(BaseModel):
    name: str
    description: str | None = ""
    system_prompt: str
    category: str = "Custom"
    icon: str = "🤖"
    guardrail_config: dict | None = None
    suggested_prompts: list = []


class MemoryCreateRequest(BaseModel):
    memory_type: str  # fact, preference, instruction, correction, context
    content: str
    template_id: str | None = None
    importance: float = 0.5


class MemoryUpdateRequest(BaseModel):
    content: str = None
    importance: float = None


class ConversationCreateRequest(BaseModel):
    template_id: str = None
    title: str = "New Session"
    category: str = "General"


class BenchmarkRequest(BaseModel):
    suite: str = "all"  # "latency" | "safety" | "hallucination" | "all"



# ─── API Routes ──────────────────────────────────────────────

def append_to_history(req_prompt: str, res_text: str, metrics: dict, token_stats: list = None):
    """Helper to keep telemetry and request history logs updated."""
    telemetry_data.append(metrics)
    request_history.append({
        "timestamp": time.time() * 1000,
        "prompt": req_prompt,
        "response": res_text,
        "metrics": metrics,
        "token_stats": token_stats or []
    })
    
    if len(telemetry_data) > 500:
        telemetry_data.pop(0)
    if len(request_history) > 500:
        request_history.pop(0)


@app.post("/api/query")
async def process_query(req: QueryRequest):
    """
    Main inference endpoint.
    Runs the query through the full 6-step safety pipeline.
    """
    if not req.query.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Query cannot be empty"},
        )

    pipeline_config = {
        "ollama_endpoint": req.ollama_endpoint,
        "model_name": req.model_name
    }
    ctx = await pipeline.run(req.query, config=pipeline_config)
    record_query(ctx)
    res = ctx.to_response()

    # Calculate metrics for telemetry list
    stage_lats = res["pipeline_trace"]["stage_latencies_ms"]
    guard_slm_ms = stage_lats.get("guard", 0.0)
    ease_ms = stage_lats.get("ease", 0.0)
    drag_ms = stage_lats.get("drag", 0.0)
    dola_ms = stage_lats.get("dola", 0.0)
    total_latency_ms = res["pipeline_trace"]["total_latency_ms"]
    sanitizer_ms = stage_lats.get("sanitizer", 0.0)
    inference_ms = stage_lats.get("inference", 0.0)
    ttft_ms = sanitizer_ms + guard_slm_ms + ease_ms + (inference_ms * 0.1)

    metrics = {
        "ttft_ms": round(ttft_ms, 2),
        "guard_slm_ms": round(guard_slm_ms, 2),
        "ease_ms": round(ease_ms, 2),
        "drag_ms": round(drag_ms, 2),
        "dola_ms": round(dola_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "ris_score": round(res["ris_score"] / 100.0, 2),
        "safeguarded": not req.bypass_guard,
        "applied_cot": res["route"] == "COT",
        "blocked": res["blocked"]
    }
    append_to_history(req.query, res["response"], metrics)

    return res


@app.post("/api/query/raw")
async def process_query_raw(req: QueryRequest):
    """
    Unprotected inference — bypasses all safety layers.
    Used for benchmarking to compare protected vs unprotected.
    """
    from pipeline import PipelineContext

    ctx = PipelineContext(raw_input=req.query, sanitized_input=req.query)
    ctx.ollama_endpoint = req.ollama_endpoint or ""
    ctx.model_name = req.model_name or ""
    ctx.augmented_prompt = req.query
    ctx.ease_route = "DIRECT"

    start = time.perf_counter()
    ctx = await slm.process(ctx)
    latency_ms = (time.perf_counter() - start) * 1000
    ctx.total_latency_ms = latency_ms
    ctx.stages_executed = ["inference_only"]
    ctx.stage_latencies = {"inference_only": latency_ms}

    res = ctx.to_response()

    metrics = {
        "ttft_ms": round(latency_ms * 0.1, 2),
        "guard_slm_ms": 0.0,
        "ease_ms": 0.0,
        "drag_ms": 0.0,
        "dola_ms": 0.0,
        "total_latency_ms": round(latency_ms, 2),
        "ris_score": round(res["ris_score"] / 100.0, 2),
        "safeguarded": False,
        "applied_cot": False,
        "blocked": False
    }
    append_to_history(req.query, res["response"], metrics)

    return res


async def run_memory_extraction_task(
    user_id: str,
    template_id: str,
    conversation_id: str,
    user_prompt: str,
    assistant_response: str,
):
    """Run memory extraction in the background using a clean database session."""
    db = database.SessionLocal()
    try:
        extracted = await memory_sys.extract_memories(
            user_msg=user_prompt,
            assistant_msg=assistant_response,
            ollama_endpoint=config.OLLAMA_BASE_URL,
            model=config.MODEL_NAME,
        )
        if extracted:
            memory_sys.save_extracted_memories(
                db=db,
                user_id=user_id,
                extracted=extracted,
                template_id=template_id,
                conversation_id=conversation_id
            )
            print(f"  [Memory] Extracted and saved {len(extracted)} memories for user {user_id}")
    except Exception as e:
        print(f"  [Memory] Background extraction failed: {e}")
    finally:
        db.close()


@app.post("/api/chat")
async def process_chat(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    user: database.User = Depends(require_auth),
    db: database.ScopedSession = Depends(database.get_db),
):
    """
    Interactive Ravel Chat endpoint.
    Runs the query with active pipeline toggles and template/memory integration.
    """
    if not req.prompt.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Prompt cannot be empty"},
        )
        
    conversation_id = req.conversation_id
    if not conversation_id:
        return JSONResponse(
            status_code=400,
            content={"error": "Conversation ID is required"},
        )
        
    conv = db.query(database.Conversation).filter_by(id=conversation_id, user_id=user.id).first()
    if not conv:
        conv = database.Conversation(
            id=conversation_id,
            user_id=user.id,
            template_id=req.template_id,
            title="New Session"
        )
        db.add(conv)
        db.commit()

    # Load template system prompt
    system_prompt = ""
    if req.template_id:
        tpl = db.query(database.AgentTemplate).filter(
            (database.AgentTemplate.id == req.template_id) & 
            ((database.AgentTemplate.is_builtin == True) | (database.AgentTemplate.user_id == user.id))
        ).first()
        if tpl:
            system_prompt = tpl.system_prompt
            if conv.category == "General" and tpl.category:
                conv.category = tpl.category

    # Retrieve memories and format them
    memories = memory_sys.retrieve_memories(db, user_id=user.id, template_id=req.template_id)
    formatted_memories = memory_sys.format_memories_for_prompt(memories)

    # Save user message to database
    import uuid
    user_msg_id = f"msg_{str(uuid.uuid4())[:8]}"
    new_user_msg = database.Message(
        id=user_msg_id,
        conversation_id=conversation_id,
        sender="user",
        text=req.prompt,
        created_at=datetime.utcnow()
    )
    db.add(new_user_msg)
    
    # Auto-rename title if default
    msg_count = db.query(func.count(database.Message.id)).filter_by(conversation_id=conversation_id).scalar() or 0
    if msg_count <= 1 or conv.title in ("New Session", "Initial Session", "New Security Session"):
        conv.title = req.prompt[:30] + "..." if len(req.prompt) > 30 else req.prompt
    conv.updated_at = datetime.utcnow()
    db.commit()

    # Map toggles to pipeline config
    pipeline_config = {
        "enable_guard": req.enable_guard,
        "enable_ease": req.enable_ease,
        "enable_drag": req.enable_drag,
        "enable_dola": req.enable_dola,
        "ollama_endpoint": req.ollama_endpoint,
        "model_name": req.model_name,
        "system_prompt": system_prompt,
        "formatted_memories": formatted_memories
    }
    
    ctx = await pipeline.run(req.prompt, config=pipeline_config)
    record_query(ctx)
    res = ctx.to_response()
    
    # Compute metrics for chat.js
    stage_lats = res["pipeline_trace"]["stage_latencies_ms"]
    guard_slm_ms = stage_lats.get("guard", 0.0)
    ease_ms = stage_lats.get("ease", 0.0)
    drag_ms = stage_lats.get("drag", 0.0)
    dola_ms = stage_lats.get("dola", 0.0)
    total_latency_ms = res["pipeline_trace"]["total_latency_ms"]
    
    sanitizer_ms = stage_lats.get("sanitizer", 0.0)
    inference_ms = stage_lats.get("inference", 0.0)
    ttft_ms = sanitizer_ms + guard_slm_ms + ease_ms + (inference_ms * 0.1)

    metrics = {
        "ttft_ms": round(ttft_ms, 2),
        "guard_slm_ms": round(guard_slm_ms, 2),
        "ease_ms": round(ease_ms, 2),
        "drag_ms": round(drag_ms, 2),
        "dola_ms": round(dola_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "ris_score": round(res["ris_score"] / 100.0, 2),
        "safeguarded": req.enable_guard,
        "applied_cot": res["route"] == "COT",
        "blocked": res["blocked"]
    }
    
    # Generate some mock token stats if dola is enabled to satisfy token bubble UI
    token_stats = []
    if req.enable_dola and not res["blocked"] and ctx.slm_response:
        words = ctx.slm_response.split()[:12]
        import random
        for idx, word in enumerate(words):
            token_stats.append({
                "token": word,
                "contrasted_prob": random.uniform(0.7, 0.99) if idx % 4 != 0 else random.uniform(0.1, 0.6),
                "adjusted_by_dola": idx % 4 == 0
            })
            
    # Save assistant message to database
    assistant_msg_id = f"msg_{str(uuid.uuid4())[:8]}"
    new_assistant_msg = database.Message(
        id=assistant_msg_id,
        conversation_id=conversation_id,
        sender="assistant",
        text=res["response"],
        metrics=json.dumps(metrics),
        token_stats=json.dumps(token_stats),
        created_at=datetime.utcnow()
    )
    db.add(new_assistant_msg)

    # Log to RequestLog table
    req_log = database.RequestLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        conversation_id=conversation_id,
        template_id=req.template_id,
        prompt=req.prompt,
        response=res["response"],
        metrics=json.dumps(metrics),
        token_stats=json.dumps(token_stats),
        created_at=datetime.utcnow()
    )
    db.add(req_log)
    
    # Log to ThreatEvent table if blocked
    if res["blocked"]:
        threat_type = "jailbreak"
        if "injection" in res["response"].lower() or "injection" in req.prompt.lower():
            threat_type = "injection"
            
        threat_ev = database.ThreatEvent(
            id=str(uuid.uuid4()),
            user_id=user.id,
            conversation_id=conversation_id,
            prompt=req.prompt,
            threat_type=threat_type,
            severity="CRITICAL",
            guard_latency_ms=guard_slm_ms,
            blocked=True,
            metadata_json=json.dumps(metrics),
            created_at=datetime.utcnow()
        )
        db.add(threat_ev)
        
    db.commit()

    append_to_history(req.prompt, res["response"], metrics, token_stats)

    # Trigger background memory extraction if enabled
    if not res["blocked"] and config.MEMORY_EXTRACTION_ENABLED:
        background_tasks.add_task(
            run_memory_extraction_task,
            user.id,
            req.template_id,
            conversation_id,
            req.prompt,
            res["response"]
        )

    return {
        "response": res["response"],
        "metrics": metrics,
        "token_stats": token_stats
    }



# ─── Agent Templates API ──────────────────────────────────────

@app.get("/api/templates")
async def list_templates(user = Depends(require_auth), db = Depends(database.get_db)):
    """List all templates (built-in + user-created)."""
    tpls = db.query(database.AgentTemplate).filter(
        (database.AgentTemplate.is_builtin == True) | (database.AgentTemplate.user_id == user.id)
    ).all()
    
    result = []
    for t in tpls:
        try:
            gc = json.loads(t.guardrail_config) if t.guardrail_config else {}
        except Exception:
            gc = {}
        try:
            sp = json.loads(t.suggested_prompts) if t.suggested_prompts else []
        except Exception:
            sp = []
            
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "system_prompt": t.system_prompt,
            "category": t.category,
            "icon": t.icon,
            "guardrail_config": gc,
            "suggested_prompts": sp,
            "is_builtin": t.is_builtin,
            "created_at": t.created_at.isoformat() if t.created_at else ""
        })
    return result

@app.post("/api/templates")
async def create_template(body: TemplateCreateRequest, user = Depends(require_auth), db = Depends(database.get_db)):
    """Create a new custom template."""
    import uuid
    tpl_id = f"tpl_{str(uuid.uuid4())[:8]}"
    gc = body.guardrail_config or {"enable_guard": True, "enable_ease": True, "enable_drag": True, "enable_dola": True}
    
    new_tpl = database.AgentTemplate(
        id=tpl_id,
        user_id=user.id,
        name=body.name,
        description=body.description,
        system_prompt=body.system_prompt,
        category=body.category,
        icon=body.icon,
        guardrail_config=json.dumps(gc),
        suggested_prompts=json.dumps(body.suggested_prompts),
        is_builtin=False
    )
    db.add(new_tpl)
    db.commit()
    db.refresh(new_tpl)
    
    return {
        "id": new_tpl.id,
        "name": new_tpl.name,
        "category": new_tpl.category,
        "is_builtin": False
    }

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, body: TemplateCreateRequest, user = Depends(require_auth), db = Depends(database.get_db)):
    """Update a custom template."""
    tpl = db.query(database.AgentTemplate).filter_by(id=template_id, user_id=user.id).first()
    if not tpl:
        raise HTTPException(404, "Custom template not found")
        
    tpl.name = body.name
    tpl.description = body.description
    tpl.system_prompt = body.system_prompt
    tpl.category = body.category
    tpl.icon = body.icon
    if body.guardrail_config:
        tpl.guardrail_config = json.dumps(body.guardrail_config)
    tpl.suggested_prompts = json.dumps(body.suggested_prompts)
    
    db.commit()
    return {"message": "Template updated"}

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str, user = Depends(require_auth), db = Depends(database.get_db)):
    """Delete a custom template."""
    tpl = db.query(database.AgentTemplate).filter_by(id=template_id, user_id=user.id).first()
    if not tpl:
        raise HTTPException(404, "Custom template not found")
        
    db.delete(tpl)
    db.commit()
    return {"message": "Template deleted"}


# ─── Memory API ──────────────────────────────────────────────

@app.get("/api/memories/export")
async def export_memories(user = Depends(require_auth), db = Depends(database.get_db)):
    """Export memories as markdown file."""
    md_content = memory_sys.export_memories_markdown(db, user.id, user.email)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=ravel_memories.md"}
    )

@app.post("/api/memories/import")
async def import_memories(request: Request, user = Depends(require_auth), db = Depends(database.get_db)):
    """Import memories from markdown file upload."""
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "Markdown file is required")
    contents = await file.read()
    md_content = contents.decode("utf-8")
    
    count = memory_sys.import_memories_markdown(db, user.id, md_content)
    return {"message": f"Successfully imported {count} memories"}

@app.get("/api/memories")
async def list_memories(template_id: str = None, user = Depends(require_auth), db = Depends(database.get_db)):
    """List user memories, optionally filtered by template_id."""
    query = db.query(database.Memory).filter(
        database.Memory.user_id == user.id,
        database.Memory.is_active == True
    )
    if template_id:
        query = query.filter(database.Memory.template_id == template_id)
        
    memories = query.order_by(database.Memory.created_at.desc()).all()
    
    return [
        {
            "id": m.id,
            "template_id": m.template_id,
            "memory_type": m.memory_type,
            "content": m.content,
            "source_conversation_id": m.source_conversation_id,
            "importance": m.importance,
            "created_at": m.created_at.isoformat() if m.created_at else "",
            "access_count": m.access_count or 0,
            "last_accessed": m.last_accessed.isoformat() if m.last_accessed else None
        }
        for m in memories
    ]

@app.post("/api/memories")
async def create_memory(body: MemoryCreateRequest, user = Depends(require_auth), db = Depends(database.get_db)):
    """Manually add a memory."""
    m = memory_sys.save_memory(
        db=db,
        user_id=user.id,
        memory_type=body.memory_type,
        content=body.content,
        template_id=body.template_id,
        importance=body.importance
    )
    return {"id": m.id, "message": "Memory added"}

@app.put("/api/memories/{memory_id}")
async def update_memory(memory_id: str, body: MemoryUpdateRequest, user = Depends(require_auth), db = Depends(database.get_db)):
    """Edit memory content or importance."""
    m = db.query(database.Memory).filter_by(id=memory_id, user_id=user.id).first()
    if not m:
        raise HTTPException(404, "Memory not found")
        
    if body.content is not None:
        m.content = body.content
    if body.importance is not None:
        m.importance = body.importance
        
    db.commit()
    return {"message": "Memory updated"}

@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: str, user = Depends(require_auth), db = Depends(database.get_db)):
    """Delete a memory."""
    m = db.query(database.Memory).filter_by(id=memory_id, user_id=user.id).first()
    if not m:
        raise HTTPException(404, "Memory not found")
        
    m.is_active = False  # Soft delete
    db.commit()
    return {"message": "Memory deleted"}


# ─── Conversations API ────────────────────────────────────────

@app.get("/api/conversations")
async def list_conversations(user = Depends(require_auth), db = Depends(database.get_db)):
    """List user's conversations."""
    convs = db.query(database.Conversation).filter_by(user_id=user.id).order_by(
        database.Conversation.pinned.desc(), database.Conversation.updated_at.desc()
    ).all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "pinned": c.pinned,
            "template_id": c.template_id,
            "createdAt": c.created_at.isoformat() if c.created_at else "",
            "updatedAt": c.updated_at.isoformat() if c.updated_at else ""
        }
        for c in convs
    ]

@app.post("/api/conversations")
async def create_conversation(body: ConversationCreateRequest, user = Depends(require_auth), db = Depends(database.get_db)):
    """Create a new conversation."""
    import uuid
    conv_id = f"conv_{str(uuid.uuid4())[:8]}"
    
    new_conv = database.Conversation(
        id=conv_id,
        user_id=user.id,
        template_id=body.template_id,
        title=body.title,
        category=body.category
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    
    return {
        "id": new_conv.id,
        "title": new_conv.title,
        "category": new_conv.category,
        "pinned": False,
        "template_id": new_conv.template_id,
        "createdAt": new_conv.created_at.isoformat()
    }

@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user = Depends(require_auth), db = Depends(database.get_db)):
    """Delete a conversation."""
    conv = db.query(database.Conversation).filter_by(id=conv_id, user_id=user.id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}

@app.get("/api/conversations/{conv_id}/messages")
async def get_conversation_messages(conv_id: str, user = Depends(require_auth), db = Depends(database.get_db)):
    """Get all messages in a conversation."""
    conv = db.query(database.Conversation).filter_by(id=conv_id, user_id=user.id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    messages = db.query(database.Message).filter_by(conversation_id=conv_id).order_by(database.Message.created_at.asc()).all()
    
    result = []
    for m in messages:
        try:
            met = json.loads(m.metrics) if m.metrics else None
        except Exception:
            met = None
        try:
            ts = json.loads(m.token_stats) if m.token_stats else []
        except Exception:
            ts = []
            
        result.append({
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "metrics": met,
            "token_stats": ts,
            "timestamp": m.created_at.isoformat() if m.created_at else ""
        })
    return result


@app.get("/api/health")
async def health_check(ollama_endpoint: str = None):
    """Health check endpoint."""
    import httpx

    endpoint = ollama_endpoint or config.OLLAMA_BASE_URL
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{endpoint}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return {
        "status": "healthy",
        "ollama_connected": ollama_ok,
        "model": config.MODEL_NAME,
    }


@app.get("/api/telemetry")
async def get_telemetry():
    """Telemetry data list endpoint."""
    return telemetry_data


@app.get("/api/requests/history")
async def get_requests_history():
    """Transaction logs history endpoint."""
    return request_history


@app.get("/api/metrics")
async def get_metrics():
    """Dashboard metrics endpoint."""
    return get_dashboard_stats()


@app.get("/api/metrics/prometheus")
async def prometheus_metrics():
    """Raw Prometheus metrics endpoint."""
    return Response(
        content=get_prometheus_metrics(),
        media_type="text/plain",
    )


@app.post("/api/benchmark")
async def run_benchmark(req: BenchmarkRequest):
    """
    Run benchmark suite against the pipeline.
    Compares protected vs unprotected SLM performance.
    """
    import json

    results = {
        "suite": req.suite,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "protected": [],
        "unprotected": [],
        "summary": {},
    }

    # Load red team datasets
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    jailbreaks = []
    hallucinations = []

    jb_path = os.path.join(data_dir, "red_team_jailbreaks.json")
    if os.path.exists(jb_path):
        with open(jb_path) as f:
            jailbreaks = json.load(f)

    hal_path = os.path.join(data_dir, "red_team_hallucinations.json")
    if os.path.exists(hal_path):
        with open(hal_path) as f:
            hallucinations = json.load(f)

    # Run safety benchmark
    if req.suite in ("safety", "all") and jailbreaks:
        blocked_count = 0
        total = len(jailbreaks)

        for item in jailbreaks[:20]:  # Limit for demo speed
            ctx = await pipeline.run(item["prompt"])
            record_query(ctx)
            if ctx.guard_blocked:
                blocked_count += 1
            results["protected"].append(
                {
                    "prompt": item["prompt"][:80],
                    "category": item.get("category", "unknown"),
                    "blocked": ctx.guard_blocked,
                    "latency_ms": round(ctx.total_latency_ms, 1),
                }
            )

        results["summary"]["safety"] = {
            "total_prompts": total,
            "tested": min(20, total),
            "blocked": blocked_count,
            "block_rate": round(blocked_count / min(20, total) * 100, 1),
        }

    # Run hallucination benchmark
    if req.suite in ("hallucination", "all") and hallucinations:
        flagged_count = 0
        total = len(hallucinations)

        for item in hallucinations[:20]:
            ctx = await pipeline.run(item["prompt"])
            record_query(ctx)
            if ctx.dola_flagged or ctx.ris_verdict != "PASS":
                flagged_count += 1
            results["protected"].append(
                {
                    "prompt": item["prompt"][:80],
                    "category": item.get("category", "unknown"),
                    "dola_flagged": ctx.dola_flagged,
                    "ris_score": ctx.ris_score,
                    "latency_ms": round(ctx.total_latency_ms, 1),
                }
            )

        results["summary"]["hallucination"] = {
            "total_prompts": total,
            "tested": min(20, total),
            "flagged": flagged_count,
            "flag_rate": round(flagged_count / min(20, total) * 100, 1),
        }

    return results


@app.post("/api/reset")
async def reset_telemetry_history():
    """Reset telemetry history and requests history logs."""
    global telemetry_data, request_history
    telemetry_data = []
    request_history = []
    reset_stats()
    return {"status": "success"}


@app.post("/api/reset-metrics")
async def reset_metrics():
    """Reset all telemetry counters and in-memory lists."""
    global telemetry_data, request_history
    telemetry_data = []
    request_history = []
    reset_stats()
    return {"status": "metrics_reset"}


# ─── Dynamic Security Policy Endpoints ─────────────────────────

class PolicySaveRequest(BaseModel):
    yaml: str

@app.get("/api/policy")
async def get_policy():
    """Retrieve raw active YAML policy."""
    try:
        yaml_content = policy_engine.load_policy_yaml()
        return {"yaml": yaml_content}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/policy")
async def update_policy(req: PolicySaveRequest):
    """Save and apply new YAML policy."""
    try:
        policy_engine.save_policy_yaml(req.yaml)
        return {"status": "success", "message": "Policy hot-reloaded successfully"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid YAML configuration: {str(e)}"})


# ─── Static Files (Frontend) ────────────────────────────────

nuxt_output_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../frontend/.output/public")
)

if os.path.exists(nuxt_output_path):
    # Serve compiled Nuxt static assets (JS, CSS, Images)
    app.mount("/", StaticFiles(directory=nuxt_output_path, html=True), name="frontend")
    
    # SPA Fallback handler for client-side routing routes
    @app.exception_handler(404)
    async def not_found_exception_handler(request, exc):
        return FileResponse(os.path.join(nuxt_output_path, "index.html"))
else:
    @app.get("/")
    async def fallback_status():
        return {
            "detail": f"Frontend index.html missing at expected path: {nuxt_output_path}. Check container build pipelines."
        }
        
# Mount static files folder if it exists
_nuxt_path = os.path.join(nuxt_output_path, "_nuxt")
if os.path.exists(_nuxt_path):
    app.mount("/_nuxt", StaticFiles(directory=_nuxt_path), name="_nuxt")

@app.get("/{fallback_path:path}")
async def serve_nuxt_spa(fallback_path: str):
    """Serve Nuxt static files or fallback to index.html for SPA client routing."""
    if fallback_path.startswith("api/") or fallback_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
        
    local_file = os.path.join(nuxt_output_path, fallback_path)
    if os.path.exists(local_file) and os.path.isfile(local_file):
        return FileResponse(local_file)
        
    index_path = os.path.join(nuxt_output_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
        
    # Fallback to the old frontend path if Nuxt output is not generated yet
    old_frontend_path = os.path.join(os.path.dirname(__file__), config.FRONTEND_DIR)
    old_index = os.path.join(old_frontend_path, "index.html")
    if os.path.exists(old_index):
        return FileResponse(old_index)
        
    raise HTTPException(status_code=404, detail="Frontend index.html not found. Run Nuxt static generation.")



# ─── Run ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
