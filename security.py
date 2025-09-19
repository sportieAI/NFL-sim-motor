"""
Security module for NFL simulation engine.
Handles API authentication, rate limiting, and access control.
"""

import hashlib
import hmac
import time
from typing import Dict, List, Optional
from collections import defaultdict, deque
import os


class APIKeyManager:
    """Manages API key authentication."""

    def __init__(self):
        self.valid_keys = set()
        self.key_metadata = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from environment or configuration."""
        # In production, this would load from a secure key store
        api_keys = os.environ.get("NFL_SIM_API_KEYS", "").split(",")
        for key in api_keys:
            if key.strip():
                self.valid_keys.add(key.strip())
                self.key_metadata[key.strip()] = {
                    "created_at": time.time(),
                    "last_used": None,
                    "usage_count": 0,
                }

    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key."""
        if api_key in self.valid_keys:
            self.key_metadata[api_key]["last_used"] = time.time()
            self.key_metadata[api_key]["usage_count"] += 1
            return True
        return False

    def get_key_metadata(self, api_key: str) -> Optional[Dict]:
        """Get metadata for an API key."""
        return self.key_metadata.get(api_key)


class RateLimiter:
    """Rate limiting implementation using sliding window."""

    def __init__(self, max_requests: int = 1000, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for the given identifier."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()

        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True

        return False

    def get_usage(self, identifier: str) -> Dict[str, int]:
        """Get current usage for identifier."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()

        return {
            "current_requests": len(self.requests[identifier]),
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "reset_time": (
                int(self.requests[identifier][0] + self.window_seconds)
                if self.requests[identifier]
                else int(now)
            ),
        }


class IPAllowlist:
    """IP address allowlist for admin interfaces."""

    def __init__(self):
        self.allowed_ips = set()
        self.allowed_ranges = []
        self._load_allowlist()

    def _load_allowlist(self):
        """Load IP allowlist from environment."""
        allowed_ips = os.environ.get("NFL_SIM_ALLOWED_IPS", "").split(",")
        for ip in allowed_ips:
            ip = ip.strip()
            if ip:
                if "/" in ip:
                    self.allowed_ranges.append(ip)
                else:
                    self.allowed_ips.add(ip)

    def is_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if ip_address in self.allowed_ips:
            return True

        # Check IP ranges (simplified - would use ipaddress module in production)
        for ip_range in self.allowed_ranges:
            if ip_address.startswith(ip_range.split("/")[0][:-1]):
                return True

        return False


class SignedRequestValidator:
    """Validates signed requests using HMAC."""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.environ.get(
            "NFL_SIM_SECRET_KEY", "default-secret"
        )

    def generate_signature(self, payload: str, timestamp: str) -> str:
        """Generate HMAC signature for payload."""
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def validate_signature(self, payload: str, timestamp: str, signature: str) -> bool:
        """Validate HMAC signature."""
        # Check timestamp freshness (prevent replay attacks)
        current_time = time.time()
        request_time = float(timestamp)
        if abs(current_time - request_time) > 300:  # 5 minute window
            return False

        expected_signature = self.generate_signature(payload, timestamp)
        return hmac.compare_digest(signature, expected_signature)


class HoneypotEndpoints:
    """Honeypot endpoints for detecting attacks."""

    def __init__(self):
        self.access_log = []
        self.suspicious_ips = set()

    def log_access(self, ip_address: str, endpoint: str, user_agent: str = None):
        """Log access to honeypot endpoint."""
        access_record = {
            "ip_address": ip_address,
            "endpoint": endpoint,
            "timestamp": time.time(),
            "user_agent": user_agent,
        }
        self.access_log.append(access_record)
        self.suspicious_ips.add(ip_address)

        # In production, this would send alerts to security team
        print(f"SECURITY ALERT: Honeypot access from {ip_address} to {endpoint}")

    def get_suspicious_activity(self) -> List[Dict]:
        """Get recent suspicious activity."""
        recent_window = time.time() - 3600  # Last hour
        return [
            record for record in self.access_log if record["timestamp"] > recent_window
        ]

    def is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP is marked as suspicious."""
        return ip_address in self.suspicious_ips


# Global security instances
api_key_manager = APIKeyManager()
rate_limiter = RateLimiter()
ip_allowlist = IPAllowlist()
signature_validator = SignedRequestValidator()
honeypot = HoneypotEndpoints()


def require_api_key(api_key: str) -> bool:
    """Decorator function to require API key."""
    return api_key_manager.validate_api_key(api_key)


def require_rate_limit(identifier: str) -> bool:
    """Check rate limiting for identifier."""
    return rate_limiter.is_allowed(identifier)


def require_ip_allowlist(ip_address: str) -> bool:
    """Check IP allowlist."""
    return ip_allowlist.is_allowed(ip_address)


def require_signed_request(payload: str, timestamp: str, signature: str) -> bool:
    """Validate signed request."""
    return signature_validator.validate_signature(payload, timestamp, signature)
