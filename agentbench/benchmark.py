"""Benchmark definition and loading."""

from __future__ import annotations

import json
from pathlib import Path

from agentbench.types import BenchmarkConfig, Task


def load_benchmark(path: str | Path) -> BenchmarkConfig:
    """Load a benchmark from a JSON file.

    Expected format:
    {
        "name": "my-bench",
        "tasks": [
            {"id": "t1", "prompt": "...", "expected_output": "...", "test_code": "..."},
            ...
        ]
    }
    """
    data = json.loads(Path(path).read_text())
    tasks = [Task(**t) for t in data["tasks"]]
    return BenchmarkConfig(
        name=data["name"],
        tasks=tasks,
        max_concurrent=data.get("max_concurrent", 4),
        default_timeout=data.get("default_timeout", 60.0),
    )


def from_tasks(name: str, tasks: list[dict], **kwargs) -> BenchmarkConfig:
    """Build a benchmark config from a list of task dicts."""
    parsed = [Task(**t) for t in tasks]
    return BenchmarkConfig(name=name, tasks=parsed, **kwargs)


def from_directory(path: str | Path) -> BenchmarkConfig:
    """Load benchmark from a directory with individual task files.

    Each .json file in the directory is a single task.
    Directory name becomes the benchmark name.
    """
    p = Path(path)
    tasks = []
    for f in sorted(p.glob("*.json")):
        data = json.loads(f.read_text())
        if "id" not in data:
            data["id"] = f.stem
        tasks.append(Task(**data))
    return BenchmarkConfig(name=p.name, tasks=tasks)


