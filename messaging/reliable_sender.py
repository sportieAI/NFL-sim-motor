"""
Reliable messaging system with message IDs, exponential backoff retry logic,
and JSON Schema validation for outbound messages.
"""

import json
import time
import uuid
import random
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from abc import ABC, abstractmethod

try:
    import jsonschema

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class MessageStatus(Enum):
    """Status of a message."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class MessagePriority(Enum):
    """Priority levels for messages."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MessageEnvelope:
    """Envelope containing message metadata and payload."""

    message_id: str
    destination: str
    payload: Dict[str, Any]
    priority: MessagePriority
    created_at: float
    expires_at: Optional[float]
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    last_attempt: Optional[float] = None
    error_message: Optional[str] = None
    schema_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["priority"] = self.priority.value
        result["status"] = self.status.value
        return result

    def is_expired(self) -> bool:
        """Check if message has expired."""
        return self.expires_at is not None and time.time() > self.expires_at

    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return (
            self.retry_count < self.max_retries
            and not self.is_expired()
            and self.status in [MessageStatus.FAILED, MessageStatus.RETRYING]
        )


class RetryStrategy:
    """Exponential backoff retry strategy."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for given retry count."""
        delay = self.base_delay * (self.exponential_base**retry_count)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add random jitter (±25%)
            jitter_amount = delay * 0.25
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)


class MessageTransport(ABC):
    """Abstract base class for message transports."""

    @abstractmethod
    async def send(self, envelope: MessageEnvelope) -> bool:
        """Send a message. Returns True if successful."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if transport is available."""
        pass


