"""
Structured exception handling for simulation robustness.
Provides consistent error envelopes with play metadata and exception details.
"""
import traceback
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PlayContext:
    """Metadata for the current play context."""
    play_id: str
    game_id: Optional[str] = None
    quarter: Optional[int] = None
    down: Optional[int] = None
    distance: Optional[int] = None
    field_position: Optional[int] = None
    team: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ErrorEnvelope:
    """Consistent error envelope with play metadata and exception details."""
    play_context: PlayContext
    exception_type: str
    exception_message: str
    stacktrace: str
    timestamp: float
    severity: str = "error"  # error, warning, critical
    recoverable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "play_context": asdict(self.play_context),
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "stacktrace": self.stacktrace,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "recoverable": self.recoverable
        }


class SimulationError(Exception):
    """Base exception for simulation-related errors."""
    def __init__(self, message: str, play_context: Optional[PlayContext] = None, recoverable: bool = True):
        super().__init__(message)
        self.play_context = play_context
        self.recoverable = recoverable


class PlayExecutionError(SimulationError):
    """Error during play execution."""
    pass


class StateTransitionError(SimulationError):
    """Error during state transition."""
    pass


class PolicySelectionError(SimulationError):
    """Error during policy/play selection."""
    pass


def create_error_envelope(exception: Exception, play_context: PlayContext, severity: str = "error") -> ErrorEnvelope:
    """Create a structured error envelope from an exception."""
    return ErrorEnvelope(
        play_context=play_context,
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        stacktrace=traceback.format_exc(),
        timestamp=time.time(),
        severity=severity,
        recoverable=getattr(exception, 'recoverable', True)
    )


def safe_execute_with_context(func, play_context: PlayContext, *args, **kwargs):
    """
    Execute a function with error handling and context capture.
    Returns (result, error_envelope) tuple.
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        error_envelope = create_error_envelope(e, play_context)
        return None, error_envelope