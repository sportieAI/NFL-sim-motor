#!/bin/bash

# Ensure the script is run from the repo root where requirements.txt exists
if [ ! -f requirements.txt ]; then
  echo "requirements.txt not found in the current directory."
  exit 1
fi

# Upgrade pip first (optional but recommended)
python -m pip install --upgrade pip

# Install all dependencies listed in requirements.txt
pip install -r requirements.txt

echo "✅ All dependencies installed."