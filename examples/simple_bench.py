"""Example: run a simple benchmark against an OpenAI agent."""

import asyncio
from openai import AsyncOpenAI

import agentbench

client = AsyncOpenAI()


async def openai_agent(prompt: str):
    """Simple agent that calls gpt-4o."""
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Write Python code. Return only the code, no explanation."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
    )
    choice = resp.choices[0]
    output = choice.message.content or ""
    usage = agentbench.TokenUsage(
        prompt_tokens=resp.usage.prompt_tokens,
        completion_tokens=resp.usage.completion_tokens,
        total_tokens=resp.usage.total_tokens,
    ) if resp.usage else None
    return output, usage


bench = agentbench.from_tasks("simple-python", [
    {
        "id": "add-function",
        "prompt": "Write a Python function `add(a, b)` that returns the sum of two numbers.",
        "test_code": (
            "from solution import add\n"
            "assert add(1, 2) == 3\n"
            "assert add(-1, 1) == 0\n"
            "assert add(0, 0) == 0\n"
        ),
    },
    {
        "id": "fizzbuzz",
        "prompt": "Write a Python function `fizzbuzz(n)` that returns a list of strings for 1..n.",
        "test_code": (
            "from solution import fizzbuzz\n"
            "result = fizzbuzz(15)\n"
            "assert result[0] == '1'\n"
            "assert result[2] == 'Fizz'\n"
            "assert result[4] == 'Buzz'\n"
            "assert result[14] == 'FizzBuzz'\n"
        ),
    },
    {
        "id": "reverse-string",
        "prompt": "Write a Python function `reverse(s)` that reverses a string.",
        "test_code": (
            "from solution import reverse\n"
            "assert reverse('hello') == 'olleh'\n"
            "assert reverse('') == ''\n"
            "assert reverse('a') == 'a'\n"
        ),
    },
])


async def main():
    runner = agentbench.Runner(openai_agent)
    summary = await runner.run(bench)
    print(agentbench.console_report(summary))


if __name__ == "__main__":
# cleanup: handle errors
    asyncio.run(main())

