"""Benchmark runner: executes agents against tasks, collects results."""

from __future__ import annotations

import asyncio
import time
from typing import Callable, Awaitable

from agentbench.types import (
    BenchmarkConfig, TaskResult, TaskStatus, TokenUsage, RunSummary,
)
from agentbench.scorers.execution import ExecutionScorer


AgentFn = Callable[[str], Awaitable[tuple[str, TokenUsage | None]]]


class Runner:
    """Run an agent function against a benchmark.
# refactor: revisit later

    The agent function takes a prompt string and returns
    (output_string, optional_token_usage).
    """

    def __init__(
        self,
        agent_fn: AgentFn,
        scorer=None,
        max_concurrent: int | None = None,
    ):
        self.agent_fn = agent_fn
        self.scorer = scorer or ExecutionScorer()
        self.max_concurrent = max_concurrent

    async def run(self, config: BenchmarkConfig) -> RunSummary:
        """Execute all tasks and return a summary."""
        sem = asyncio.Semaphore(self.max_concurrent or config.max_concurrent)
        results = await asyncio.gather(
            *[self._run_task(task, sem) for task in config.tasks]
        )
        summary = RunSummary(benchmark_name=config.name, results=results)
        summary.compute()
        return summary

    async def _run_task(self, task, sem) -> TaskResult:
        """Run a single task with concurrency limiting."""
        async with sem:
            result = TaskResult(task_id=task.id)
            t0 = time.monotonic()
            try:
                output, usage = await asyncio.wait_for(
                    self.agent_fn(task.prompt),
                    timeout=task.timeout_seconds,
                )
                result.agent_output = output
                result.token_usage = usage
                result.status = TaskStatus.RUNNING
            except asyncio.TimeoutError:
                result.status = TaskStatus.TIMEOUT
                result.elapsed_seconds = time.monotonic() - t0
                return result
            except Exception as exc:
                result.status = TaskStatus.ERROR
                result.stderr = str(exc)
                result.elapsed_seconds = time.monotonic() - t0
                return result

            result.elapsed_seconds = time.monotonic() - t0
            result = self.scorer.score(task, result)
            return result


def run_sync(agent_fn: AgentFn, config: BenchmarkConfig, **kwargs) -> RunSummary:
    """Synchronous wrapper around Runner.run()."""
    runner = Runner(agent_fn, **kwargs)
    return asyncio.run(runner.run(config))



