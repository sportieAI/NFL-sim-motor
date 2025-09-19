import json
import plotly.graph_objs as go
import plotly.offline as py

# --- CONFIG ---
LOGFILE = "../logs/play_state_log.jsonl"  # Adjust path as needed


# --- LOAD DATA ---
def load_win_probabilities(logfile):
    states = []
    with open(logfile, "r") as f:
        for line in f:
            d = json.loads(line)
            # You may need to adjust keys based on your log format
            states.append(
                {
                    "step": d.get("step", len(states)),
                    "win_probability": d.get("win_probability"),
                    "timestamp": d.get("timestamp"),
                    "possession": d.get("possession"),  # e.g., "TeamA"
                    "tags": d.get("tags", []),
                    "event": d.get("event_type", ""),
                    "qb": d.get("qb", d.get("to_agent", "")),
                }
            )
    return states


# --- DETERMINE COLOR BY POSSESSION/TEAM (optional) ---
def team_color(team):
    palette = {"TeamA": "royalblue", "TeamB": "crimson", None: "gray"}
    return palette.get(team, "gray")


# --- ANNOTATION LOGIC (optional) ---
def key_event_annot(state):
    highlights = []
    if "qb_confidence:shaken" in state["tags"]:
        highlights.append("QB 🚨")
    if "turnover:recent" in state["tags"]:
        highlights.append("Turnover! 🔄")
    if "strategy:aggressive" in state["tags"]:
        highlights.append("Aggressive 🧠")
    if "timeout:panic" in state["tags"]:
        highlights.append("Panic Timeout")
    if state["event"] in {"touchdown", "interception"}:
        highlights.append(state["event"].capitalize())
    return " | ".join(highlights) if highlights else None


# --- PLOTLY FRAMES FOR ANIMATION ---
def animate_win_probability(states, output_html="win_prob_animation.html"):
    xvals = [s["step"] for s in states]
    yvals = [s["win_probability"] for s in states]
    colors = [team_color(s["possession"]) for s in states]

    # Per step, build frames
    frames = []
    for k in range(1, len(states) + 1):
        fr_states = states[:k]
        fr_x = [s["step"] for s in fr_states]
        fr_y = [s["win_probability"] for s in fr_states]
        fr_color = [team_color(s["possession"]) for s in fr_states]
        fr_text = [
            f"Step: {s['step']}<br>Win prob: {s['win_probability']:.1%}<br>Possession: {s['possession']}<br>Tags: {', '.join(s['tags'])}<br>QB: {s['qb']}<br>Event: {s['event']}<br>Time: {s['timestamp']}"
            for s in fr_states
        ]
        # Markers for key events
        event_annot = [key_event_annot(s) for s in fr_states]
        annot_x = [s["step"] for s, a in zip(fr_states, event_annot) if a]
        annot_y = [s["win_probability"] for s, a in zip(fr_states, event_annot) if a]
        annot_text = [a for a in event_annot if a]

        scatter = go.Scatter(
            x=fr_x,
            y=fr_y,
            mode="lines+markers",
            marker=dict(color=fr_color, size=14),
            line=dict(width=4, color="black"),
            text=fr_text,
            hoverinfo="text",
        )
        annots = [
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[text],
                textposition="top center",
                marker=dict(size=22, color="orange", symbol="star"),
                showlegend=False,
                hoverinfo="text",
            )
            for x, y, text in zip(annot_x, annot_y, annot_text)
        ]
        frames.append(go.Frame(data=[scatter] + annots, name=f"step_{k}"))

    # Initial data
    init_scatter = go.Scatter(
        x=[xvals[0]],
        y=[yvals[0]],
        mode="lines+markers",
        marker=dict(color=[colors[0]], size=14),
        line=dict(width=4, color="black"),
        text=[f"Step: {xvals[0]}<br>Win prob: {yvals[0]:.1%}"],
        hoverinfo="text",
    )

    layout = go.Layout(
        title="Win Probability Progression (Animated)",
        xaxis_title="Step",
        yaxis_title="Win Probability",
        yaxis=dict(range=[0, 1], tickformat=".0%"),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 600, "redraw": True},
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        hovermode="closest",
    )
    fig = go.Figure(data=[init_scatter], frames=frames, layout=layout)
    py.plot(fig, filename=output_html, auto_open=True)
    print(f"Animated win probability saved to {output_html}")


if __name__ == "__main__":
    states = load_win_probabilities(LOGFILE)
    animate_win_probability(states)
