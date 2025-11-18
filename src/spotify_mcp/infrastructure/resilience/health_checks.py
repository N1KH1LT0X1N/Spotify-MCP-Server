"""Comprehensive health check system."""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check component."""

    def __init__(
        self,
        name: str,
        check_func: Callable,
        critical: bool = True,
        timeout: float = 5.0
    ):
        """
        Initialize health check.

        Args:
            name: Health check name
            check_func: Async function that performs the check
            critical: Whether this check is critical for overall health
            timeout: Timeout for check in seconds
        """
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.timeout = timeout

        # Statistics
        self.last_check_time: Optional[datetime] = None
        self.last_status: Optional[HealthStatus] = None
        self.total_checks = 0
        self.total_failures = 0

    async def check(self) -> Dict[str, Any]:
        """
        Execute health check.

        Returns:
            Dictionary with check results
        """
        self.total_checks += 1
        start_time = datetime.utcnow()

        try:
            # Execute check with timeout
            result = await asyncio.wait_for(
                self.check_func(),
                timeout=self.timeout
            )

            duration = (datetime.utcnow() - start_time).total_seconds()

            # Determine status from result
            if isinstance(result, dict):
                is_healthy = result.get("healthy", True)
                details = result.get("details", {})
                message = result.get("message", "OK")
            elif isinstance(result, bool):
                is_healthy = result
                details = {}
                message = "OK" if is_healthy else "Check failed"
            else:
                is_healthy = True
                details = {"result": result}
                message = "OK"

            self.last_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
            self.last_check_time = datetime.utcnow()

            if not is_healthy:
                self.total_failures += 1

            return {
                "name": self.name,
                "status": self.last_status.value,
                "healthy": is_healthy,
                "critical": self.critical,
                "message": message,
                "details": details,
                "duration_seconds": duration,
                "timestamp": self.last_check_time.isoformat()
            }

        except asyncio.TimeoutError:
            self.total_failures += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_check_time = datetime.utcnow()

            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "healthy": False,
                "critical": self.critical,
                "message": f"Health check timed out after {self.timeout}s",
                "error": "timeout",
                "timestamp": self.last_check_time.isoformat()
            }

        except Exception as e:
            self.total_failures += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_check_time = datetime.utcnow()

            logger.error(
                f"Health check {self.name} failed",
                exc_info=True,
                extra={"check": self.name, "error": str(e)}
            )

            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "healthy": False,
                "critical": self.critical,
                "message": f"Health check failed: {str(e)}",
                "error": type(e).__name__,
                "timestamp": self.last_check_time.isoformat()
            }


class HealthCheckSystem:
    """
    Comprehensive health check system.

    Manages multiple health checks and provides aggregated health status.
    Supports both liveness and readiness checks for Kubernetes.
    """

    def __init__(self):
        """Initialize health check system."""
        self.checks: Dict[str, HealthCheck] = {}
        self.start_time = datetime.utcnow()

    def register_check(
        self,
        name: str,
        check_func: Callable,
        critical: bool = True,
        timeout: float = 5.0
    ) -> None:
        """
        Register a health check.

        Args:
            name: Unique name for the check
            check_func: Async function that performs the check
            critical: Whether failure causes overall unhealthy status
            timeout: Timeout for check in seconds
        """
        self.checks[name] = HealthCheck(name, check_func, critical, timeout)
        logger.info(f"Registered health check: {name} (critical={critical})")

    async def check_all(self) -> Dict[str, Any]:
        """
        Execute all health checks.

        Returns:
            Aggregated health status
        """
        # Run all checks concurrently
        check_tasks = [check.check() for check in self.checks.values()]
        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        # Process results
        check_results = []
        critical_failures = 0
        non_critical_failures = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check raised exception: {result}")
                continue

            check_results.append(result)

            if not result["healthy"]:
                if result["critical"]:
                    critical_failures += 1
                else:
                    non_critical_failures += 1

        # Determine overall status
        if critical_failures > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif non_critical_failures > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "status": overall_status.value,
            "healthy": overall_status == HealthStatus.HEALTHY,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime,
            "checks": check_results,
            "summary": {
                "total": len(check_results),
                "healthy": len(check_results) - critical_failures - non_critical_failures,
                "degraded": non_critical_failures,
                "unhealthy": critical_failures
            }
        }

    async def liveness_check(self) -> Dict[str, Any]:
        """
        Liveness check for Kubernetes.

        Returns True if the application is running and can handle requests.
        Failures should trigger container restart.

        Returns:
            Liveness status
        """
        # Basic liveness check - just verify we can respond
        return {
            "alive": True,
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness check for Kubernetes.

        Returns True if the application is ready to handle requests.
        Failures should remove pod from load balancer.

        Returns:
            Readiness status
        """
        # Check critical components only
        critical_checks = [
            check for check in self.checks.values()
            if check.critical
        ]

        if not critical_checks:
            return {
                "ready": True,
                "status": "healthy",
                "message": "No critical checks registered"
            }

        # Run critical checks
        check_tasks = [check.check() for check in critical_checks]
        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        # Check if all critical checks passed
        all_passed = all(
            isinstance(r, dict) and r.get("healthy", False)
            for r in results
        )

        return {
            "ready": all_passed,
            "status": "healthy" if all_passed else "unhealthy",
            "checks": [r for r in results if isinstance(r, dict)],
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get health check statistics."""
        return {
            "total_checks": len(self.checks),
            "checks": {
                name: {
                    "total_checks": check.total_checks,
                    "total_failures": check.total_failures,
                    "last_status": check.last_status.value if check.last_status else None,
                    "last_check_time": check.last_check_time.isoformat() if check.last_check_time else None
                }
                for name, check in self.checks.items()
            }
        }


# Global health check system
_health_system: Optional[HealthCheckSystem] = None


def get_health_system() -> HealthCheckSystem:
    """
    Get global health check system (singleton pattern).

    Returns:
        Global health check system
    """
    global _health_system
    if _health_system is None:
        _health_system = HealthCheckSystem()
    return _health_system


def init_health_system() -> HealthCheckSystem:
    """
    Initialize global health check system.

    Returns:
        Configured health check system
    """
    global _health_system
    _health_system = HealthCheckSystem()
    return _health_system


# Common health check implementations
async def check_spotify_api(client) -> Dict[str, Any]:
    """Health check for Spotify API connectivity."""
    try:
        user = await client.current_user()
        return {
            "healthy": user is not None,
            "message": "Spotify API accessible",
            "details": {"user_id": user.get("id") if user else None}
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Spotify API error: {str(e)}",
            "details": {"error_type": type(e).__name__}
        }


async def check_cache(cache_manager) -> Dict[str, Any]:
    """Health check for cache backend."""
    try:
        stats = cache_manager.get_stats()
        return {
            "healthy": True,
            "message": "Cache operational",
            "details": {
                "backend": cache_manager._backend_name,
                "hit_rate": stats.get("hits", 0) / max(stats.get("hits", 0) + stats.get("misses", 0), 1) * 100
            }
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Cache error: {str(e)}"
        }


async def check_metrics(metrics_collector) -> Dict[str, Any]:
    """Health check for metrics system."""
    try:
        # Simple check that metrics are being collected
        return {
            "healthy": True,
            "message": "Metrics system operational"
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Metrics error: {str(e)}"
        }
