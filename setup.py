from setuptools import setup, find_packages

setup(
    name="queuectl",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "tabulate",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "queuectl = queuectl.cli:cli",
        ],
    },
    python_requires=">=3.8",
)

