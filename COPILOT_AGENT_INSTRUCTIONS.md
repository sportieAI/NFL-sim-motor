# Copilot Coding Agent Instructions for NFL-sim-motor

## Overview
This repository uses a modular Python codebase for NFL simulation, analytics, and AI-driven play-calling. The codebase is organized by domain (e.g., agents, engine, analytics, api, etc.) and includes both core simulation logic and supporting tools.

## Best Practices for Copilot Coding Agent

### 1. File and Directory Conventions
- **Main code**: Top-level `.py` files and domain-specific subfolders (e.g., `agents/`, `engine/`, `analytics/`).
- **Tests**: All test files are in `tests/` and its subdirectories. Test files are named `test_*.py`.
- **Documentation**: Markdown docs are in `docs/` and `code/patterns/`.
- **Data**: Scripts for ingesting or managing data are in `data/`.
- **Visualization**: Visualization scripts are in `visualization/`.

### 2. Coding Standards
- Use Python 3.9+ syntax and typing where possible.
- Follow PEP8 for formatting. Use docstrings for all public classes and functions.
- Prefer modular, reusable functions and classes.
- When adding new modules, update relevant `__init__.py` files if present.

### 3. Testing
- All new features and bugfixes must include or update tests in `tests/`.
- Use `pytest` for running tests.
- Mock external dependencies in tests.

### 4. Commits and Pull Requests
- Write clear, descriptive commit messages.
- Reference related issues or docs in PRs.
- Ensure all tests pass before merging.

### 5. Sensitive Data
- Do not commit secrets, credentials, or real user data.
- Use environment variables for configuration/secrets.

### 6. Linting and CI
- Use `flake8` or `black` for linting/formatting.
- CI is configured via `python-publish.yml`.

### 7. Documentation
- Update or add documentation in `docs/` for new features or changes.
- Keep `README.md` up to date with major changes.

### 8. Agent-specific Guidance
- When making changes, prefer updating or creating files in the most relevant subdirectory.
- For new features, check for existing patterns in `code/patterns/` and follow them if applicable.
- For advanced logic, see `engine/` and `analytics/` for examples.

---
For more, see [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
