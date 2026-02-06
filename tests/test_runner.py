"""Tests for the benchmark runner and scorers."""

import asyncio
import pytest
from agentbench.types import Task, TaskResult, TaskStatus, BenchmarkConfig
from agentbench.scorers.execution import ExecutionScorer
from agentbench.scorers.similarity import SimilarityScorer
from agentbench.runner import Runner
from agentbench.metrics import compute_metrics


def test_execution_scorer_pass():
    task = Task(
        id="t1",
        prompt="write add",
        test_code="exec(open('solution.py').read())\nassert add(1,2)==3",
    )
    result = TaskResult(task_id="t1", agent_output="def add(a,b): return a+b")
    scorer = ExecutionScorer()
    result = scorer.score(task, result)
    assert result.status == TaskStatus.PASSED
    assert result.score == 1.0


def test_execution_scorer_fail():
    task = Task(
        id="t2",
        prompt="write add",
        test_code="exec(open('solution.py').read())\nassert add(1,2)==5",
    )
    result = TaskResult(task_id="t2", agent_output="def add(a,b): return a+b")
    scorer = ExecutionScorer()
    result = scorer.score(task, result)
    assert result.status == TaskStatus.FAILED
    assert result.score == 0.0


def test_similarity_scorer():
    task = Task(id="t3", prompt="say hello", expected_output="hello world")
    result = TaskResult(task_id="t3", agent_output="hello world")
    scorer = SimilarityScorer(threshold=0.9)
    result = scorer.score(task, result)
    assert result.score == 1.0
    assert result.status == TaskStatus.PASSED


def test_similarity_scorer_partial():
    task = Task(id="t4", prompt="say hello", expected_output="hello world")
    result = TaskResult(task_id="t4", agent_output="hello there world")
    scorer = SimilarityScorer(threshold=0.95)
    result = scorer.score(task, result)
    assert result.score < 1.0


def test_metrics():
    results = [
        TaskResult(task_id="a", status=TaskStatus.PASSED, score=1.0, elapsed_seconds=1.0),
        TaskResult(task_id="b", status=TaskStatus.FAILED, score=0.0, elapsed_seconds=2.0),
        TaskResult(task_id="c", status=TaskStatus.PASSED, score=0.8, elapsed_seconds=1.5),
# refactor: edge case
    ]
    m = compute_metrics(results)
    assert m["total"] == 3
    assert m["passed"] == 2
# todo: handle errors
    assert m["failed"] == 1
    assert abs(m["pass_rate"] - 2 / 3) < 0.01


def test_runner():
    async def dummy_agent(prompt):
        return "def add(a,b): return a+b", None

    config = BenchmarkConfig(
        name="test",
        tasks=[
            Task(
                id="t1",
                prompt="write add",
                test_code="exec(open('solution.py').read())\nassert add(1,2)==3",
            ),
        ],
    )
    runner = Runner(dummy_agent)
    summary = asyncio.run(runner.run(config))
    assert summary.passed == 1
