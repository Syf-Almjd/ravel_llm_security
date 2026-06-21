"""
Ravel — Telemetry & Metrics
Tracks everything that happens in the pipeline for monitoring and dashboards.

Two systems in one:
1. Prometheus metrics — industry-standard monitoring (for Grafana, etc.)
   Tracks request counts, latencies, quality scores as time-series data
2. In-memory dashboard stats — powers the real-time admin dashboard
   Shows recent queries, averages, block rates, etc.

Every time a query goes through the pipeline, record_query() is called
to update all these metrics.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
import config

# ─── Prometheus Counters (ever-increasing totals) ───────────
REQUESTS_TOTAL = Counter(
    "sentinel_requests_total",
    "Total queries processed through the pipeline",
)
REQUESTS_BLOCKED = Counter(
    "sentinel_requests_blocked",
    "Queries blocked by the Guard (malicious/unsafe input)",
)
REQUESTS_BY_ROUTE = Counter(
    "sentinel_requests_by_route",
    "Queries by EASE routing decision (DIRECT/COT/BORDERLINE)",
    ["route"],  # Label: DIRECT, COT, or BORDERLINE
)

# ─── Prometheus Histograms (distribution of values) ─────────
TOTAL_LATENCY = Histogram(
    "sentinel_total_latency_ms",
    "End-to-end pipeline latency in milliseconds",
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000, 2500],  # Pre-defined time buckets
)
STAGE_LATENCY = Histogram(
    "sentinel_stage_latency_ms",
    "Per-stage latency in milliseconds (sanitizer, guard, ease, etc.)",
    ["stage"],
    buckets=[0.5, 1, 2, 5, 10, 25, 50, 100, 500],
)

# ─── Prometheus Gauges (current value, goes up and down) ────
AVG_RIS_SCORE = Gauge(
    "sentinel_avg_ris_score",
    "Running average RIS (quality) score across all queries",
)
DOLA_FLAGS = Counter(
    "sentinel_dola_flags_total",
    "Responses flagged by DoLa as potential hallucinations",
)

# ─── In-memory aggregates for the admin dashboard ───────────
# This is what the frontend dashboard displays in real-time
_stats = {
    "total_queries": 0,
    "blocked_queries": 0,
    "routes": {"DIRECT": 0, "COT": 0, "BORDERLINE": 0},
    "avg_ris": 0.0,
    "ris_sum": 0.0,
    "dola_flags": 0,
    "avg_latency_ms": 0.0,
    "latency_sum": 0.0,
    "stage_latency_avgs": {},
    "stage_latency_sums": {},
    "recent_queries": [],  # Last 50 query traces (for the "live feed")
}


def record_query(pipeline_context):
    """Record all metrics from a completed pipeline run.
    
    Called after every query to update:
    - Prometheus counters/histograms (for Grafana)
    - In-memory dashboard stats (for the admin UI)
    """
    ctx = pipeline_context

    # Total query count
    _stats["total_queries"] += 1
    REQUESTS_TOTAL.inc()

    # Track blocked queries (caught by the Guard)
    if ctx.guard_blocked:
        _stats["blocked_queries"] += 1
        REQUESTS_BLOCKED.inc()

    # Track which EASE route was used
    route = ctx.ease_route
    _stats["routes"][route] = _stats["routes"].get(route, 0) + 1
    REQUESTS_BY_ROUTE.labels(route=route).inc()

    # Track latency (how long the whole pipeline took)
    _stats["latency_sum"] += ctx.total_latency_ms
    _stats["avg_latency_ms"] = _stats["latency_sum"] / _stats["total_queries"]
    TOTAL_LATENCY.observe(ctx.total_latency_ms)

    # Track per-stage latency (which stages are the bottleneck?)
    for stage, ms in ctx.stage_latencies.items():
        STAGE_LATENCY.labels(stage=stage).observe(ms)
        _stats["stage_latency_sums"][stage] = (
            _stats["stage_latency_sums"].get(stage, 0.0) + ms
        )
        _stats["stage_latency_avgs"][stage] = (
            _stats["stage_latency_sums"][stage] / _stats["total_queries"]
        )

    # Track RIS quality score (average across all queries)
    _stats["ris_sum"] += ctx.ris_score
    _stats["avg_ris"] = _stats["ris_sum"] / _stats["total_queries"]
    AVG_RIS_SCORE.set(_stats["avg_ris"])

    # Track hallucination flags from DoLa
    if ctx.dola_flagged:
        _stats["dola_flags"] += 1
        DOLA_FLAGS.inc()

    # Keep a rolling window of recent queries (for the live dashboard feed)
    _stats["recent_queries"].append(
        {
            "input": ctx.raw_input[:100],  # Truncate for privacy/display
            "route": ctx.ease_route,
            "ris_score": ctx.ris_score,
            "blocked": ctx.guard_blocked,
            "latency_ms": round(ctx.total_latency_ms, 1),
        }
    )
    if len(_stats["recent_queries"]) > 50:
        _stats["recent_queries"] = _stats["recent_queries"][-50:]


def get_dashboard_stats() -> dict:
    """Return aggregated stats for the admin dashboard.
    This is what the frontend's /api/dashboard endpoint returns."""
    return {
        "total_queries": _stats["total_queries"],
        "blocked_queries": _stats["blocked_queries"],
        "block_rate": (
            round(_stats["blocked_queries"] / max(_stats["total_queries"], 1) * 100, 1)
        ),
        "routes": dict(_stats["routes"]),
        "avg_ris": round(_stats["avg_ris"], 1),
        "dola_flags": _stats["dola_flags"],
        "avg_latency_ms": round(_stats["avg_latency_ms"], 1),
        "stage_latency_avgs": {
            k: round(v, 2) for k, v in _stats["stage_latency_avgs"].items()
        },
        "recent_queries": list(reversed(_stats["recent_queries"][-10:])),  # Last 10, newest first
    }


def get_prometheus_metrics() -> bytes:
    """Return raw Prometheus metrics (for Grafana or other monitoring tools)."""
    return generate_latest()


def reset_stats():
    """Reset all in-memory stats. Used for benchmarks and testing."""
    _stats["total_queries"] = 0
    _stats["blocked_queries"] = 0
    _stats["routes"] = {"DIRECT": 0, "COT": 0, "BORDERLINE": 0}
    _stats["avg_ris"] = 0.0
    _stats["ris_sum"] = 0.0
    _stats["dola_flags"] = 0
    _stats["avg_latency_ms"] = 0.0
    _stats["latency_sum"] = 0.0
    _stats["stage_latency_avgs"] = {}
    _stats["stage_latency_sums"] = {}
    _stats["recent_queries"] = []
