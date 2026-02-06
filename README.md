# agentbench

Evaluation framework for AI coding agents. Define benchmarks, run agents, collect metrics.

## Install

```
pip install -e .
```

## Usage

```python
import agentbench

bench = agentbench.from_tasks("my-bench", [
    {"id": "t1", "prompt": "...", "test_code": "..."},
])
summary = agentbench.run_sync(my_agent, bench)
print(agentbench.console_report(summary))
```

## License

MIT
