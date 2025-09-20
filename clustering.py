import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class PlayClusterer:
    """TF-IDF + KMeans clustering for play scenarios."""

    MODEL_PATH = "play_clusterer.joblib"

    def __init__(self):
        if os.path.exists(self.MODEL_PATH):
            self.vectorizer, self.kmeans = joblib.load(self.MODEL_PATH)
        else:
            # Fit on a small default corpus for quick start
            corpus = [
                "pass short gain",
                "run negative yards",
                "explosive pass",
                "turnover",
                "field goal",
                "touchdown"
            ]
            self.vectorizer = TfidfVectorizer()
            X = self.vectorizer.fit_transform(corpus)
            self.kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            self.kmeans.fit(X)
            joblib.dump((self.vectorizer, self.kmeans), self.MODEL_PATH)

    def assign_cluster(self, tag_dict):
        # Use tags as a pseudo-document for clustering
        doc = " ".join(tag_dict["tags"])
        X = self.vectorizer.transform([doc])
        cluster = int(self.kmeans.predict(X)[0])
        return f"cluster_{cluster}"
