"""
Persistence Example

Demonstrates saving and loading simulation state.
"""

import pickle
import sqlite3
import json
import os
from datetime import datetime

def save_state_to_pickle(state, filename):
    """Save state to pickle file"""
    with open(filename, "wb") as f:
        pickle.dump(state, f)

def load_state_from_pickle(filename):
    """Load state from pickle file"""
    with open(filename, "rb") as f:
        return pickle.load(f)

def save_state_to_sqlite(state, db_path="simulation.db", table="game_states"):
    """Save state to SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            state_data TEXT
        )
    ''')
    
    # Insert state data
    timestamp = datetime.now().isoformat()
    state_json = json.dumps(state, default=str)
    cursor.execute(f'INSERT INTO {table} (timestamp, state_data) VALUES (?, ?)', 
                   (timestamp, state_json))
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def load_state_from_sqlite(state_id, db_path="simulation.db", table="game_states"):
    """Load state from SQLite database by ID"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT state_data FROM {table} WHERE id = ?', (state_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def list_saved_states(db_path="simulation.db", table="game_states"):
    """List all saved states in SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'SELECT id, timestamp FROM {table} ORDER BY timestamp DESC')
        results = cursor.fetchall()
        return [{"id": row[0], "timestamp": row[1]} for row in results]
    except sqlite3.OperationalError:
        # Table doesn't exist
        return []
    finally:
        conn.close()

# Redis persistence (optional - requires redis package)
try:
    import redis
    
    def save_state_to_redis(state, key, redis_url="redis://localhost:6379/0"):
        """Save state to Redis"""
        r = redis.Redis.from_url(redis_url)
        r.set(key, pickle.dumps(state))

    def load_state_from_redis(key, redis_url="redis://localhost:6379/0"):
        """Load state from Redis"""
        r = redis.Redis.from_url(redis_url)
        data = r.get(key)
        if data:
            return pickle.loads(data)
        return None
        
except ImportError:
    def save_state_to_redis(state, key, redis_url="redis://localhost:6379/0"):
        print("Redis not available. Install redis package to use Redis persistence.")
        
    def load_state_from_redis(key, redis_url="redis://localhost:6379/0"):
        print("Redis not available. Install redis package to use Redis persistence.")
        return None
