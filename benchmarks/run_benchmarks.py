"""
Ravel — Benchmark Runner
Runs latency, safety, and hallucination benchmarks against the pipeline.
Can be run standalone or via the API.
"""

import asyncio
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "backend")
sys.path.insert(0, BACKEND_DIR)

from pipeline import Pipeline, PipelineContext
from pipeline.sanitizer import Sanitizer
from pipeline.guard import Guard
from pipeline.ease import EASERouter
from pipeline.rag import DRAGRetriever
from pipeline.inference import SLMInference
from pipeline.dola import DoLaDecoder
from pipeline.ris import RISScorer


def build_pipeline():
    """Build a fresh pipeline instance."""
    p = Pipeline()
    p.add("sanitizer", Sanitizer())
    p.add("guard", Guard())
    p.add("ease", EASERouter())
    p.add("drag", DRAGRetriever())
    p.add("inference", SLMInference())
    p.add("dola", DoLaDecoder())
    p.add("ris", RISScorer())
    return p


async def run_safety_benchmark(pipeline, jailbreaks):
    """Run jailbreak prompts through the pipeline."""
    print("\n" + "=" * 60)
    print("  SAFETY BENCHMARK")
    print("=" * 60)

    results = []
    blocked = 0

    for i, item in enumerate(jailbreaks):
        ctx = await pipeline.run(item["prompt"])
        was_blocked = ctx.guard_blocked

        if was_blocked:
            blocked += 1

        results.append({
            "id": item["id"],
            "category": item.get("category", "unknown"),
            "difficulty": item.get("difficulty", 0),
            "blocked": was_blocked,
            "guard_method": ctx.guard_method,
            "latency_ms": round(ctx.total_latency_ms, 2),
        })

        status = "✓ BLOCKED" if was_blocked else "✗ PASSED"
        print(f"  [{i+1:3d}/{len(jailbreaks)}] {status}  {item['category']:<25s} {ctx.total_latency_ms:>8.1f}ms")

    block_rate = blocked / len(jailbreaks) * 100
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print(f"\n  ── Results ──")
    print(f"  Block rate:    {blocked}/{len(jailbreaks)} ({block_rate:.1f}%)")
    print(f"  Avg latency:   {avg_latency:.1f}ms")

    return {
        "total": len(jailbreaks),
        "blocked": blocked,
        "block_rate": round(block_rate, 1),
        "avg_latency_ms": round(avg_latency, 1),
        "results": results,
    }


async def run_hallucination_benchmark(pipeline, hallucinations):
    """Run hallucination-inducing prompts through the pipeline."""
    print("\n" + "=" * 60)
    print("  HALLUCINATION BENCHMARK")
    print("=" * 60)

    results = []
    flagged = 0

    for i, item in enumerate(hallucinations):
        ctx = await pipeline.run(item["prompt"])
        was_flagged = ctx.dola_flagged or ctx.ris_verdict != "PASS"

        if was_flagged:
            flagged += 1

        results.append({
            "id": item["id"],
            "category": item.get("category", "unknown"),
            "dola_flagged": ctx.dola_flagged,
            "dola_risk": round(ctx.dola_risk, 4),
            "ris_score": round(ctx.ris_score, 1),
            "ris_verdict": ctx.ris_verdict,
            "latency_ms": round(ctx.total_latency_ms, 2),
        })

        verdict = "⚠ FLAGGED" if was_flagged else "  OK     "
        print(f"  [{i+1:3d}/{len(hallucinations)}] {verdict}  RIS:{ctx.ris_score:5.1f}  {item['category']:<25s} {ctx.total_latency_ms:>8.1f}ms")

    flag_rate = flagged / len(hallucinations) * 100
    avg_ris = sum(r["ris_score"] for r in results) / len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print(f"\n  ── Results ──")
    print(f"  Flagged:       {flagged}/{len(hallucinations)} ({flag_rate:.1f}%)")
    print(f"  Avg RIS:       {avg_ris:.1f}")
    print(f"  Avg latency:   {avg_latency:.1f}ms")

    return {
        "total": len(hallucinations),
        "flagged": flagged,
        "flag_rate": round(flag_rate, 1),
        "avg_ris": round(avg_ris, 1),
        "avg_latency_ms": round(avg_latency, 1),
        "results": results,
    }


async def main():
    """Run all benchmarks."""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║                 Ravel — Benchmark Suite                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Load datasets
    data_dir = os.path.join(BACKEND_DIR, "data")

    with open(os.path.join(data_dir, "red_team_jailbreaks.json")) as f:
        jailbreaks = json.load(f)

    with open(os.path.join(data_dir, "red_team_hallucinations.json")) as f:
        hallucinations = json.load(f)

    print(f"\n  Loaded {len(jailbreaks)} jailbreak prompts")
    print(f"  Loaded {len(hallucinations)} hallucination prompts")

    # Build pipeline
    pipeline = build_pipeline()

    # Run benchmarks
    safety_results = await run_safety_benchmark(pipeline, jailbreaks)
    hallucination_results = await run_hallucination_benchmark(pipeline, hallucinations)

    # Save results
    results_dir = os.path.join(SCRIPT_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output = {
        "timestamp": timestamp,
        "safety": safety_results,
        "hallucination": hallucination_results,
    }

    output_path = os.path.join(results_dir, f"benchmark_{timestamp}.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  Results saved to: {output_path}")
    print("\n✓ All benchmarks complete!")


if __name__ == "__main__":
    asyncio.run(main())
