#!/bin/sh
set -e

# Configuration
TEAM="KC"
SEASON="2023"
MODE="historical"

echo "Setting up NFL Simulation Engine..."

# Check if we're already in the repo directory
if [ -f "main.py" ] && [ -f "requirements.txt" ]; then
    echo "Already in NFL-sim-motor directory, skipping clone"
else
    echo "Cloning repository..."
    REPO_URL="https://github.com/sportieAI/NFL-sim-motor.git"
    REPO_NAME="NFL-sim-motor"
    
    if [ ! -d "$REPO_NAME" ]; then
        git clone "$REPO_URL" || {
            echo "Failed to clone repository (possible firewall/network issue)"
            echo "Please manually download and extract the repository"
            exit 1
        }
    fi
    cd "$REPO_NAME"
fi

echo "Checking for python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required. Please install it from your package manager."
    exit 1
fi

echo "Setting up Python virtual environment..."
python3 -m venv venv || python3 -m venv .venv
if [ -d "venv" ]; then 
    . venv/bin/activate
else 
    . .venv/bin/activate
fi

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip || echo "Warning: pip upgrade failed, continuing with existing version"

# Try to install requirements with timeout and fallback
echo "Installing requirements (this may take a moment)..."
timeout 300 pip install -r requirements.txt || {
    echo "Installation timed out or failed (likely firewall/network issue)"
    echo "Trying offline mode setup..."
    export OFFLINE_MODE=true
    echo "OFFLINE_MODE=true" > .env
    echo "Set up for offline mode. External APIs will use mock data."
}

echo "Testing installation..."
python3 -c "import main; print('Installation successful!')" || {
    echo "Installation verification failed"
    echo "Please check error messages above"
    exit 1
}

echo "Running sample simulation..."
export OFFLINE_MODE=true  # Ensure offline mode for demo
python3 main.py || {
    echo "Sample simulation failed"
    echo "Check the error messages above for details"
    exit 1
}

echo ""
echo "🏈 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run simulations: python3 main.py"
echo "2. Launch dashboard: python3 dashboard_and_api.py"
echo "3. For online mode, set API keys in environment variables"
echo "4. See FIREWALL_CONFIGURATION.md for network setup help"
echo ""
echo "Repository is ready for use in offline mode."