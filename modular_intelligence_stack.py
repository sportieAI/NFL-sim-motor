🧠 Modular Intelligence Stack (Fly-ready)

This stack enables full-cycle, modular NFL game intelligence—from simulation to recall and learning.
Each module is replaceable and can be invoked independently for testing, orchestration, or model upgrades.

Layer         | Module            | Output                    | Use
--------------|-------------------|---------------------------|----------------------------
Simulation    | simulate_play     | PlayEvent                 | Ground truth
Tagging       | tagging_engine    | TagBundle                 | Semantic hooks
Clustering    | clustering        | cluster_id                | Scenario cognition
Prediction    | model_infer       | EPA, win_prob             | Strategic foresight
Narrative     | creative_output   | summary_text, voice_params| Engagement
Memory        | memory_continuity | DriveSnapshot             | Recall & replay
Evaluation    | Evaluator         | policy deltas             | Learning loop

from typing import Any, Dict

# --- Simulation Layer ---
def simulate_play(state: Dict[str, Any]) -> Dict[str, Any]:
    # Simulate a single NFL play; output a PlayEvent dict
    return {
        "play_id": state.get("next_play_id", 1),
        "description": "Pass complete to WR1 for 12 yards.",
        "raw_stats": {"yards": 12, "complete": True},
        "team": state.get("team", "NEP"),
        "down": state.get("down", 1),
        "distance": state.get("distance", 10),
        "yardline": state.get("yardline", "NEP 25"),
        "clock": state.get("clock", "15:00 Q1"),
    }

# --- Tagging Layer ---
def tagging_engine(play_event: Dict[str, Any]) -> Dict[str, Any]:
    # Extract tags, sentiment, and features from play text and stats
    tags = []
    desc = play_event.get("description", "").lower()
    if "pass complete" in desc:
        tags.append("completion")
    if play_event["raw_stats"]["yards"] >= 10:
        tags.append("explosive_play")
    sentiment = "positive" if play_event["raw_stats"]["yards"] > 0 else "neutral"
    return {"tags": tags, "sentiment": sentiment, "features": play_event["raw_stats"]}

# --- Clustering Layer ---
def clustering(tag_bundle: Dict[str, Any]) -> str:
    # Assign play to a cluster based on tags/features
    if "explosive_play" in tag_bundle["tags"]:
        return "cluster_explosive"
    if "completion" in tag_bundle["tags":
        return "cluster_safe"
    return "cluster_other"

# --- Prediction Layer ---
def model_infer(play_event: Dict[str, Any], cluster_id: str) -> Dict[str, float]:
    # Predict EPA, win_prob, etc. (stubbed for demo)
    epa = 0.24 if cluster_id == "cluster_explosive" else 0.02
    win_prob = 0.57 if "explosive_play" in play_event.get("description", "") else 0.51
    return {"EPA": epa, "win_prob": win_prob}

# --- Narrative Layer ---
def creative_output(play_event: Dict[str, Any], pred: Dict[str, float]) -> Dict[str, Any]:
    # Generate a narrative and voice parameters
    summary = f"{play_event['description']} (EPA: {pred['EPA']:.2f}, Win%: {pred['win_prob']:.0%})"
    voice_params = {"emotion": "excited" if pred["EPA"] > 0.2 else "neutral"}
    return {"summary_text": summary, "voice_params": voice_params}

# --- Memory Layer ---
def memory_continuity(play_event: Dict[str, Any], tag_bundle: Dict[str, Any], cluster_id: str, pred: Dict[str, float], narrative: Dict[str, Any]) -> Dict[str, Any]:
    # Aggregate all key outputs into a DriveSnapshot for recall/replay
    return {
        "play_id": play_event["play_id"],
        "tags": tag_bundle["tags"],
        "cluster_id": cluster_id,
        "EPA": pred["EPA"],
        "win_prob": pred["win_prob"],
        "summary": narrative["summary_text"],
        "voice": narrative["voice_params"]
    }

# --- Evaluation Layer ---
def Evaluator(memory: Dict[str, Any], prev_memory: Dict[str, Any]) -> Dict[str, Any]:
    # Compare memory snapshots, produce policy deltas (stubbed)
    delta_epa = memory["EPA"] - prev_memory.get("EPA", 0)
    return {"policy_deltas": {"EPA_change": delta_epa}}

# --- Example Orchestration ---
def full_intelligence_pass(state, prev_memory):
    # 1. Simulation
    play_event = simulate_play(state)
    # 2. Tagging
    tag_bundle = tagging_engine(play_event)
    # 3. Clustering
    cluster_id = clustering(tag_bundle)
    # 4. Prediction
    pred = model_infer(play_event, cluster_id)
    # 5. Narrative
    narrative = creative_output(play_event, pred)
    # 6. Memory
    memory = memory_continuity(play_event, tag_bundle, cluster_id, pred, narrative)
    # 7. Evaluation
    eval_result = Evaluator(memory, prev_memory)
    return {
        "PlayEvent": play_event,
        "TagBundle": tag_bundle,
        "cluster_id": cluster_id,
        "Prediction": pred,
        "Narrative": narrative,
        "DriveSnapshot": memory,
        "policy_deltas": eval_result["policy_deltas"],
    }

# --- Example Usage ---
if __name__ == "__main__":
    # Mock state and previous memory
    state = {"next_play_id": 1, "down": 1, "distance": 10, "team": "NEP", "yardline": "NEP 25", "clock": "15:00 Q1"}
    prev_memory = {}
    outputs = full_intelligence_pass(state, prev_memory)
    for k, v in outputs.items():
        print(f"{k}: {v}")