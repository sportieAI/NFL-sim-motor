"""
Health check and readiness endpoints for production deployment.
"""
import json
import time
from datetime import datetime
from typing import Dict, Any

from config import config
from logging_config import get_logger

logger = get_logger('health-check')


def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health status."""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": config.environment,
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check configuration
    try:
        _ = config.get('app.name')
        health_status["checks"]["configuration"] = {"status": "healthy", "message": "Configuration loaded"}
    except Exception as e:
        health_status["checks"]["configuration"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check schema manager
    try:
        from schemas.schema_manager import SchemaManager
        schema_manager = SchemaManager()
        health_status["checks"]["schemas"] = {"status": "healthy", "message": "Schema manager initialized"}
    except Exception as e:
        health_status["checks"]["schemas"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check logging system
    try:
        logger.info("Health check logging test")
        health_status["checks"]["logging"] = {"status": "healthy", "message": "Logging system operational"}
    except Exception as e:
        health_status["checks"]["logging"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"
    
    # Add response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_status


def get_readiness() -> Dict[str, Any]:
    """Check if system is ready to handle requests."""
    readiness_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Validate production config if needed
    if config.is_production():
        try:
            from config import validate_production_config
            validate_production_config()
            readiness_status["checks"]["production_config"] = {"status": "ready", "message": "Production config validated"}
        except Exception as e:
            readiness_status["checks"]["production_config"] = {"status": "not_ready", "message": str(e)}
            readiness_status["status"] = "not_ready"
    
    # Check core functionality
    try:
        # Test schema validation
        from schemas.schema_manager import SchemaManager, run_schema_tests
        results = run_schema_tests()
        if results.get('overall_success', False):
            readiness_status["checks"]["schema_validation"] = {"status": "ready", "message": "Schema tests passed"}
        else:
            readiness_status["checks"]["schema_validation"] = {"status": "not_ready", "message": "Schema tests failed"}
            readiness_status["status"] = "not_ready"
    except Exception as e:
        readiness_status["checks"]["schema_validation"] = {"status": "not_ready", "message": str(e)}
        readiness_status["status"] = "not_ready"
    
    return readiness_status


if __name__ == '__main__':
    # CLI health check
    print("=== System Health Check ===")
    health = get_system_health()
    print(json.dumps(health, indent=2))
    
    print("\n=== System Readiness Check ===")
    readiness = get_readiness()
    print(json.dumps(readiness, indent=2))
    
    # Exit with appropriate code
    if health["status"] == "healthy" and readiness["status"] == "ready":
        print("\n✅ System is healthy and ready")
        exit(0)
    else:
        print("\n❌ System has issues")
        exit(1)