import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)

class NLPTagger:
    """Minimal NLP tagger for play descriptions and sentiment."""

    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def tag(self, text):
        tags = []
        t = text.lower()
        if "pass" in t:
            tags.append("pass")
        if "run" in t:
            tags.append("run")
        if "yards" in t:
            try:
                yards = int([w for w in t.split() if w.lstrip('-').isdigit()][0])
            except (IndexError, ValueError):
                yards = 0
            if yards >= 10:
                tags.append("explosive")
            if yards <= 0:
                tags.append("negative_play")
        sentiment = self.sia.polarity_scores(text)["compound"]
        return {"tags": tags, "sentiment": sentiment}
