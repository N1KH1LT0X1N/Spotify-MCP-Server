"""
Resilience infrastructure for Spotify MCP Server.

Provides production-grade reliability patterns:
- Circuit breaker for preventing cascade failures
- Rate limiting with token bucket algorithm
- Comprehensive health check system
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerOpenError,
    CircuitState,
    get_circuit_breaker_registry
)

from .rate_limiter import (
    TokenBucket,
    RateLimiter,
    SpotifyRateLimiter,
    get_rate_limiter,
    init_rate_limiter
)

from .health_checks import (
    HealthCheck,
    HealthCheckSystem,
    HealthStatus,
    get_health_system,
    init_health_system,
    check_spotify_api,
    check_cache,
    check_metrics
)

from .retry import (
    RetryPolicy,
    RetryExhaustedError,
    retry,
    register_retry_policy,
    get_retry_policy,
    SPOTIFY_API_RETRY_POLICY,
    CRITICAL_RETRY_POLICY,
    QUICK_RETRY_POLICY
)

from .fallback import (
    Fallback,
    FallbackChain,
    FallbackExhaustedError,
    with_fallback,
    return_none,
    return_empty_dict,
    return_empty_list,
    return_error_response,
    cache_fallback,
    default_value_fallback
)

__all__ = [
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerRegistry',
    'CircuitBreakerOpenError',
    'CircuitState',
    'get_circuit_breaker_registry',

    # Rate Limiter
    'TokenBucket',
    'RateLimiter',
    'SpotifyRateLimiter',
    'get_rate_limiter',
    'init_rate_limiter',

    # Health Checks
    'HealthCheck',
    'HealthCheckSystem',
    'HealthStatus',
    'get_health_system',
    'init_health_system',
    'check_spotify_api',
    'check_cache',
    'check_metrics',

    # Retry Logic
    'RetryPolicy',
    'RetryExhaustedError',
    'retry',
    'register_retry_policy',
    'get_retry_policy',
    'SPOTIFY_API_RETRY_POLICY',
    'CRITICAL_RETRY_POLICY',
    'QUICK_RETRY_POLICY',

    # Fallback / Graceful Degradation
    'Fallback',
    'FallbackChain',
    'FallbackExhaustedError',
    'with_fallback',
    'return_none',
    'return_empty_dict',
    'return_empty_list',
    'return_error_response',
    'cache_fallback',
    'default_value_fallback',
]
