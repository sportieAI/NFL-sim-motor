"""
Plug-and-Play Expansion Paths for Continuous Intelligence Loop

- NBA/MLB/UFC: Swap schemas, retrain tagging & clustering, reuse pipelines.
- Partner APIs: Serve narratives, predictions, and cluster insights via secure endpoints.
- Fly’s Dashboard: Visualize possession flow, emotional arcs, and strategic pivots in real time.
"""

# --- 1. Schema Swap for New Sports (NBA, MLB, UFC) ---
def load_sport_schema(sport):
    """
    Dynamically loads schema and model assets for a given sport.
    """
    if sport == "NFL":
        from engine.simulator import NFLSimulator as Simulator
        from nlp_tagging import NLPTagger
        from clustering import PlayClusterer
    elif sport == "NBA":
        from nba_engine.simulator import NBASimulator as Simulator
        from nba_nlp_tagging import NBATagger as NLPTagger
        from nba_clustering import NBAClusterer as PlayClusterer
    elif sport == "MLB":
        from mlb_engine.simulator import MLBSimulator as Simulator
        from mlb_nlp_tagging import MLBTagger as NLPTagger
        from mlb_clustering import MLBClusterer as PlayClusterer
    elif sport == "UFC":
        from ufc_engine.simulator import UFCSimulator as Simulator
        from ufc_nlp_tagging import UFCTagger as NLPTagger
        from ufc_clustering import UFCClusterer as PlayClusterer
    else:
        raise ValueError(f"Unsupported sport: {sport}")
    return Simulator, NLPTagger, PlayClusterer

# --- 2. API Serving for Partners ---
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/insights")
async def serve_insights(request: Request):
    """
    Accepts JSON state, returns narrative, prediction, and cluster info.
    """
    body = await request.json()
    sport = body.get("sport", "NFL")
    Simulator, NLPTagger, PlayClusterer = load_sport_schema(sport)
    sim = Simulator()
    tagger = NLPTagger()
    clusterer = PlayClusterer()
    play = sim.simulate_play(body["state"])
    tags = tagger.tag(play['description'])
    cluster = clusterer.assign_cluster(tags)
    # Prediction and narrative modules reused as before:
    from ml_predictor import PlayOutcomePredictor
    from llm_narrative import LLMNarrator
    predictor = PlayOutcomePredictor()
    narrator = LLMNarrator()
    prediction = predictor.predict(play, tags, cluster)
    narrative = narrator.narrate(play, cluster, prediction)
    return JSONResponse({
        "play": play,
        "tags": tags,
        "cluster": cluster,
        "prediction": prediction,
        "narrative": narrative
    })

# --- 3. Real-Time Dashboard Streaming (Fly’s Dashboard) ---
import threading
import queue

class DashboardStreamer:
    """
    Streams key events and states to a dashboard in real time.
    """
    def __init__(self, publish_func):
        self.q = queue.Queue()
        self.publish_func = publish_func
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stream(self, data):
        self.q.put(data)

    def _run(self):
        while True:
            data = self.q.get()
            if data is None:
                break
            self.publish_func(data)

# Usage example:
# def fly_dashboard_publish(data):
#     # Send to websocket, HTTP endpoint, or update in-memory dashboard
#     print("Dashboard update:", data)
#
# streamer = DashboardStreamer(publish_func=fly_dashboard_publish)
# streamer.stream({"narrative": "Touchdown!", "emotion": 0.95})