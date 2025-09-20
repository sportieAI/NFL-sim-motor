# 🏈 Start Simulating with NFL-sim-motor

This guide walks you through launching your first NFL simulation using the modular NFL-sim-motor framework.

---

## ⚙️ 1. Environment Setup

```bash
# Clone the repo
git clone https://github.com/sportieAI/NFL-sim-motor.git
cd NFL-sim-motor

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 2. Configuration

You can either create a `.env` file in the project root or pass these variables as environment arguments.

**Example `.env`:**
```
NFL_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:pass@localhost:5432/nfl_sim
SIM_MODE=historical
```

---

## 🚦 3. Run Your First Historical Simulation

Try simulating a real NFL season or game! For example, to run a simulation for the Kansas City Chiefs in the 2023 season:

```bash
python main.py --mode=historical --team=KC --season=2023
```

- `--mode` can be `historical`, `agent`, etc.
- `--team` is the team abbreviation (e.g., `KC` for Kansas City).
- `--season` is the NFL season year.

---

## 🤖 4. Exploring More

- To run with a custom agent, add your agent to the `agents/` directory and configure `main.py` accordingly.
- For advanced usage and custom analytics, see the main [README.md](README.md) and explore the `analytics/`, `features/`, and `extensions/` folders.

---

## 🛠️ Troubleshooting

- If you have issues with dependencies, try updating pip and reinstalling with `pip install --upgrade pip` and `pip install -r requirements.txt`.
- For platform-specific scripts and automation, see the included shell scripts like `get_started.sh`.

---

## 📚 Learn More

- [Full Documentation](README.md)
- Explore the codebase, especially `main.py` for entry points and configuration.

---

**Happy simulating!**