class HTTPTransport(MessageTransport):
    """HTTP-based message transport."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    async def send(self, envelope: MessageEnvelope) -> bool:
        """Send message via HTTP POST."""
        try:
            # In a real implementation, this would use aiohttp or similar
            # For now, simulate HTTP request
            await asyncio.sleep(0.1)  # Simulate network delay

            # Simulate occasional failures for testing
            if random.random() < 0.1:  # 10% failure rate
                raise Exception("Simulated network error")

            self.logger.info(
                f"HTTP message sent: {envelope.message_id} to {envelope.destination}"
            )
            return True

        except Exception as e:
            self.logger.error(f"HTTP send failed for {envelope.message_id}: {e}")
            return False

    def is_available(self) -> bool:
        """Check if HTTP transport is available."""
        # In real implementation, would check network connectivity
        return True


class WebSocketTransport(MessageTransport):
    """WebSocket-based message transport."""

    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.connected = True  # Simulate connected state
        self.logger = logging.getLogger(__name__)

    async def send(self, envelope: MessageEnvelope) -> bool:
        """Send message via WebSocket."""
        try:
            # Simulate WebSocket send
            await asyncio.sleep(0.05)  # Simulate send delay

            # Simulate occasional failures
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("WebSocket connection lost")

            self.logger.info(f"WebSocket message sent: {envelope.message_id}")
            return True

        except Exception as e:
            self.logger.error(f"WebSocket send failed for {envelope.message_id}: {e}")
            return False

    def is_available(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected


class MessageValidator:
    """Validates messages against JSON schemas."""

    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

        # Load default schemas
        self._load_default_schemas()

    def _load_default_schemas(self):
        """Load default message schemas."""
        # Game event schema
        self.schemas["game_event"] = {
            "type": "object",
            "required": ["event_type", "timestamp", "game_id"],
            "properties": {
                "event_type": {"type": "string"},
                "timestamp": {"type": "number"},
                "game_id": {"type": "string"},
                "play_id": {"type": "string"},
                "team": {"type": "string"},
                "data": {"type": "object"},
            },
        }

        # Error report schema
        self.schemas["error_report"] = {
            "type": "object",
            "required": ["error_type", "message", "timestamp"],
            "properties": {
                "error_type": {"type": "string"},
                "message": {"type": "string"},
                "timestamp": {"type": "number"},
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                },
                "context": {"type": "object"},
            },
        }

        # Simulation result schema
        self.schemas["simulation_result"] = {
            "type": "object",
            "required": ["simulation_id", "timestamp", "result"],
            "properties": {
                "simulation_id": {"type": "string"},
                "timestamp": {"type": "number"},
                "result": {"type": "object"},
                "metrics": {"type": "object"},
                "metadata": {"type": "object"},
            },
        }

    def register_schema(self, schema_name: str, schema: Dict[str, Any]):
        """Register a new message schema."""
        self.schemas[schema_name] = schema
        self.logger.info(f"Registered schema: {schema_name}")

    def validate(
        self, payload: Dict[str, Any], schema_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate a payload against a schema."""
        if not JSONSCHEMA_AVAILABLE:
            self.logger.warning("jsonschema not available, skipping validation")
            return True, None

        if schema_name not in self.schemas:
            return False, f"Schema '{schema_name}' not found"

        try:
            jsonschema.validate(payload, self.schemas[schema_name])
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class ReliableMessageSender:
    """
    Reliable message sender with retry logic, validation, and multiple transports.
    """

    def __init__(
        self,
        retry_strategy: Optional[RetryStrategy] = None,
        validator: Optional[MessageValidator] = None,
    ):
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.validator = validator or MessageValidator()
        self.transports: Dict[str, MessageTransport] = {}
        self.pending_messages: Dict[str, MessageEnvelope] = {}
        self.sent_messages: List[MessageEnvelope] = []
        self.failed_messages: List[MessageEnvelope] = []

        self.logger = logging.getLogger(__name__)
        self.is_running = False

        # Message queues by priority
        self.message_queues: Dict[MessagePriority, List[MessageEnvelope]] = {
            priority: [] for priority in MessagePriority
        }

    def register_transport(self, name: str, transport: MessageTransport):
        """Register a message transport."""
        self.transports[name] = transport
        self.logger.info(f"Registered transport: {name}")

    async def send_message(
        self,
        destination: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        schema_name: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """
        Send a message with reliability guarantees.

        Returns message ID for tracking.
        """
        # Generate unique message ID
        message_id = str(uuid.uuid4())

        # Validate payload if schema provided
        if schema_name:
            is_valid, error = self.validator.validate(payload, schema_name)
            if not is_valid:
                self.logger.error(f"Message validation failed: {error}")
                raise ValueError(f"Message validation failed: {error}")

        # Create message envelope
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        envelope = MessageEnvelope(
            message_id=message_id,
            destination=destination,
            payload=payload,
            priority=priority,
            created_at=time.time(),
            expires_at=expires_at,
            schema_name=schema_name,
        )

        # Add to pending messages
        self.pending_messages[message_id] = envelope

        # Add to priority queue
        self.message_queues[priority].append(envelope)

        # Try immediate send
        await self._attempt_send(envelope)

        return message_id

    async def _attempt_send(self, envelope: MessageEnvelope) -> bool:
        """Attempt to send a message."""
        if envelope.is_expired():
            envelope.status = MessageStatus.EXPIRED
            self._move_to_failed(envelope)
            return False

        # Find available transport
        transport = self._select_transport(envelope.destination)
        if not transport:
            self.logger.warning(f"No available transport for {envelope.destination}")
            return False

        envelope.last_attempt = time.time()

        try:
            success = await transport.send(envelope)

            if success:
                envelope.status = MessageStatus.SENT
                self._move_to_sent(envelope)
                return True
            else:
                envelope.retry_count += 1
                envelope.status = MessageStatus.FAILED
                envelope.error_message = "Transport send failed"

                if envelope.can_retry():
                    envelope.status = MessageStatus.RETRYING
                    await self._schedule_retry(envelope)
                else:
                    self._move_to_failed(envelope)

                return False

        except Exception as e:
            envelope.retry_count += 1
            envelope.status = MessageStatus.FAILED
            envelope.error_message = str(e)

            self.logger.error(f"Send attempt failed for {envelope.message_id}: {e}")

            if envelope.can_retry():
                envelope.status = MessageStatus.RETRYING
                await self._schedule_retry(envelope)
            else:
                self._move_to_failed(envelope)

            return False

    async def _schedule_retry(self, envelope: MessageEnvelope):
        """Schedule a retry for a failed message."""
        delay = self.retry_strategy.get_delay(envelope.retry_count)

        self.logger.info(
            f"Scheduling retry for {envelope.message_id} in {delay:.2f}s "
            f"(attempt {envelope.retry_count + 1}/{envelope.max_retries})"
        )

        # In a real implementation, this would use a proper task scheduler
        asyncio.create_task(self._delayed_retry(envelope, delay))

    async def _delayed_retry(self, envelope: MessageEnvelope, delay: float):
        """Execute a delayed retry."""
        await asyncio.sleep(delay)

        if envelope.message_id in self.pending_messages:
            await self._attempt_send(envelope)

    def _select_transport(self, destination: str) -> Optional[MessageTransport]:
        """Select an available transport for the destination."""
        # Simple selection logic - could be enhanced with load balancing
        for transport in self.transports.values():
            if transport.is_available():
                return transport
        return None

    def _move_to_sent(self, envelope: MessageEnvelope):
        """Move message to sent list."""
        if envelope.message_id in self.pending_messages:
            del self.pending_messages[envelope.message_id]

        self.sent_messages.append(envelope)

        # Keep only recent sent messages
        if len(self.sent_messages) > 1000:
            self.sent_messages = self.sent_messages[-1000:]

    def _move_to_failed(self, envelope: MessageEnvelope):
        """Move message to failed list."""
        if envelope.message_id in self.pending_messages:
            del self.pending_messages[envelope.message_id]

        self.failed_messages.append(envelope)

        # Keep only recent failed messages
        if len(self.failed_messages) > 500:
            self.failed_messages = self.failed_messages[-500:]

    def get_message_status(self, message_id: str) -> Optional[MessageStatus]:
        """Get the status of a message."""
        # Check pending messages
        if message_id in self.pending_messages:
            return self.pending_messages[message_id].status

        # Check sent messages
        for msg in self.sent_messages:
            if msg.message_id == message_id:
                return msg.status

        # Check failed messages
        for msg in self.failed_messages:
            if msg.message_id == message_id:
                return msg.status

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get messaging statistics."""
        total_sent = len(self.sent_messages)
        total_failed = len(self.failed_messages)
        total_pending = len(self.pending_messages)

        return {
            "total_sent": total_sent,
            "total_failed": total_failed,
            "total_pending": total_pending,
            "success_rate": (
                total_sent / (total_sent + total_failed)
                if (total_sent + total_failed) > 0
                else 1.0
            ),
            "pending_by_priority": {
                priority.name: len(messages)
                for priority, messages in self.message_queues.items()
            },
            "failed_by_reason": {},  # Could be enhanced to track failure reasons
        }

    async def process_pending_messages(self):
        """Process all pending messages (background task)."""
        self.is_running = True

        while self.is_running:
            try:
                # Process messages by priority (highest first)
                for priority in sorted(
                    MessagePriority, key=lambda p: p.value, reverse=True
                ):
                    queue = self.message_queues[priority]

                    # Process a batch of messages from this priority level
                    batch_size = min(10, len(queue))
                    for _ in range(batch_size):
                        if queue:
                            envelope = queue.pop(0)
                            if envelope.message_id in self.pending_messages:
                                await self._attempt_send(envelope)

                # Sleep before next processing cycle
                await asyncio.sleep(1.0)

            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(5.0)  # Longer sleep on error

    def stop(self):
        """Stop the message processor."""
        self.is_running = False
