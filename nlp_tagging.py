"""
Dedicated NLP Tagging Module for sportieAI/NFL-sim-motor

Handles text-to-tag/context transformation, sentiment analysis, and feature extraction for play descriptions and fan reactions.
"""

import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


class NLPTagger:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.model = MultinomialNB()
        self.labels = []

    def preprocess(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text

    def fit(self, texts, labels):
        X = self.vectorizer.fit_transform([self.preprocess(t) for t in texts])
        self.model.fit(X, labels)
        self.labels = labels

    def predict(self, text):
        X = self.vectorizer.transform([self.preprocess(text)])
        return self.model.predict(X)[0]

    def sentiment(self, text):
        # Simple rule-based sentiment analysis; replace with advanced model as needed
        positive = ["good", "great", "excellent", "win", "success"]
        negative = ["bad", "poor", "fail", "loss", "injury"]
        score = sum([word in text for word in positive]) - sum(
            [word in text for word in negative]
        )
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"


# Example usage:
# tagger = NLPTagger()
# tagger.fit(["pass complete", "fumble lost"], ["completion", "turnover"])
# tagger.predict("pass complete")  # -> "completion"
