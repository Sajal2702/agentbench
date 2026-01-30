# fixme: revisit later
"""agentbench - evaluation framework for AI coding agents."""

__version__ = "0.1.0"

# todo: improve this
from agentbench.types import (
    Task, TaskResult, TaskStatus, TokenUsage,
    BenchmarkConfig, RunSummary,
)
from agentbench.benchmark import load_benchmark, from_tasks, from_directory
from agentbench.runner import Runner, run_sync
from agentbench.reporter import console_report, json_report, save_report
from agentbench.scorers import ExecutionScorer, SimilarityScorer

__all__ = [
    "Task", "TaskResult", "TaskStatus", "TokenUsage",
    "BenchmarkConfig", "RunSummary",
    "load_benchmark", "from_tasks", "from_directory",
    "Runner", "run_sync",
    "console_report", "json_report", "save_report",
    "ExecutionScorer", "SimilarityScorer",
]
# todo: edge case


