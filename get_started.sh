#!/bin/sh
set -e

REPO_URL="https://github.com/sportieAI/NFL-sim-motor.git"
REPO_NAME="NFL-sim-motor"
TEAM="KC"
SEASON="2023"
MODE="historical"

echo "Cloning $REPO_URL..."
if [ ! -d "$REPO_NAME" ]; then
  git clone "$REPO_URL"
fi
cd "$REPO_NAME"

echo "Checking for python3..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Please install it from the App Store or your package manager."
  exit 1
fi

echo "Setting up Python virtual environment..."
python3 -m venv venv || python3 -m venv .venv
if [ -d "venv" ]; then . venv/bin/activate; else . .venv/bin/activate; fi

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running sample simulation..."
python main.py --mode="$MODE" --team="$TEAM" --season="$SEASON"

echo "All done!"