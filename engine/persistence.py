"""
Persistence Example

Demonstrates saving and loading simulation state.
"""

import pickle
import redis

def save_state_to_pickle(state, filename):
    with open(filename, "wb") as f:
        pickle.dump(state, f)

def load_state_from_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

def save_state_to_redis(state, key, redis_url="redis://localhost:6379/0"):
    r = redis.Redis.from_url(redis_url)
    r.set(key, pickle.dumps(state))

def load_state_from_redis(key, redis_url="redis://localhost:6379/0"):
    r = redis.Redis.from_url(redis_url)
    return pickle.loads(r.get(key))
