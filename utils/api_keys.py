"""
API keys configuration for external data sources
"""

import os

# Sportradar API key - use environment variable or demo key
SPORTRADAR_KEY = os.environ.get('SPORTRADAR_API_KEY', 'demo_key')

# SportsData.io (formerly Fantasy Data) API key
FASTR_KEY = os.environ.get('SPORTSDATA_API_KEY', 'demo_key')

# Note: For production use, set these as environment variables:
# export SPORTRADAR_API_KEY="your_actual_api_key"
# export SPORTSDATA_API_KEY="your_actual_api_key"