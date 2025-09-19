"""
NFL Simulation Motor - Production-ready NFL simulation engine
"""

__version__ = "1.0.0"
__author__ = "sportieAI"
__email__ = "contact@sportieai.com"

from .config import config, ConfigManager

__all__ = [
    "config",
    "ConfigManager",
    "__version__",
    "__author__",
    "__email__",
]