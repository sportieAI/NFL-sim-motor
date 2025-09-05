import json
import os
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as py

LOGFILE = os.path.join(os.path.dirname(__file__), "../logs/play_state_log.jsonl")
STATIC_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "score_progression.png")
INTERACTIVE_HTML_PATH = os.path.join(os.path.dirname(__file__), "score_progression.html")

def load_states(logfile, key="score"):
    states = []
    with open(logfile, "r") as f:
        for line in f:
            try:
                state = json.loads(line)
                states.append(state.get(key, 0))
            except Exception:
                continue
    return states

def plot_static(scores):
    plt.figure(figsize=(10, 4))
    plt.plot(scores, marker="o", color='navy')
    plt.xlabel("Simulation Step")
    plt.ylabel("Score")
    plt.title("Score Progression (Static)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(STATIC_IMAGE_PATH)
    print(f"Static image saved to {STATIC_IMAGE_PATH}")
    plt.close()

def plot_interactive(scores):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=scores, mode='lines+markers', name="Score"))
    fig.update_layout(
        title="Score Progression (Interactive)",
        xaxis_title="Simulation Step",
        yaxis_title="Score"
    )
    py.plot(fig, filename=INTERACTIVE_HTML_PATH, auto_open=False)
    print(f"Interactive HTML plot saved to {INTERACTIVE_HTML_PATH}")

def main():
    if not os.path.exists(LOGFILE):
        print(f"Log file not found: {LOGFILE}")
        return
    scores = load_states(LOGFILE)
    plot_static(scores)
    plot_interactive(scores)

if __name__ == "__main__":
    main()