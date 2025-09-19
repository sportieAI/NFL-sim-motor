"""
Reliability module for NFL simulation engine.
Provides message queues, retry logic, and fault tolerance.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from collections import deque
import random
import math


@dataclass
class Message:
    """Message envelope for reliable messaging."""

    id: str
    payload: Dict[str, Any]
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0  # Higher numbers = higher priority

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


class ExponentialBackoff:
    """Exponential backoff with jitter for retries."""

    def __init__(
        self, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for retry attempt."""
        delay = min(self.base_delay * (2**retry_count), self.max_delay)

        if self.jitter:
            # Add jitter to prevent thundering herd
            delay *= 0.5 + random.random() * 0.5

        return delay


class DeadLetterQueue:
    """Dead letter queue for failed messages."""

    def __init__(self, max_size: int = 10000):
        self.messages = deque(maxlen=max_size)
        self.max_size = max_size

    def add_message(self, message: Message, error: str):
        """Add failed message to DLQ."""
        dlq_entry = {"message": message, "error": error, "dlq_timestamp": time.time()}
        self.messages.append(dlq_entry)

    def get_messages(self, limit: int = 100) -> list:
        """Get messages from DLQ."""
        return list(self.messages)[-limit:]

    def size(self) -> int:
        """Get DLQ size."""
        return len(self.messages)


class ReliableMessageBroker:
    """Reliable message broker with retry and DLQ."""

    def __init__(self):
        self.queues = {}
        self.consumers = {}
        self.dlq = DeadLetterQueue()
        self.backoff = ExponentialBackoff()
        self.retry_queue = deque()
        self.processing = False

    def create_queue(self, queue_name: str):
        """Create a new queue."""
        if queue_name not in self.queues:
            self.queues[queue_name] = deque()

    def publish(
        self, queue_name: str, payload: Dict[str, Any], priority: int = 0
    ) -> str:
        """Publish message to queue."""
        self.create_queue(queue_name)

        message = Message(
            id=str(uuid.uuid4()),
            payload=payload,
            timestamp=time.time(),
            priority=priority,
        )

        # Insert by priority (higher priority first)
        queue = self.queues[queue_name]
        inserted = False
        for i, existing_msg in enumerate(queue):
            if message.priority > existing_msg.priority:
                queue.insert(i, message)
                inserted = True
                break

        if not inserted:
            queue.append(message)

        return message.id

    def subscribe(
        self, queue_name: str, consumer_func: Callable[[Dict[str, Any]], bool]
    ):
        """Subscribe consumer to queue."""
        self.create_queue(queue_name)
        self.consumers[queue_name] = consumer_func

    def consume_message(self, queue_name: str) -> Optional[Message]:
        """Consume single message from queue."""
        if queue_name in self.queues and self.queues[queue_name]:
            return self.queues[queue_name].popleft()
        return None

    def process_message(self, queue_name: str, message: Message) -> bool:
        """Process message with consumer."""
        if queue_name not in self.consumers:
            return False

        try:
            consumer = self.consumers[queue_name]
            success = consumer(message.payload)

            if not success and message.retry_count < message.max_retries:
                # Schedule retry
                message.retry_count += 1
                retry_delay = self.backoff.get_delay(message.retry_count)
                retry_time = time.time() + retry_delay

                self.retry_queue.append((retry_time, queue_name, message))
                return False
            elif not success:
                # Send to DLQ
                self.dlq.add_message(message, "Max retries exceeded")
                return False

            return True

        except Exception as e:
            if message.retry_count < message.max_retries:
                message.retry_count += 1
                retry_delay = self.backoff.get_delay(message.retry_count)
                retry_time = time.time() + retry_delay

                self.retry_queue.append((retry_time, queue_name, message))
            else:
                self.dlq.add_message(message, str(e))

            return False

    def process_retries(self):
        """Process messages in retry queue."""
        current_time = time.time()
        ready_retries = []

        while self.retry_queue:
            retry_time, queue_name, message = self.retry_queue[0]
            if retry_time <= current_time:
                ready_retries.append((queue_name, message))
                self.retry_queue.popleft()
            else:
                break

        for queue_name, message in ready_retries:
            self.process_message(queue_name, message)

    def run_consumer_loop(self, max_iterations: int = None):
        """Run consumer loop."""
        iteration = 0
        self.processing = True

        while self.processing and (
            max_iterations is None or iteration < max_iterations
        ):
            processed_any = False

            # Process regular messages
            for queue_name in self.queues:
                message = self.consume_message(queue_name)
                if message:
                    self.process_message(queue_name, message)
                    processed_any = True

            # Process retries
            self.process_retries()

            # Sleep briefly if no messages processed
            if not processed_any:
                time.sleep(0.1)

            iteration += 1

    def stop(self):
        """Stop consumer loop."""
        self.processing = False

    def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics."""
        return {
            "queues": {name: len(queue) for name, queue in self.queues.items()},
            "retry_queue_size": len(self.retry_queue),
            "dlq_size": self.dlq.size(),
            "consumers": list(self.consumers.keys()),
        }


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# Global reliability instances
message_broker = ReliableMessageBroker()
circuit_breaker = CircuitBreaker()


def publish_simulation_event(
    event_type: str, data: Dict[str, Any], priority: int = 0
) -> str:
    """Publish simulation event to message broker."""
    payload = {"event_type": event_type, "data": data, "timestamp": time.time()}
    return message_broker.publish("simulation_events", payload, priority)


def subscribe_to_simulation_events(consumer_func: Callable[[Dict[str, Any]], bool]):
    """Subscribe to simulation events."""
    message_broker.subscribe("simulation_events", consumer_func)


def with_circuit_breaker(func: Callable):
    """Decorator to add circuit breaker protection."""

    def wrapper(*args, **kwargs):
        return circuit_breaker.call(func, *args, **kwargs)

    return wrapper
