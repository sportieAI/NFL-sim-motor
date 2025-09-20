import joblib
import numpy as np

class PlayOutcomePredictor:
    """Sklearn/ANN-based outcome predictor (load your own .joblib model)."""
    MODEL_PATH = "play_outcome_predictor.joblib"

    def __init__(self):
        try:
            self.model = joblib.load(self.MODEL_PATH)
        except Exception:
            # Fallback: trivial linear model for stub
            from sklearn.linear_model import LinearRegression
            self.model = LinearRegression().fit([[0, 0]], [0])

    def predict(self, play, tags, cluster):
        # Feature engineering stub: use play and tags for features
        features = [
            play.get("down", 1),
            play.get("yards", 0),
            int("explosive" in tags["tags"]),
            int("negative_play" in tags["tags"]),
        ]
        arr = np.array(features).reshape(1, -1)
        pred = float(self.model.predict(arr)[0])
        return {
            "expected_yards": pred,
            "risk_score": np.clip(1 - pred / 15, 0, 1)  # Example: higher yards = lower risk
        }