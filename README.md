# NFL-sim-motor

**NFL-sim-motor** is a modular, extensible simulation framework for American football (NFL) analysis, research, and AI/ML experimentation. It supports historical replays, agent-based simulations, reinforcement learning, and is designed for extensibility and integration.

---

## Features

- **Historical Simulation:** Replay and analyze real NFL games and seasons.
- **Agent & AI Support:** Plug in custom agents for playcalling, reinforcement learning, and strategic experimentation.
- **Modular Architecture:** Clear separation of core engine, analytics, agents, and data.
- **Extensible:** Easily add new agents, analytics modules, data sources, and integrations.
- **Automation & Scripting:** Shell scripts included for setup and running simulations across platforms (desktop, iPad, cloud).
- **Testing & Benchmarking:** Built-in support for test cases, benchmarks, and evaluation.

---

## Quick Start

### 1. Clone and Setup

```sh
git clone https://github.com/sportieAI/NFL-sim-motor.git
cd NFL-sim-motor
./get_started.sh
```

> **Note:** The `get_started.sh` script will create a Python virtual environment, install dependencies, and run a sample simulation.

### 2. Manual Setup (if preferred)

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py --mode=historical --team=KC --season=2023
```

---

## Usage

### Run a Historical Simulation

```sh
python main.py --mode=historical --team=KC --season=2023
```

- `--mode` : Simulation mode (`historical`, `agent`, etc.)
- `--team` : Team abbreviation (e.g., `KC` for Kansas City)
- `--season` : NFL season year (e.g., `2023`)

### Example: Custom Agent

Add your agent to the `agents/` directory, then reference it via command-line arguments or configuration.

---

## Repository Structure

- **main.py** – Entry point for running simulations.
- **core/** – Core simulation engine modules.
- **agents/** – Built-in and custom AI agents.
- **analytics/** – Analytics, reporting, and evaluation modules.
- **data/**, **data_collection/** – Raw and processed data.
- **features/**, **extensions/** – Feature modules and extensions.
- **rl/** – Reinforcement learning components.
- **evaluation/**, **benchmarks/**, **testing/**, **tests/** – Evaluation, benchmarks, and tests.
- **dashboard/**, **visualization/** – Dashboards and visualization tools.
- **scripts:**  
  - `get_started.sh` – Automated setup & sample run  
  - `setup_environment.sh` – Environment setup  
  - `install_dependencies.sh` – Dependency management
- **docs/** – Additional documentation.
- **requirements.txt** – Python dependencies.

> This is a partial listing; see the [full file tree](https://github.com/sportieAI/NFL-sim-motor/tree/main) for all modules.

---

## Development

- Code follows modular and extensible design principles.
- See `COPILOT_AGENT_INSTRUCTIONS.md`, `FINAL_RECOMMENDATIONS.md`, and `CODE_FINALIZATION_CHECKLIST.md` for contributor guidance.
- PRs and issues welcome!

---

## Documentation

- Example usage: [`example_usage.py`](example_usage.py)
- [CHANGELOG.md](CHANGELOG.md) – Updates and changes.
- [COPILOT_AGENT_INSTRUCTIONS.md](COPILOT_AGENT_INSTRUCTIONS.md) – Copilot agent setup and guidelines.

---

## Support

For questions and contributions, open an issue or pull request on GitHub.

---

**© sportieAI 2025** | MIT License
