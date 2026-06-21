"""
Ravel — Pipeline Orchestrator
The pipeline is the heart of Ravel. It chains all 6 security stages together:
  Sanitizer → Guard → EASE → DRAG → Inference → DoLa → RIS

Each stage reads and writes to a shared "context" object (PipelineContext).
If the Guard blocks a request, all downstream stages are skipped.
"""

import time
from dataclasses import dataclass, field


@dataclass
class PipelineContext:
    """Shared state object that gets passed through every pipeline stage.
    Each stage reads from it and writes its results back to it.
    Think of it as a "report card" that gets filled in as the query moves through."""

    # ── Input ────────────────────────────────────────────────
    raw_input: str = ""          # The original user message (before any processing)
    sanitized_input: str = ""    # The cleaned version (after removing attacks)

    # ── GUARD results ────────────────────────────────────────
    guard_safe: bool = True           # Did the input pass the safety check?
    guard_confidence: float = 1.0     # How confident is the guard? (0-1)
    guard_method: str = ""            # Which detection method was used? ("svm", "heuristic", etc.)
    guard_blocked: bool = False       # Was this request blocked?

    # ── EASE results ─────────────────────────────────────────
    ease_route: str = "DIRECT"        # How should we handle this query? DIRECT | COT | BORDERLINE
    ease_score: float = 0.0           # Complexity score (0-1)

    # ── RAG / DRAG results ───────────────────────────────────
    fact_cards: list = field(default_factory=list)  # Knowledge retrieved from ChromaDB
    augmented_prompt: str = ""        # The prompt with RAG context injected

    # ── Inference results ────────────────────────────────────
    slm_response: str = ""            # The AI model's response text
    logprobs: list = field(default_factory=list)  # Token probabilities (used by DoLa)

    # ── DoLa results ─────────────────────────────────────────
    dola_risk: float = 0.0            # Hallucination risk score (0-1)
    dola_flagged: bool = False        # Was this response flagged as hallucinated?

    # ── RIS results ──────────────────────────────────────────
    ris_score: float = 0.0            # Overall response quality score (0-100)
    ris_breakdown: dict = field(default_factory=dict)  # Per-dimension scores
    ris_verdict: str = "PASS"         # Final decision: PASS | WARN | BLOCK

    # ── Telemetry (performance tracking) ─────────────────────
    stage_latencies: dict = field(default_factory=dict)  # How long each stage took (ms)
    total_latency_ms: float = 0.0                        # Total pipeline time
    stages_executed: list = field(default_factory=list)   # Which stages actually ran

    # ── Dynamic configuration (set per-request) ──────────────
    ollama_endpoint: str = ""        # Custom model endpoint (if not using default)
    model_name: str = ""             # Which model to use
    system_prompt: str = ""          # The persona's system prompt
    formatted_memories: str = ""     # User memories injected into the prompt

    def to_response(self) -> dict:
        """Convert the pipeline results into a JSON-friendly dict for the API response.
        This is what the frontend receives after each query."""
        return {
            "response": self.slm_response,
            "blocked": self.guard_blocked,
            "ris_score": round(self.ris_score, 1),
            "ris_verdict": self.ris_verdict,
            "ris_breakdown": self.ris_breakdown,
            "route": self.ease_route,
            "fact_cards_used": len(self.fact_cards),
            "dola_risk": round(self.dola_risk, 3),
            "guard_confidence": round(self.guard_confidence, 3),
            "pipeline_trace": {
                "stages_executed": self.stages_executed,
                "stage_latencies_ms": {
                    k: round(v, 2) for k, v in self.stage_latencies.items()
                },
                "total_latency_ms": round(self.total_latency_ms, 2),
            },
        }


class Pipeline:
    """Runs all registered security stages in sequence.
    
    How it works:
    1. You add stages with `pipeline.add("name", stage_instance)`
    2. You run a query with `pipeline.run("user input")`
    3. Each stage processes the context and passes it to the next
    4. If any early stage blocks the request, downstream stages are skipped
    """

    def __init__(self):
        self.steps: list = []  # List of (name, stage) tuples

    def add(self, name: str, step):
        """Register a pipeline stage with a human-readable name.
        The name is used for telemetry and for toggling stages on/off."""
        self.steps.append((name, step))

    async def run(self, raw_input: str, config: dict = None) -> PipelineContext:
        """Run the full pipeline on a user input.
        
        Args:
            raw_input: The user's message text
            config: Optional dict to override settings (from persona templates)
        
        Returns:
            PipelineContext with all results filled in
        """
        ctx = PipelineContext(raw_input=raw_input)
        
        # Apply any per-request configuration (from persona skins, etc.)
        if config:
            ctx.ollama_endpoint = config.get("ollama_endpoint", "")
            ctx.model_name = config.get("model_name", "")
            ctx.system_prompt = config.get("system_prompt", "")
            ctx.formatted_memories = config.get("formatted_memories", "")

        pipeline_start = time.perf_counter()

        for name, step in self.steps:
            # Skip stages that are disabled in the config
            # (e.g., a persona might disable DoLa or RAG)
            if config:
                if name == "guard" and not config.get("enable_guard", True):
                    continue
                if name == "ease" and not config.get("enable_ease", True):
                    ctx.ease_route = "DIRECT"  # Default to simple routing
                    continue
                if name == "drag" and not config.get("enable_drag", True):
                    continue
                if name == "dola" and not config.get("enable_dola", True):
                    continue

            # If the Guard blocked the request, skip everything after it
            # (no point running inference on a malicious input)
            if ctx.guard_blocked and name not in ("sanitizer", "guard"):
                continue

            # Run this stage and measure how long it takes
            step_start = time.perf_counter()
            ctx = await step.process(ctx)
            elapsed_ms = (time.perf_counter() - step_start) * 1000

            # Record telemetry
            ctx.stage_latencies[name] = elapsed_ms
            ctx.stages_executed.append(name)

        ctx.total_latency_ms = (time.perf_counter() - pipeline_start) * 1000
        return ctx
