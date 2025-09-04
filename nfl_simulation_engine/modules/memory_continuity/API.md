# Memory Continuity Module — API Documentation

This API documentation covers the key classes and methods provided by the module, including detailed usage examples.

---

## CacheManager

**Purpose:**  
Handles disk-based artifact caching for simulation runs.

### Class: `CacheManager`

#### Constructor
```python
CacheManager(cache_dir="cache")
```
- `cache_dir`: Directory to store cache files.

#### Methods

- **has_cache(key)**  
  Checks if an artifact exists in the cache.
  ```python
  cache.has_cache("artifact_001")  # Returns True/False
  ```

- **get_cache(key)**  
  Retrieves the cached artifact or returns None if not found.
  ```python
  result = cache.get_cache("artifact_001")
  if result is not None:
      print("Retrieved:", result)
  ```

- **set_cache(key, artifact)**  
  Stores the artifact in the cache under the given key.
  ```python
  cache.set_cache("artifact_001", {"foo": "bar"})
  ```

- **ensure_artifact(key, generate_func, *args, **kwargs)**  
  Retrieves artifact from cache or generates/caches it if missing.
  ```python
  def generate_artifact(x):
      return {"result": x * 2}

  artifact = cache.ensure_artifact("artifact_001", generate_artifact, 21)
  # Uses cache if present, else generates and caches
  ```

---

## TrendsEngine

**Purpose:**  
Models and updates momentum, confidence, and possession trends.

### Class: `TrendsEngine`

#### Methods

- **update_momentum(outcome, state)**
  ```python
  momentum = trends.update_momentum(outcome, state)
  ```

- **update_confidence(prediction, actual)**
  ```python
  confidence = trends.update_confidence(prediction="TD", actual="TD")
  ```

- **update_possession_trends(possession_state, outcome)**
  ```python
  trends.update_possession_trends(possession_state, outcome)
  ```

- **get_trends_summary()**
  ```python
  summary = trends.get_trends_summary()
  print(summary)
  ```

---

## EventTagger

**Purpose:**  
Tags simulation/game events using NLP.

### Class: `EventTagger`

#### Constructor
```python
EventTagger(custom_patterns=None)
```
- `custom_patterns`: List of pattern dictionaries for custom tagging.

#### Methods

- **tag_event(event_text)**
  ```python
  tagger = EventTagger(custom_patterns=[
      {"regex": "touchdown", "tag": "scoring_event"},
      {"regex": "interception", "tag": "turnover"}
  ])
  tags = tagger.tag_event("Quarterback throws a touchdown pass.")
  print(tags)
  ```

---

## MetaLearningTrigger

**Purpose:**  
Automates meta-learning triggers based on conditions and game metrics.

### Class: `MetaLearningTrigger`

#### Constructor
```python
MetaLearningTrigger(learning_callback, check_interval=60)
```
- `learning_callback`: Function to call when triggered.
- `check_interval`: How often to check for triggers (seconds).

#### Methods

- **add_trigger_condition(condition_func)**
  ```python
  def score_jump_condition(state):
      return state.get('score_diff', 0) > 20

  trigger.add_trigger_condition(score_jump_condition)
  ```

- **check_and_trigger(game_state)**
  ```python
  trigger.check_and_trigger(current_game_state)
  ```

---

## Example: Integrated Workflow

```python
from cache_manager import CacheManager
from trends import TrendsEngine
from nlp_tagging import EventTagger
from meta_learning_triggers import MetaLearningTrigger

# Setup cache manager
cache = CacheManager()

# Artifact generation with cache
def artifact_func(x):
    return {"result": x * 2}
artifact = cache.ensure_artifact("artifact_001", artifact_func, 21)

# Trend modeling
trends = TrendsEngine()
state, outcome = {}, {'yards': 10}
momentum = trends.update_momentum(outcome, state)

# NLP tagging
tagger = EventTagger()
tags = tagger.tag_event("Quarterback throws a touchdown pass.")

# Meta-learning trigger
def callback(state): print("Triggered!", state)
trigger = MetaLearningTrigger(learning_callback=callback)
trigger.add_trigger_condition(lambda s: s.get("score", 0) > 30)
trigger.check_and_trigger({"score": 35})
```

---

**For more details, see individual module docstrings and README.