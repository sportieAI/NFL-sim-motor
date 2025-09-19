"""
Advanced NLP Tagging using Transformer Models.
"""

from transformers import pipeline


class AdvancedNLPTagger:
    def __init__(self):
        self.model = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

    def classify(self, text):
        return self.model(text)

    def extract_entities(self, text):
        ner = pipeline("ner", model="dslim/bert-base-NER")
        return ner(text)


# Example usage:
# tagger = AdvancedNLPTagger()
# print(tagger.classify("Great touchdown by the QB!"))
# print(tagger.extract_entities("Patrick Mahomes completed the pass."))
