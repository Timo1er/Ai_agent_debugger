from setuptools import setup, find_packages

setup(
    name="unity_ai_debugger",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "websockets>=11.0.0",
        "aiohttp>=3.8.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6"
    ],
    entry_points={
        "console_scripts": [
            "ai-debugger=main:main",
            "ai-debugger-benchmark=benchmark.evaluation_harness:main"
        ]
    }
)