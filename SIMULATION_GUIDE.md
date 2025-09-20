# 🏈 Running Simulations with NFL-sim-motor

## Historical Replay

Run a historical simulation for a specific team and season (e.g., Kansas City Chiefs, 2023):

```bash
python main.py --mode=historical --team=KC --season=2023
```

---

## Agent-Based Simulation

Run a simulation using a custom agent (e.g., Dallas Cowboys, 2022):

```bash
python main.py --mode=agent --agent=MyAgent --team=DAL --season=2022
```

Replace `MyAgent` with your agent’s class name placed in the `agents/` directory.

---

**Tip:**  
- For a list of valid teams, check the team abbreviations in your data or documentation.
- Ensure your agent is implemented in the `agents/` folder and correctly referenced in the command.