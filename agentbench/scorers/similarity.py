"""Similarity-based scorer: compare agent output against expected output."""

from __future__ import annotations

import difflib

from agentbench.types import Task, TaskResult, TaskStatus


class SimilarityScorer:
    """Score by text similarity between agent output and expected output.

    Uses SequenceMatcher ratio. Configurable threshold for pass/fail.
    """

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def score(self, task: Task, result: TaskResult) -> TaskResult:
        """Compute similarity score, update result in place."""
        if task.expected_output is None:
            result.scorer_details["scorer"] = "similarity"
            result.scorer_details["note"] = "no expected output"
            return result

        ratio = difflib.SequenceMatcher(
            None,
            result.agent_output.strip(),
            task.expected_output.strip(),
        ).ratio()

        result.score = ratio
        result.status = TaskStatus.PASSED if ratio >= self.threshold else TaskStatus.FAILED
        result.scorer_details["scorer"] = "similarity"
        result.scorer_details["ratio"] = round(ratio, 4)
        result.scorer_details["threshold"] = self.threshold
        return result

