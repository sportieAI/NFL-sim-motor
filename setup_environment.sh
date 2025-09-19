#!/bin/bash

# 1. Create a Python 3.10+ environment (using venv)
python3.10 -m venv venv
source venv/bin/activate

# Alternatively, with conda:
# conda create -n nfl-sim python=3.10 -y
# conda activate nfl-sim

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure Redis is running (default port 6379)
if ! nc -z localhost 6379; then
  echo "Starting Redis server..."
  redis-server &
else
  echo "Redis is already running."
fi

# 4. Ensure Postgres is running (default port 5432)
if ! nc -z localhost 5432; then
  echo "Please start your Postgres server manually."
else
  echo "Postgres is already running."
fi

# 5. (Optional) Start FAISS index server
if [ "$START_FAISS" = "1" ]; then
  echo "Starting FAISS index server..."
  # Replace with your FAISS server command, e.g.,
  # python faiss_server.py &
else
  echo "FAISS index server not started (set START_FAISS=1 to enable)."
fi

echo "✅ Environment setup complete."