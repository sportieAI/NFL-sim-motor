"""
Mock API keys for development and testing.
In production, these would be loaded from environment variables or secrets manager.
"""
import os

# Mock API keys - in production these should come from environment variables
SPORTRADAR_KEY = os.getenv("SPORTRADAR_API_KEY", "mock_sportradar_key_dev_only")
FASTR_KEY = os.getenv("FASTR_API_KEY", "mock_fastr_key_dev_only")

# Add warning for development
if SPORTRADAR_KEY == "mock_sportradar_key_dev_only":
    import warnings
    warnings.warn("Using mock API keys - set SPORTRADAR_API_KEY environment variable for production")

if FASTR_KEY == "mock_fastr_key_dev_only":
    import warnings
    warnings.warn("Using mock API keys - set FASTR_API_KEY environment variable for production")
