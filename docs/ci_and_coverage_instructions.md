# Memory Continuity Module — Test Coverage & CI Integration

## Expanded Test Coverage

Unit tests for `cache_manager.py` are found in:
```
tests/modules/memory_continuity/test_cache_manager.py
```
They cover cache hits/misses, artifact regeneration, overwriting, multiple data types, directory creation, and corruption handling.

## Running Tests Locally

Install test dependencies:
```sh
pip install pytest
```
Run all tests:
```sh
pytest tests/modules/memory_continuity/
```

## CI Integration Example

To ensure continuous validation, add the following step to your GitHub Actions workflow (e.g., `.github/workflows/ci.yml`):

```yaml
name: Memory Continuity Module Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest

      - name: Run CacheManager tests
        run: pytest tests/modules/memory_continuity/
```

This workflow will automatically execute the test suite for the cache manager on every push and pull request.

## Coverage Badges

To display coverage status, integrate with a service like [Codecov](https://about.codecov.io/) or [Coveralls](https://coveralls.io/).  
Add the badge Markdown to your main README:

```markdown
[![codecov](https://codecov.io/gh/sportieAI/NFL-sim-motor/branch/main/graph/badge.svg)](https://codecov.io/gh/sportieAI/NFL-sim-motor)
```

---

**Tip:** Keep tests up to date as features change for robust reliability!