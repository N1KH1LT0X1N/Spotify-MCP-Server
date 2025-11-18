"""Circuit breaker pattern implementation for preventing cascade failures."""

import asyncio
import time
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Optional metrics integration
try:
    from spotify_mcp.infrastructure.metrics import get_metrics_collector
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject all requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker to prevent cascade failures.

    When a service is failing, the circuit breaker "opens" and fails fast
    instead of hammering the failing service with retries. After a timeout,
    it enters "half-open" state to test if the service recovered.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        timeout: float = 30.0
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name for identification
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery (half-open)
            success_threshold: Successes in half-open before closing
            timeout: Request timeout in seconds
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout = timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.utcnow()

        # Statistics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_rejections = 0

        # Initialize metrics if available
        if METRICS_AVAILABLE:
            collector = get_metrics_collector()
            collector.update_circuit_breaker_state(self.name, self.state.value)

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            TimeoutError: If call exceeds timeout
            Any exception raised by the function
        """
        self.total_calls += 1

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = datetime.utcnow()

                # Update metrics
                if METRICS_AVAILABLE:
                    collector = get_metrics_collector()
                    collector.update_circuit_breaker_state(self.name, self.state.value)
            else:
                self.total_rejections += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable until recovery timeout expires."
                )

        # Execute call with timeout
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout
            )

            self._on_success()
            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"Circuit breaker {self.name}: Call timeout after {self.timeout}s"
            )
            self._on_failure()
            raise

        except Exception as e:
            logger.warning(
                f"Circuit breaker {self.name}: Call failed - {type(e).__name__}: {e}"
            )
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.total_successes += 1
        self.failure_count = 0

        # Record success metric
        if METRICS_AVAILABLE:
            collector = get_metrics_collector()
            collector.record_circuit_breaker_success(self.name)

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.success_threshold:
                logger.info(f"Circuit breaker {self.name} closing after successful recovery")
                self.state = CircuitState.CLOSED
                self.success_count = 0
                self.last_state_change = datetime.utcnow()

                # Update metrics
                if METRICS_AVAILABLE:
                    collector = get_metrics_collector()
                    collector.update_circuit_breaker_state(self.name, self.state.value)

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        # Record failure metric
        if METRICS_AVAILABLE:
            collector = get_metrics_collector()
            collector.record_circuit_breaker_failure(self.name)

        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker {self.name} reopening after failed recovery attempt")
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.last_state_change = datetime.utcnow()

            # Update metrics
            if METRICS_AVAILABLE:
                collector = get_metrics_collector()
                collector.update_circuit_breaker_state(self.name, self.state.value)

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.warning(
                    f"Circuit breaker {self.name} opening after {self.failure_count} failures"
                )
                self.state = CircuitState.OPEN
                self.last_state_change = datetime.utcnow()

                # Update metrics
                if METRICS_AVAILABLE:
                    collector = get_metrics_collector()
                    collector.update_circuit_breaker_state(self.name, self.state.value)

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics.

        Returns:
            Dictionary with circuit breaker stats
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_rejections": self.total_rejections,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_state_change": self.last_state_change.isoformat(),
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "config": {
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "success_threshold": self.success_threshold,
                "timeout": self.timeout
            }
        }

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.utcnow()
        logger.info(f"Circuit breaker {self.name} has been reset")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        """Initialize circuit breaker registry."""
        self.breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        timeout: float = 30.0
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one.

        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
            success_threshold: Successes needed to close circuit
            timeout: Request timeout

        Returns:
            Circuit breaker instance
        """
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold,
                timeout=timeout
            )

        return self.breakers[name]

    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self.breakers.items()
        }

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()


# Global registry
_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """
    Get global circuit breaker registry (singleton pattern).

    Returns:
        Global circuit breaker registry
    """
    global _registry
    if _registry is None:
        _registry = CircuitBreakerRegistry()
    return _registry
