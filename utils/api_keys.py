# API Keys configuration with fallback handling
import os

# API Keys with environment variable fallbacks
SPORTRADAR_KEY = os.getenv('SPORTRADAR_API_KEY', 'demo_key_placeholder')
FASTR_KEY = os.getenv('FASTR_API_KEY', 'demo_key_placeholder')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
COQUI_API_KEY = os.getenv('COQUI_API_KEY', '')

# Flag to indicate if we're in offline/demo mode
OFFLINE_MODE = os.getenv('OFFLINE_MODE', 'true').lower() == 'true'

def get_api_key(service_name):
    """
    Get API key for a service with appropriate fallback.
    
    Args:
        service_name: Name of the service ('sportradar', 'fastr', 'openai', 'coqui')
    
    Returns:
        API key string or None if not available
    """
    keys = {
        'sportradar': SPORTRADAR_KEY,
        'fastr': FASTR_KEY,
        'openai': OPENAI_API_KEY,
        'coqui': COQUI_API_KEY
    }
    
    key = keys.get(service_name.lower())
    
    # Return None for demo/placeholder keys to trigger fallback behavior
    if key in ['demo_key_placeholder', '']:
        return None
        
    return key

def is_service_available(service_name):
    """
    Check if a service is available (has real API key and not in offline mode).
    """
    if OFFLINE_MODE:
        return False
        
    return get_api_key(service_name) is not None