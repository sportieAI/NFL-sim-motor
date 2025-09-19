"""
Observability module for NFL simulation engine.
Provides structured logging, metrics, and tracing.
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Dict, Any, Optional
import os


class StructuredLogger:
    """Structured JSON logger with correlation IDs."""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Create formatter for JSON output
        formatter = self._create_json_formatter()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        log_file = os.environ.get("LOG_FILE")
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _create_json_formatter(self):
        """Create JSON formatter for structured logging."""

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": time.time(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Add correlation ID if available
                correlation_id = getattr(record, "correlation_id", None)
                if correlation_id:
                    log_entry["correlation_id"] = correlation_id

                # Add extra fields
                for key, value in record.__dict__.items():
                    if key not in [
                        "name",
                        "msg",
                        "args",
                        "levelname",
                        "levelno",
                        "pathname",
                        "filename",
                        "module",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "processName",
                        "process",
                        "message",
                    ]:
                        log_entry[key] = value

                return json.dumps(log_entry)

        return JSONFormatter()

    def info(self, message: str, **kwargs):
        """Log info message with optional fields."""
        extra = {"correlation_id": self._get_correlation_id(), **kwargs}
        self.logger.info(message, extra=extra)

    def error(self, message: str, **kwargs):
        """Log error message with optional fields."""
        extra = {"correlation_id": self._get_correlation_id(), **kwargs}
        self.logger.error(message, extra=extra)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional fields."""
        extra = {"correlation_id": self._get_correlation_id(), **kwargs}
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional fields."""
        extra = {"correlation_id": self._get_correlation_id(), **kwargs}
        self.logger.debug(message, extra=extra)

    def _get_correlation_id(self) -> str:
        """Get or create correlation ID for current context."""
        # In a real implementation, this would use context variables
        # For now, generate a new UUID for each call
        return str(uuid.uuid4())


class MetricsCollector:
    """Collects and exports metrics for monitoring."""

    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.histograms = {}

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        key = self._make_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        key = self._make_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)

    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge value."""
        key = self._make_key(name, tags)
        self.metrics[key] = value

    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create metric key with tags."""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name},{tag_str}"
        return name

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": self.counters,
            "histograms": {
                k: {"count": len(v), "avg": sum(v) / len(v) if v else 0}
                for k, v in self.histograms.items()
            },
            "gauges": self.metrics,
        }


class PerformanceTracer:
    """Performance tracing for simulation operations."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.active_spans = {}

    @contextmanager
    def trace_operation(self, operation_name: str, **metadata):
        """Trace a simulation operation."""
        span_id = str(uuid.uuid4())
        start_time = time.time()

        self.logger.info(
            f"Starting {operation_name}",
            span_id=span_id,
            operation=operation_name,
            **metadata,
        )

        try:
            yield span_id
            duration = time.time() - start_time
            self.logger.info(
                f"Completed {operation_name}",
                span_id=span_id,
                operation=operation_name,
                duration_ms=duration * 1000,
                status="success",
                **metadata,
            )
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed {operation_name}",
                span_id=span_id,
                operation=operation_name,
                duration_ms=duration * 1000,
                status="error",
                error=str(e),
                **metadata,
            )
            raise


# Global instances
logger = StructuredLogger("nfl_sim_engine")
metrics = MetricsCollector()
tracer = PerformanceTracer(logger)


def log_simulation_event(event_type: str, **data):
    """Log a simulation event with structured data."""
    logger.info(f"Simulation event: {event_type}", event_type=event_type, **data)


def track_performance_metric(metric_name: str, value: float, **tags):
    """Track a performance metric."""
    metrics.record_histogram(f"simulation.{metric_name}", value, tags)


def log_play_execution(play_call: Dict, outcome: Dict, execution_time_ms: float):
    """Log play execution with full context."""
    logger.info(
        "Play executed",
        play_type=play_call.get("type"),
        yards_gained=outcome.get("yards"),
        execution_time_ms=execution_time_ms,
        success=outcome.get("success", False),
    )

    track_performance_metric(
        "play_execution_time",
        execution_time_ms,
        play_type=play_call.get("type", "unknown"),
    )
