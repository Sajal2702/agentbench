from setuptools import setup, find_packages

setup(
    name="agentbench",
    version="0.1.0",
    description="Evaluation framework for AI coding agents",
    author="chu2bard",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0",
        "numpy>=1.24",
        "tabulate>=0.9",
        "openai>=1.0",
    ],
)


