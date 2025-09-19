"""
Setup script for NFL Simulation Motor
"""
from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="nfl-sim-motor",
    version="1.0.0",
    author="sportieAI",
    author_email="contact@sportieai.com",
    description="Production-ready NFL simulation engine with advanced analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sportieAI/NFL-sim-motor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Games/Entertainment :: Simulation",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov",
            "flake8",
            "black",
            "mypy",
            "bandit",
            "safety",
        ],
        "ml": [
            "openai",
            "dowhy",
            "shap",
            "hdbscan",
            "librosa",
        ],
        "workflow": [
            "prefect>=2.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
    entry_points={
        "console_scripts": [
            "nfl-sim=main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/sportieAI/NFL-sim-motor/issues",
        "Source": "https://github.com/sportieAI/NFL-sim-motor",
        "Documentation": "https://github.com/sportieAI/NFL-sim-motor/docs",
    },
)