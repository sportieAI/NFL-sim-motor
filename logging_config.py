"""
Structured logging system with correlation IDs and production-ready features.
"""
import logging
import logging.handlers
import json
import uuid
import time
import sys
import os
from typing import Dict, Any, Optional
from contextlib import contextmanager
from threading import local
from datetime import datetime

from config import config

# Thread-local storage for correlation IDs
_local = local()


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record):
        # Get correlation ID from thread-local storage
        correlation_id = getattr(_local, 'correlation_id', None)
        record.correlation_id = correlation_id or 'no-correlation-id'
        
        # Add additional context
        record.timestamp = datetime.utcnow().isoformat()
        record.environment = config.environment
        
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    
    def format(self, record):
        log_entry = {
            'timestamp': record.timestamp,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': record.correlation_id,
            'environment': record.environment,
            'hostname': self.hostname,
            'process_id': os.getpid(),
            'thread_id': record.thread,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text',
                          'stack_info', 'correlation_id', 'timestamp', 'environment']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class StructuredLogger:
    """Enhanced logger with correlation ID and structured logging support."""
    
    def __init__(self, name: str = None):
        self.name = name or __name__
        self.logger = logging.getLogger(self.name)
        self._configured = False
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger with appropriate handlers and formatters."""
        if self._configured:
            return
        
        self.logger.setLevel(getattr(logging, config.get('logging.level', 'INFO')))
        
        # Remove existing handlers to avoid duplication
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # File handler (if configured)
        log_file = config.get('logging.output_file')
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=config.get('logging.max_file_size_mb', 100) * 1024 * 1024,
                    backupCount=config.get('logging.backup_count', 5)
                )
            except (OSError, IOError) as e:
                # Fallback to console only if file handler fails
                print(f"Warning: Could not create file handler for {log_file}: {e}")
                file_handler = None
        else:
            file_handler = None
        
        # Choose formatter based on configuration
        if config.get('logging.format') == 'json':
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s'
            )
        
        # Configure handlers
        console_handler.setFormatter(formatter)
        console_handler.addFilter(CorrelationIDFilter())
        self.logger.addHandler(console_handler)
        
        if file_handler:
            file_handler.setFormatter(formatter)
            file_handler.addFilter(CorrelationIDFilter())
            self.logger.addHandler(file_handler)
        
        self._configured = True
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra context."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra context."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra context."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra context."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra context."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)
    
    def log_possession_start(self, team: str, down: int, distance: int, field_position: int, **kwargs):
        """Log possession start with football-specific context."""
        self.info(
            "Possession started",
            event_type="possession_start",
            team=team,
            down=down,
            distance=distance,
            field_position=field_position,
            **kwargs
        )
    
    def log_play_result(self, play_type: str, result: str, yards_gained: int, **kwargs):
        """Log play result with football-specific context."""
        self.info(
            "Play completed",
            event_type="play_result",
            play_type=play_type,
            result=result,
            yards_gained=yards_gained,
            **kwargs
        )
    
    def log_simulation_metrics(self, duration: float, plays_simulated: int, **kwargs):
        """Log simulation performance metrics."""
        self.info(
            "Simulation completed",
            event_type="simulation_metrics",
            duration_seconds=duration,
            plays_simulated=plays_simulated,
            plays_per_second=plays_simulated / duration if duration > 0 else 0,
            **kwargs
        )


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return getattr(_local, 'correlation_id', None)


def set_correlation_id(correlation_id: str):
    """Set the correlation ID for the current thread."""
    _local.correlation_id = correlation_id


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


@contextmanager
def correlation_context(correlation_id: Optional[str] = None):
    """Context manager for setting correlation ID."""
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    old_correlation_id = getattr(_local, 'correlation_id', None)
    set_correlation_id(correlation_id)
    
    try:
        yield correlation_id
    finally:
        if old_correlation_id is not None:
            set_correlation_id(old_correlation_id)
        else:
            # Remove correlation ID if it wasn't set before
            if hasattr(_local, 'correlation_id'):
                delattr(_local, 'correlation_id')


# Global logger instance
logger = StructuredLogger('nfl-sim-motor')


def get_logger(name: str = None) -> StructuredLogger:
    """Get a logger instance with the specified name."""
    return StructuredLogger(name)


# Performance monitoring utilities
class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger_instance: StructuredLogger = None):
        self.operation_name = operation_name
        self.logger = logger_instance or logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation_name}", operation=self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation_name}",
                operation=self.operation_name,
                duration_seconds=duration,
                success=True
            )
        else:
            self.logger.error(
                f"Failed {self.operation_name}",
                operation=self.operation_name,
                duration_seconds=duration,
                success=False,
                error_type=exc_type.__name__,
                error_message=str(exc_val)
            )
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None