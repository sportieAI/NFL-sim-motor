"""
Enhanced configuration manager with environment-specific settings.
Supports staging.yaml and production.yaml configurations with environment variable overrides.
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from prefect.blocks.system import Secret
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConfigManager:
    """Enhanced configuration manager for environment-specific settings."""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv('APP_ENV', 'development')
        self.config_dir = Path(__file__).parent / 'config'
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment-specific YAML file."""
        config_file = self.config_dir / f'{self.environment}.yaml'
        
        if not config_file.exists():
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Expand environment variables in config values
            config = self._expand_env_vars(config)
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}")
            return self._get_default_config()
    
    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in config values."""
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            # Extract environment variable name and default value
            env_expr = obj[2:-1]  # Remove ${ and }
            if ':-' in env_expr:
                env_var, default = env_expr.split(':-', 1)
                return os.getenv(env_var, default)
            else:
                return os.getenv(env_expr, obj)
        else:
            return obj
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for fallback."""
        return {
            'app': {
                'name': 'NFL-sim-motor',
                'version': '1.0.0',
                'debug': True,
                'log_level': 'INFO'
            },
            'database': {
                'postgres': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'nfl_sim',
                    'username': 'postgres',
                    'password': '',
                    'pool_size': 10
                },
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'password': None
                }
            },
            'storage': {
                's3': {
                    'bucket': 'nfl-sim-local',
                    'region': 'us-west-2',
                    'endpoint_url': 'http://localhost:9000'
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'database.postgres.host')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self, db_type: str = 'postgres') -> Dict[str, Any]:
        """Get database configuration for specified type."""
        return self.get(f'database.{db_type}', {})
    
    def get_storage_config(self, storage_type: str = 's3') -> Dict[str, Any]:
        """Get storage configuration for specified type."""
        return self.get(f'storage.{storage_type}', {})
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == 'production'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('app.debug', False)


# Global config manager instance
config = ConfigManager()


def get_s3_settings():
    """Get S3 settings with Prefect secret support."""
    s3_config = config.get_storage_config('s3')
    
    # Prefer Prefect secret block, fallback to env vars for local dev
    if PREFECT_AVAILABLE and config.is_production():
        try:
            access_key = Secret.load("s3-access-key").get()
            secret_key = Secret.load("s3-secret-key").get()
            endpoint_url = Secret.load("s3-endpoint-url").get()
            bucket = Secret.load("s3-bucket").get()
        except Exception:
            access_key = os.environ.get("S3_ACCESS_KEY", s3_config.get('access_key', 'minioadmin'))
            secret_key = os.environ.get("S3_SECRET_KEY", s3_config.get('secret_key', 'minioadmin'))
            endpoint_url = os.environ.get("S3_ENDPOINT_URL", s3_config.get('endpoint_url', 'http://localhost:9000'))
            bucket = os.environ.get("S3_BUCKET", s3_config.get('bucket', 'simulation-archives'))
    else:
        access_key = os.environ.get("S3_ACCESS_KEY", s3_config.get('access_key', 'minioadmin'))
        secret_key = os.environ.get("S3_SECRET_KEY", s3_config.get('secret_key', 'minioadmin'))
        endpoint_url = os.environ.get("S3_ENDPOINT_URL", s3_config.get('endpoint_url', 'http://localhost:9000'))
        bucket = os.environ.get("S3_BUCKET", s3_config.get('bucket', 'simulation-archives'))
    
    return {
        "access_key": access_key,
        "secret_key": secret_key,
        "endpoint_url": endpoint_url,
        "bucket": bucket,
        "region": s3_config.get('region', 'us-west-2')
    }


def get_mongo_settings():
    """Get MongoDB settings with Prefect secret support."""
    if PREFECT_AVAILABLE and config.is_production():
        try:
            mongo_url = Secret.load("mongo-url").get()
            db_name = Secret.load("mongo-db-name").get()
        except Exception:
            mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
            db_name = os.environ.get("MONGO_DB_NAME", "sim")
    else:
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("MONGO_DB_NAME", "sim")
    
    return {"mongo_url": mongo_url, "db_name": db_name}


def get_redis_settings():
    """Get Redis settings with Prefect secret support."""
    redis_config = config.get_database_config('redis')
    
    if PREFECT_AVAILABLE and config.is_production():
        try:
            redis_url = Secret.load("redis-url").get()
        except Exception:
            redis_url = os.environ.get("REDIS_URL", f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}")
    else:
        redis_url = os.environ.get("REDIS_URL", f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}")
    
    return {"redis_url": redis_url}


def get_postgres_settings():
    """Get PostgreSQL settings."""
    pg_config = config.get_database_config('postgres')
    
    return {
        "host": pg_config.get('host', 'localhost'),
        "port": pg_config.get('port', 5432),
        "database": pg_config.get('database', 'nfl_sim'),
        "username": pg_config.get('username', 'postgres'),
        "password": pg_config.get('password', ''),
        "pool_size": pg_config.get('pool_size', 10),
        "max_overflow": pg_config.get('max_overflow', 20)
    }


def get_jwt_secret():
    """Get JWT secret for authentication."""
    if PREFECT_AVAILABLE and config.is_production():
        try:
            return Secret.load("jwt-secret").get()
        except Exception:
            pass
    
    jwt_secret = os.environ.get("JWT_SECRET", config.get('security.jwt_secret'))
    if not jwt_secret:
        if config.is_production():
            raise ValueError("JWT_SECRET must be set in production environment")
        else:
            logger.warning("Using default JWT secret for development - change in production!")
            return "dev_jwt_secret_change_in_production"
    
    return jwt_secret


def validate_production_config():
    """Validate that all required production settings are present."""
    if not config.is_production():
        return True
    
    required_secrets = [
        'POSTGRES_PASSWORD',
        'JWT_SECRET',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    
    missing_secrets = []
    for secret in required_secrets:
        if not os.environ.get(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        raise ValueError(f"Missing required production secrets: {', '.join(missing_secrets)}")
    
    return True