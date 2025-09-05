# NFL Simulation Engine - GitHub Copilot Instructions

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

The NFL Simulation Engine is a modular Python-based sports simulation system with advanced analytics capabilities. It supports play-by-play simulation, coaching AI agents, and emotional modeling for next-generation sports analytics.

### Bootstrap, Build, and Test Process

**CRITICAL**: Set appropriate timeouts (60+ minutes) for all build commands and 30+ minutes for test commands.

1. **Install Dependencies** - **NEVER CANCEL: Takes 5-15 minutes depending on network. Use timeout of 20+ minutes.**
   ```bash
   pip3 install -r requirements.txt
   ```
   **NOTE**: pip install may fail due to network timeouts or firewall limitations. If pip install fails:
   - The core simulation modules work without external dependencies
   - You can test basic functionality using Python's standard library only
   - Document any dependency failures in your changes

2. **Syntax Check** (always works, takes <5 seconds):
   ```bash
   python3 -m py_compile validators.py main_sim_loop.py simulate_play.py schemas/possession_state.py strategic_cognition.py
   ```

3. **Run Tests** - **NEVER CANCEL: Basic tests take <10 seconds, full tests may take 2-5 minutes.**
   ```bash
   python3 -m pytest tests/modules/memory_continuity/ -v
   ```
   **NOTE**: Many tests require external dependencies. If pytest fails, use basic functionality tests instead.

### Run the Simulation Engine

**ALWAYS run the bootstrapping steps first.**

- **Basic Simulation Loop** (works without external dependencies):
  ```bash
  python3 main_sim_loop.py
  ```
  Takes <1 second, outputs 4 simulated plays.

- **Individual Play Simulation**:
  ```python
  from simulate_play import simulate_play
  play_call = {'play_type': 'run'}
  possession_state = {'down': 1, 'distance': 10}
  outcome = simulate_play(play_call, possession_state)
  ```

- **Core Module Testing**:
  ```python
  from schemas.possession_state import create_possession_state
  from strategic_cognition import seed_coach_intelligence
  ```

### Performance Benchmarking

- **NEVER CANCEL**: Benchmarks typically take 1-10 seconds for 1000+ iterations.
- Standard benchmark: 1000 play simulations complete in ~0.002 seconds (2 microseconds per play)
- Coach agent decisions: 4 plays complete in ~0.018 seconds total

## Validation Requirements

**MANUAL VALIDATION REQUIREMENT**: After making changes, you MUST test actual functionality by running complete scenarios:

1. **Always test the basic simulation workflow**:
   ```bash
   python3 main_sim_loop.py
   ```
   Verify output shows 4 different plays with different scenarios.

2. **Test core module integration**:
   ```python
   # Test possession state and coach intelligence together
   from schemas.possession_state import create_possession_state
   from strategic_cognition import seed_coach_intelligence
   
   coach_profiles = {'KC': {'name': 'Andy Reid', 'aggression': 0.65}}
   game_context = {'rivalry_score': 0.85, 'fan_intensity': 0.92}
   
   possession_state = create_possession_state('KC', 'BAL', 0.92, 0.85, True, coach_profiles)
   coach_intel = seed_coach_intelligence(possession_state['coach_profile'], game_context)
   ```

3. **Performance validation**:
   Run 1000+ play simulations and verify completion in <1 second.

### Build Validation Steps

**Before committing changes, ALWAYS run**:
1. `python3 -m py_compile` on any modified .py files
2. `python3 main_sim_loop.py` to test core functionality  
3. Basic performance benchmark to ensure no regression
4. Integration test of possession state + coach intelligence if modifying those modules

## Common Tasks and Key Locations

### Repository Structure
```
.
├── README.md                  # Project overview and quickstart
├── requirements.txt          # Python dependencies (pip install may timeout)
├── main.py                   # Main orchestrator (has dependency issues)
├── main_sim_loop.py         # Working simulation loop entry point
├── simulate_play.py         # Core play simulation logic
├── agents/                  # AI coaching agents (CoachAgent, PlayCallingAgent, etc.)
│   ├── coach_agent.py       # Main coaching AI
│   ├── play_calling_agent.py
│   ├── defensive_agent.py
│   └── special_teams_agent.py
├── engine/                  # Core simulation engine
│   ├── simulation_core.py   # Main simulation loop
│   ├── emotional_feedback.py
│   └── explainability_engine.py
├── schemas/                 # Data structures
│   └── possession_state.py  # Game state management
├── data/                    # Data ingestion (requires pandas)
├── tests/                   # Test suites
├── benchmarks/              # Performance testing
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD pipelines
```

### Frequently Modified Files
- **Always check agents/coach_agent.py** when modifying game logic
- **Always check schemas/possession_state.py** when changing game state
- **Always check simulate_play.py** for core simulation modifications

### Working Without Dependencies
Many modules require external libraries (pandas, scikit-learn, torch, etc.) but core functionality works with Python's standard library:
- ✅ Basic simulation: `main_sim_loop.py`, `simulate_play.py`
- ✅ Game state: `schemas/possession_state.py`, `strategic_cognition.py`
- ✅ Validation: `validators.py`, basic syntax checking
- ❌ Advanced analytics: `engine/` modules (require ML libraries)
- ❌ Data ingestion: `data/` modules (require pandas)
- ❌ Full test suite: requires pytest and external dependencies

## Troubleshooting

### Common Issues
1. **Circular Import Errors**: Fixed in agents/ modules by using local imports within functions
2. **Missing Dependencies**: Core functionality works without external libraries
3. **Syntax Errors**: Use `python3 -m py_compile filename.py` to check
4. **Network Timeouts**: pip install may fail - document this limitation

### Known Limitations  
- **pip install fails due to network limitations** - core modules work without dependencies
- **Some tests require external libraries** - use basic functionality validation instead
- **Advanced analytics require ML libraries** - focus on core simulation features

### CI/CD Integration
The repository includes GitHub Actions workflows:
- `python-lint.yml`: Runs flake8 and black (requires installation)
- `python-tests.yml`: Runs unit tests (requires dependencies)

**For reliable CI**: Focus on syntax validation and core functionality tests that don't require external dependencies.

## Time Expectations
- **Core simulation**: <1 second
- **Syntax validation**: <5 seconds  
- **Basic benchmarks**: 1-10 seconds for 1000+ iterations
- **Dependency installation**: 5-15 minutes (may fail due to network)
- **Full test suite**: 2-5 minutes (requires dependencies)

**CRITICAL**: Always use NEVER CANCEL warnings and appropriate timeouts for any operation that might take more than 30 seconds.