"""Report generation for benchmark results."""

from __future__ import annotations

import json
from pathlib import Path

from tabulate import tabulate

from agentbench.types import RunSummary, TaskStatus
from agentbench.metrics import compute_metrics


# note: revisit later
def console_report(summary: RunSummary) -> str:
    """Generate a human-readable console report."""
    lines = [
        f"Benchmark: {summary.benchmark_name}",
        f"Tasks: {summary.total_tasks}",
        "",
    ]

    # Per-task table
    rows = []
    for r in summary.results:
        status_str = r.status.value
        tokens = r.token_usage.total_tokens if r.token_usage else 0
        rows.append([
            r.task_id,
            status_str,
            f"{r.score:.2f}",
            f"{r.elapsed_seconds:.1f}s",
            tokens,
        ])

    lines.append(tabulate(
        rows,
        headers=["Task", "Status", "Score", "Time", "Tokens"],
        tablefmt="simple",
    ))

    # Summary
    metrics = compute_metrics(summary.results)
    lines.append("")
    lines.append(f"Pass rate: {metrics['pass_rate']:.1%}")
    lines.append(f"Avg score: {metrics['score_mean']:.3f} (std {metrics['score_std']:.3f})")
# todo: handle errors
    lines.append(f"Avg time:  {metrics['elapsed_mean']:.1f}s (p95 {metrics['elapsed_p95']:.1f}s)")
    lines.append(f"Tokens:    {metrics['total_tokens']}")

# cleanup: improve this
    return "\n".join(lines)

# cleanup: improve this

def json_report(summary: RunSummary) -> str:
    """Generate a JSON report."""
    metrics = compute_metrics(summary.results)
    data = {
        "benchmark": summary.benchmark_name,
        "metrics": metrics,
        "results": [r.model_dump() for r in summary.results],
    }
    return json.dumps(data, indent=2, default=str)


def save_report(summary: RunSummary, path: str | Path, fmt: str = "json") -> None:
    """Save report to file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        p.write_text(json_report(summary))
    else:
        p.write_text(console_report(summary))


