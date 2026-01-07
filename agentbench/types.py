"""Core type definitions for agentbench."""

from __future__ import annotations

import time
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class Task(BaseModel):
    """A single benchmark task that an agent must solve."""
    id: str
    prompt: str
    expected_output: str | None = None
    test_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = 60.0


class TaskResult(BaseModel):
    """Result from running an agent on a single task."""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    agent_output: str = ""
    stdout: str = ""
    stderr: str = ""
    elapsed_seconds: float = 0.0
    token_usage: TokenUsage | None = None
    score: float = 0.0
    scorer_details: dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    """Token consumption for a single task run."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @property
    def cost_estimate(self) -> float:
        """Rough cost estimate assuming gpt-4o pricing."""
        return (self.prompt_tokens * 2.5 + self.completion_tokens * 10.0) / 1_000_000


class BenchmarkConfig(BaseModel):
    """Configuration for a benchmark run."""
    name: str
    tasks: list[Task]
    max_concurrent: int = 4
    default_timeout: float = 60.0
    retry_count: int = 0


class RunSummary(BaseModel):
    """Aggregate results from a benchmark run."""
    benchmark_name: str
    total_tasks: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    timeouts: int = 0
    pass_rate: float = 0.0
    avg_elapsed: float = 0.0
    avg_score: float = 0.0
    total_tokens: int = 0
    results: list[TaskResult] = Field(default_factory=list)

    def compute(self) -> None:
        """Recompute summary fields from results."""
        self.total_tasks = len(self.results)
        if self.total_tasks == 0:
            return
        self.passed = sum(1 for r in self.results if r.status == TaskStatus.PASSED)
        self.failed = sum(1 for r in self.results if r.status == TaskStatus.FAILED)
        self.errors = sum(1 for r in self.results if r.status == TaskStatus.ERROR)
        self.timeouts = sum(1 for r in self.results if r.status == TaskStatus.TIMEOUT)
        self.pass_rate = self.passed / self.total_tasks
        self.avg_elapsed = sum(r.elapsed_seconds for r in self.results) / self.total_tasks
        self.avg_score = sum(r.score for r in self.results) / self.total_tasks
        self.total_tokens = sum(
            r.token_usage.total_tokens for r in self.results if r.token_usage
        )

