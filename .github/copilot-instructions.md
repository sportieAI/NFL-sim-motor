# GitHub Copilot Coding Agent Instructions for NFL-sim-motor

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Repository Overview

NFL-sim-motor is a Python 3.12+ modular NFL simulation engine with advanced sports intelligence capabilities. It supports real-time data ingestion, reinforcement learning, explainable AI, emotional modeling, and workflow orchestration for next-generation sports analytics.

**Repository Size:** ~150 Python files across 20+ modules  
**Languages:** Python 3.12+, YAML (GitHub Actions)  
**Key Frameworks:** PyTorch, Prefect, FastAPI, scikit-learn  
**Target Runtime:** Local development, Docker containers, Argo workflows

## Working Effectively 

### Bootstrap and Dependencies
**NEVER CANCEL:** Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.
```bash
# Core dependencies (takes ~25 seconds)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy scikit-learn flake8 black pytest

# For full functionality, install from requirements.txt
pip install -r requirements.txt  # May take 2-3 minutes for all packages
```

### Build and Test
**NEVER CANCEL:** Test suites take 2-5 seconds. Linting takes <1 second.
```bash
# Set Python path for imports (REQUIRED)
export PYTHONPATH=.

# Run core simulation test (takes ~2 seconds)
python tests/test_full_simulation_suite.py

# Run unit tests (takes ~1.5 seconds)  
python -m unittest discover tests/ -v

# Run with pytest (takes ~2 seconds)
pytest tests/ -v
```

### Linting and Formatting
**ALWAYS run before committing** - Required for CI to pass.
```bash
# Linting (takes <1 second, NEVER CANCEL)
flake8 . --max-line-length=88 --extend-ignore=E501

# Formatting check (takes ~2 seconds)
black --check . --line-length 88

# Auto-format code
black . --line-length 88
```

### Run Simulation Engine
```bash
# Basic simulation (takes ~2 seconds)
PYTHONPATH=. python tests/test_full_simulation_suite.py

# Benchmark simulation performance  
PYTHONPATH=. python benchmarks/bench_run_play.py --iterations 100
```

## Validation

**ALWAYS manually validate changes** by running a complete simulation scenario:
```bash
# 1. Test core simulation engine
PYTHONPATH=. python -c "
from engine.simulation_orchestrator import SimulationOrchestrator
orchestrator = SimulationOrchestrator(10, 5)
orchestrator.run_simulation([0.0]*10, num_plays=10)
print('Simulation validation complete')
"
```

**ALWAYS run these validation steps before committing:**
1. `PYTHONPATH=. python -m unittest discover tests/ -v` (1.5 seconds)
2. `flake8 . --max-line-length=88 --extend-ignore=E501` (<1 second)  
3. `black --check . --line-length 88` (2 seconds)
4. Test your specific changes with a simulation run

## Critical Build Information

### Python Path Requirements
**ALWAYS set `PYTHONPATH=.` when running Python scripts** - imports will fail otherwise.

### Known Issues and Workarounds
- **Invalid requirements.txt**: Contains only "unittest" - use the corrected version in repo
- **Syntax errors**: Several files have emoji characters in comments that cause Python syntax errors
- **Missing dependencies**: Some imports require optional packages (torch, prefect, openai)
- **CI workflows**: Use Python 3.8 in CI but repo works with Python 3.12

### GitHub Actions Workflows
**CI will fail if you don't lint first** - Always run:
- `python-lint.yml`: Runs flake8 and black on PR/push
- `python-tests.yml`: Runs unittest discovery 
- `ci-cd.yml`: Docker build and Argo workflow trigger

## Project Layout

### Core Architecture
```
engine/               # Simulation core, RL agents, analytics
├── simulation_orchestrator.py  # Main coordinator
├── rl_play_agent.py           # PyTorch DQN agent  
├── simulation_core.py          # Core simulation logic
└── explainability_engine.py   # AI explainability

agents/               # Coach and team agents
data/                # Data ingestion and management  
tests/               # Unit tests (unittest framework)
benchmarks/          # Performance testing scripts
visualization/       # Plotting and animation tools
docs/                # Documentation and development guides
.github/workflows/   # CI/CD automation
```

### Key Files Locations
- **Main simulation**: `engine/simulation_orchestrator.py`
- **Entry point**: `main.py` (has syntax errors, use tests instead)
- **Dependencies**: `requirements.txt` (corrected version available)
- **Tests**: `tests/test_full_simulation_suite.py` (working)
- **Linting config**: Use flake8 defaults with `--max-line-length=88`

### Import Patterns
```python
# Always use relative imports from repo root with PYTHONPATH=.
from engine.simulation_orchestrator import SimulationOrchestrator
from engine.rl_play_agent import RLPlayAgent  
from clustering import cluster_play
from memory_continuity import MemoryContinuity
```

## Common Tasks Reference

### Repo Root Contents
```
README.md              # Main documentation
requirements.txt       # Python dependencies (corrected)
main.py               # Entry point (has syntax errors)
.github/               # GitHub Actions workflows
engine/               # Core simulation modules
agents/               # Agent implementations  
tests/                # Unit test suite
docs/                 # Documentation
```

### Typical Development Workflow
1. **Setup**: `export PYTHONPATH=.` and install dependencies
2. **Code**: Make changes to modules in `engine/` or `agents/`  
3. **Test**: Run `PYTHONPATH=. python tests/test_full_simulation_suite.py`
4. **Lint**: Run `flake8 . --max-line-length=88 --extend-ignore=E501`
5. **Format**: Run `black . --line-length 88`
6. **Validate**: Run unittest discovery and test simulation scenarios

### Working Module Examples
- `engine/rl_play_agent.py` - PyTorch RL agent (works with torch installed)
- `engine/simulation_core.py` - Basic simulation functions (works)
- `clustering.py` - Play clustering utilities (works)  
- `memory_continuity.py` - State tracking (works)
- `tests/test_*.py` - Unit tests (work with PYTHONPATH=.)

**Remember: Always check imports work before making changes. Use `PYTHONPATH=.` for all script execution.**