"""Cache statistics endpoint for monitoring and observability."""

from typing import Dict, Any, Optional
from datetime import datetime

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CacheStatistics:
    """
    Collect and expose cache statistics for monitoring.

    Provides detailed metrics about cache performance including:
    - Hit/miss rates
    - Size and evictions
    - Performance by strategy
    - Invalidation history
    - Warming statistics
    """

    def __init__(self, cache_manager, invalidator=None, warmer=None):
        """
        Initialize cache statistics collector.

        Args:
            cache_manager: CacheManager instance
            invalidator: CacheInvalidator instance (optional)
            warmer: CacheWarmer instance (optional)
        """
        self.cache_manager = cache_manager
        self.invalidator = invalidator
        self.warmer = warmer

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with all cache statistics
        """
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "cache": self._get_cache_stats(),
            "backend": {
                "type": self.cache_manager._backend_name,
                "redis_url": self.cache_manager._redis_url if self.cache_manager._backend_name == "redis" else None
            }
        }

        # Add invalidation stats if available
        if self.invalidator:
            stats["invalidation"] = self.invalidator.get_stats()

        # Add warming stats if available
        if self.warmer:
            stats["warming"] = self.warmer.get_stats()

        return stats

    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache backend statistics."""
        try:
            backend_stats = self.cache_manager.get_stats()

            # Calculate derived metrics
            hits = backend_stats.get("hits", 0)
            misses = backend_stats.get("misses", 0)
            total_requests = hits + misses

            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            miss_rate = (misses / total_requests * 100) if total_requests > 0 else 0

            return {
                **backend_stats,
                "hit_rate_percent": round(hit_rate, 2),
                "miss_rate_percent": round(miss_rate, 2),
                "total_requests": total_requests
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}", exc_info=True)
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get cache health status for health checks.

        Returns:
            Dictionary with health status
        """
        try:
            stats = self._get_cache_stats()

            # Determine health based on metrics
            is_healthy = True
            issues = []

            # Check hit rate
            hit_rate = stats.get("hit_rate_percent", 0)
            if hit_rate < 50:
                issues.append(f"Low cache hit rate: {hit_rate:.1f}%")

            # Check if cache is responding
            if "error" in stats:
                is_healthy = False
                issues.append(f"Cache error: {stats['error']}")

            return {
                "healthy": is_healthy and len(issues) == 0,
                "status": "healthy" if is_healthy else "degraded",
                "hit_rate_percent": hit_rate,
                "issues": issues
            }
        except Exception as e:
            return {
                "healthy": False,
                "status": "unhealthy",
                "error": str(e)
            }

    def reset_all_stats(self) -> None:
        """Reset all statistics counters."""
        self.cache_manager.reset_stats()

        if self.invalidator:
            self.invalidator.reset_stats()

        if self.warmer:
            self.warmer.reset_stats()

        logger.info("All cache statistics have been reset")


# Global statistics instance
_statistics: Optional[CacheStatistics] = None


def get_cache_statistics():
    """
    Get global cache statistics instance (singleton pattern).

    Returns:
        Global cache statistics
    """
    global _statistics
    return _statistics


def init_statistics(cache_manager, invalidator=None, warmer=None) -> CacheStatistics:
    """
    Initialize global cache statistics.

    Args:
        cache_manager: CacheManager instance
        invalidator: CacheInvalidator instance (optional)
        warmer: CacheWarmer instance (optional)

    Returns:
        Configured cache statistics
    """
    global _statistics
    _statistics = CacheStatistics(cache_manager, invalidator, warmer)
    return _statistics
