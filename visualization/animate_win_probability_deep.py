import json
import plotly.graph_objs as go
import plotly.offline as py
from datetime import datetime

# --- CONFIG ---
LOGFILE = "../logs/play_state_log.jsonl"   # Adjust path as needed

# --- LOAD DATA ---
def load_win_probabilities(logfile):
    states = []
    with open(logfile, "r") as f:
        for line in f:
            d = json.loads(line)
            # You may need to adjust keys based on your log format
            ts = d.get("timestamp")
            try:
                tpar = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") if ts else None
            except Exception:
                tpar = None
            states.append({
                "step": d.get("step", len(states)),
                "win_probability": d.get("win_probability"),
                "timestamp": ts,
                "datetime": tpar,
                "possession": d.get("possession"),  # e.g., "NE", "KC"
                "tags": d.get("tags", []),
                "event": d.get("event_type", ""),
                "qb": d.get("qb", d.get("to_agent", "")),
                "offense": d.get("offense"),
                "defense": d.get("defense"),
            })
    return states

# --- ADVANCED TEAM COLOR PALETTE ---
def team_color(team):
    # Example: add as many as you want (NFL, custom, etc.)
    palette = {
        "NE": "#002244",      # Patriots blue
        "KC": "#E31837",      # Chiefs red
        "DAL": "#003594",     # Cowboys blue
        "SF": "#AA0000",      # 49ers red
        "NYG": "#0B2265",     # Giants blue
        "PHI": "#004C54",     # Eagles green
        "BAL": "#241773",     # Ravens purple
        "MIA": "#008E97",     # Dolphins aqua
        "TeamA": "royalblue",
        "TeamB": "crimson",
        None: "gray",
    }
    return palette.get(team, "#888888")  # fallback grey

# --- RICHER EVENT ANNOTATION ---
def key_event_annot(state):
    tags = set(state["tags"])
    annots = []
    # Standard tags
    if "qb_confidence:shaken" in tags:
        annots.append("QB 🚨")
    if "turnover:recent" in tags or state["event"] in {"interception", "fumble"}:
        annots.append("Turnover! 🔄")
    if "strategy:aggressive" in tags:
        annots.append("Aggressive 🧠")
    if "timeout:panic" in tags:
        annots.append("Panic Timeout")
    # Football moments
    if "4th_down_conversion" in tags:
        annots.append("4th Down Conversion!")
    if "red_zone" in tags:
        annots.append("Red Zone 🚩")
    if "qb_clutch_rating:elite" in tags:
        annots.append("QB Clutch ⭐️")
    if "defensive_stand" in tags:
        annots.append("Goal Line Stand 🛡️")
    if state["event"] in {"touchdown", "field_goal"}:
        annots.append(state["event"].replace("_", " ").capitalize())
    # You can expand this further!
    return " | ".join(annots) if annots else None

# --- AUDIO/CREATIVE OVERLAY HOOK (stub) ---
def creative_trigger(state, annotation):
    # This is where you'd call an audio/voice routine or creative overlay
    # For now we just print, but you could call TTS, soundFX, or creative visuals
    if annotation:
        print(f"CREATIVE TRIGGER: {annotation} at step {state['step']} / time {state['timestamp']}")
        # Example: call_audio_overlay(annotation, timestamp=state['timestamp'])

# --- PLOTLY FRAMES FOR ANIMATION ---
def animate_win_probability(states, output_html="win_prob_animation_deep.html"):
    # Use timestamps for x if possible, else fallback to step
    if all(s["datetime"] for s in states):
        xvals = [s["datetime"] for s in states]
        x_label = "Timestamp"
    else:
        xvals = [s["step"] for s in states]
        x_label = "Step"
    yvals = [s["win_probability"] for s in states]
    colors = [team_color(s["possession"]) for s in states]

    # Per step, build frames
    frames = []
    for k in range(1, len(states)+1):
        fr_states = states[:k]
        fr_x = [s["datetime"] if s["datetime"] else s["step"] for s in fr_states]
        fr_y = [s["win_probability"] for s in fr_states]
        fr_color = [team_color(s["possession"]) for s in fr_states]
        fr_text = [
            f"Step: {s['step']}<br>Win prob: {s['win_probability']:.1%}<br>Possession: {s['possession']}<br>Tags: {', '.join(s['tags'])}<br>QB: {s['qb']}<br>Event: {s['event']}<br>Time: {s['timestamp']}"
            for s in fr_states
        ]
        # Markers for key events
        event_annot = [key_event_annot(s) for s in fr_states]
        annot_x = [x for x,a in zip(fr_x, event_annot) if a]
        annot_y = [y for y,a in zip(fr_y, event_annot) if a]
        annot_text = [a for a in event_annot if a]

        # Trigger creative overlays or audio if present
        for s, a in zip(fr_states, event_annot):
            if a:
                creative_trigger(s, a)

        scatter = go.Scatter(
            x=fr_x, y=fr_y, mode="lines+markers",
            marker=dict(color=fr_color, size=14),
            line=dict(width=4, color="black"),
            text=fr_text, hoverinfo="text"
        )
        annots = [
            go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                text=[text],
                textposition="top center",
                marker=dict(size=22, color="orange", symbol="star"),
                showlegend=False,
                hoverinfo="text"
            )
            for x, y, text in zip(annot_x, annot_y, annot_text)
        ]
        frames.append(go.Frame(data=[scatter] + annots, name=f"step_{k}"))

    # Initial data
    init_scatter = go.Scatter(
        x=[xvals[0]], y=[yvals[0]], mode="lines+markers",
        marker=dict(color=[colors[0]], size=14),
        line=dict(width=4, color="black"),
        text=[f"Step: {states[0]['step']}<br>Win prob: {yvals[0]:.1%}"],
        hoverinfo="text"
    )

    layout = go.Layout(
        title="Win Probability Progression (Animated, Enhanced)",
        xaxis_title=x_label,
        yaxis_title="Win Probability",
        yaxis=dict(range=[0,1], tickformat=".0%"),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": 600, "redraw": True}, "fromcurrent": True}]),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                ]
            )
        ],
        hovermode="closest"
    )
    fig = go.Figure(data=[init_scatter], frames=frames, layout=layout)
    py.plot(fig, filename=output_html, auto_open=True)
    print(f"Animated win probability saved to {output_html}")

if __name__ == "__main__":
    states = load_win_probabilities(LOGFILE)
    animate_win_probability(states)