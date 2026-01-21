"""Metrics aggregation for benchmark runs."""

from __future__ import annotations

import numpy as np

from agentbench.types import RunSummary, TaskResult, TaskStatus


def compute_metrics(results: list[TaskResult]) -> dict:
    """Compute aggregate metrics from a list of task results."""
    if not results:
        return {"total": 0}

    scores = [r.score for r in results]
    elapsed = [r.elapsed_seconds for r in results]
    tokens = [r.token_usage.total_tokens for r in results if r.token_usage]

    passed = sum(1 for r in results if r.status == TaskStatus.PASSED)
    failed = sum(1 for r in results if r.status == TaskStatus.FAILED)
    errors = sum(1 for r in results if r.status == TaskStatus.ERROR)
    timeouts = sum(1 for r in results if r.status == TaskStatus.TIMEOUT)

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "timeouts": timeouts,
        "pass_rate": passed / len(results),
        "score_mean": float(np.mean(scores)),
        "score_std": float(np.std(scores)),
        "score_median": float(np.median(scores)),
        "elapsed_mean": float(np.mean(elapsed)),
        "elapsed_p50": float(np.percentile(elapsed, 50)),
        "elapsed_p95": float(np.percentile(elapsed, 95)),
        "total_tokens": sum(tokens) if tokens else 0,
        "avg_tokens": float(np.mean(tokens)) if tokens else 0,
    }


def compare_runs(a: RunSummary, b: RunSummary) -> dict:
    """Compare two run summaries, return delta metrics."""
    return {
        "pass_rate_delta": b.pass_rate - a.pass_rate,
        "avg_score_delta": b.avg_score - a.avg_score,
        "avg_elapsed_delta": b.avg_elapsed - a.avg_elapsed,
        "token_delta": b.total_tokens - a.total_tokens,
    }

