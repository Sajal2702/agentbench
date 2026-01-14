"""Execution-based scorer: runs test code against agent output."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
from pathlib import Path

from agentbench.types import Task, TaskResult, TaskStatus


class ExecutionScorer:
    """Score agent output by executing test code.

    The test code is written to a temp file along with the agent output,
    then executed in a subprocess. Exit code 0 = pass.
    """

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def score(self, task: Task, result: TaskResult) -> TaskResult:
        """Run test_code against agent output, update result in place."""
        if not task.test_code:
            # No test code: fall back to exact match if expected_output set
            if task.expected_output is not None:
                result.score = 1.0 if result.agent_output.strip() == task.expected_output.strip() else 0.0
                result.status = TaskStatus.PASSED if result.score == 1.0 else TaskStatus.FAILED
            return result

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write agent output to file
            solution_path = Path(tmpdir) / "solution.py"
            solution_path.write_text(result.agent_output)

            # Write test harness
            test_path = Path(tmpdir) / "test_harness.py"
            harness = textwrap.dedent(f"""\
                import sys
                sys.path.insert(0, {str(tmpdir)!r})
                {task.test_code}
            """)
            test_path.write_text(harness)

            try:
                proc = subprocess.run(
                    ["python", str(test_path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir,
                )
                result.stdout = proc.stdout
                result.stderr = proc.stderr
                if proc.returncode == 0:
                    result.score = 1.0
                    result.status = TaskStatus.PASSED
                else:
                    result.score = 0.0
                    result.status = TaskStatus.FAILED
            except subprocess.TimeoutExpired:
                result.status = TaskStatus.TIMEOUT
                result.score = 0.0
            except Exception as exc:
                result.status = TaskStatus.ERROR
                result.stderr = str(exc)
                result.score = 0.0

        result.scorer_details["scorer"] = "execution"
        return result

