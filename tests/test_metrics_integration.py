#!/usr/bin/env python3
"""
Quick test to verify metrics infrastructure integration.
This verifies that the metrics system works without breaking existing functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_metrics_imports():
    """Test that all metrics imports work correctly."""
    print("Testing metrics imports...")

    try:
        from spotify_mcp.infrastructure.metrics import (
            get_metrics_collector,
            track_tool_call,
            track_cache_operation,
            update_cache_metrics,
            METRICS_AVAILABLE
        )
        print(f"✓ Metrics imports successful")

        # Check actual prometheus-client installation
        collector = get_metrics_collector()
        if collector.enabled:
            print("✓ prometheus-client is installed and enabled")
        else:
            print("⚠ prometheus-client not installed (graceful degradation active)")

        print("\n✅ Metrics import tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Metrics import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_collector():
    """Test that metrics collector works."""
    print("Testing metrics collector...")

    try:
        from spotify_mcp.infrastructure.metrics import get_metrics_collector

        collector = get_metrics_collector()
        print(f"✓ Metrics collector initialized (enabled: {collector.enabled})")

        # Test recording metrics (should work even without prometheus-client)
        collector.record_tool_call('test_tool', 0.5, 'success')
        print("✓ Tool call metric recorded")

        collector.record_cache_operation('get', 'hit')
        print("✓ Cache operation metric recorded")

        collector.update_cache_stats('memory', 85.5, 100)
        print("✓ Cache stats metric updated")

        collector.increment_active_requests()
        collector.decrement_active_requests()
        print("✓ Active requests tracking works")

        print("\n✅ Metrics collector tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Metrics collector test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_cache_with_metrics():
    """Test that cache works with metrics integration."""
    print("Testing cache with metrics integration...")

    try:
        from spotify_mcp.infrastructure.cache import get_cache_manager

        cache_mgr = get_cache_manager()
        cache = cache_mgr.cache

        # These operations should track metrics if available
        cache.set("test_key", {"test": "value"}, ttl=60)
        print("✓ Cache set with metrics tracking")

        value = cache.get("test_key")
        assert value == {"test": "value"}
        print("✓ Cache get with metrics tracking")

        # Test miss
        miss_value = cache.get("nonexistent_key")
        assert miss_value is None
        print("✓ Cache miss with metrics tracking")

        stats = cache.get_stats()
        print(f"✓ Cache stats: {stats}")

        print("\n✅ Cache with metrics tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Cache with metrics test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_endpoint():
    """Test metrics endpoint (only if prometheus-client installed)."""
    print("Testing metrics endpoint...")

    try:
        from spotify_mcp.infrastructure.metrics import get_metrics_collector, metrics_endpoint

        collector = get_metrics_collector()

        # Check if prometheus-client is actually installed
        if not collector.enabled:
            print("⚠ prometheus-client not installed (testing graceful degradation)")

            content, content_type = metrics_endpoint()
            assert content is not None
            assert 'text/plain' in content_type
            content_str = content.decode() if isinstance(content, bytes) else content
            assert 'Metrics not available' in content_str
            print("✓ Metrics endpoint returns graceful degradation message")
            print("\n✅ Metrics endpoint tests passed (graceful degradation)!\n")
            return True

        # prometheus-client is installed, test full functionality
        content, content_type = metrics_endpoint()

        assert content is not None
        assert 'text/plain' in content_type or 'openmetrics' in content_type
        print(f"✓ Metrics endpoint returns data ({len(content)} bytes)")

        # Check that our metrics are present
        content_str = content.decode() if isinstance(content, bytes) else content
        assert 'spotify_mcp_' in content_str
        print("✓ Metrics endpoint contains spotify_mcp metrics")

        print("\n✅ Metrics endpoint tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Metrics endpoint test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Spotify MCP Server - Metrics Integration Tests")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed &= test_metrics_imports()
    all_passed &= test_metrics_collector()
    all_passed &= test_cache_with_metrics()
    all_passed &= test_metrics_endpoint()

    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)
    print()

    if not all_passed:
        sys.exit(1)
