# Advanced NLP Tagging

## Overview
Uses transformer-based models for sentiment, classification, and entity recognition.

## Features
- Deep contextual tagging for plays and reactions
- Named Entity Recognition (players, teams, actions)
- Easy integration with HuggingFace pipelines

## Example

```python
from nlp_transformer import AdvancedNLPTagger
nlp = AdvancedNLPTagger()
print(nlp.classify("Amazing run!"))
print(nlp.extract_entities("Patrick Mahomes threw a touchdown pass."))
```

## Requirements
- `transformers` Python library
