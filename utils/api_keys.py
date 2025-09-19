"""API key management for external services."""

import os

# External API keys (loaded from environment variables)
SPORTRADAR_KEY = os.environ.get("SPORTRADAR_API_KEY", "demo-key")
FASTR_KEY = os.environ.get("FASTR_API_KEY", "demo-key")
ESPN_KEY = os.environ.get("ESPN_API_KEY", "demo-key")

# API endpoints
SPORTRADAR_BASE_URL = "https://api.sportradar.us/nfl"
FASTR_BASE_URL = "https://api.fastr.ai"
ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
