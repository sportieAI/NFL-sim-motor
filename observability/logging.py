"""
Per-tenant structured logging utility.
Supports JSON logs, tenant context, and extension for cloud-native log aggregation.
"""
import logging
import json
import sys
from contextvars import ContextVar

# Context variable to keep track of current tenant
_current_tenant = ContextVar("current_tenant", default="unknown-tenant")

def set_tenant(tenant_id: str):
    _current_tenant.set(tenant_id)

def get_tenant():
    return _current_tenant.get()

class TenantFilter(logging.Filter):
    def filter(self, record):
        record.tenant = get_tenant()
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "tenant": getattr(record, "tenant", "unknown-tenant"),
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)

def setup_logger():
    logger = logging.getLogger("NFL-sim-motor")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(TenantFilter())
    logger.handlers = [handler]
    return logger

# Usage:
# from observability.logging import setup_logger, set_tenant
# set_tenant("team-abc")
# logger = setup_logger()
# logger.info("Simulation started", extra={"extra": {"module": "simulator"}})