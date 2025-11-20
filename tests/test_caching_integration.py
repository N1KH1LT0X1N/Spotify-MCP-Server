#!/usr/bin/env python3
"""
Quick test to verify caching layer integration.
This verifies that the caching infrastructure works without breaking existing functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_mcp.infrastructure.cache import get_cache_manager, CacheStrategy


def test_memory_cache():
    """Test that memory cache works."""
    print("Testing memory cache...")

    cache_mgr = get_cache_manager()
    cache = cache_mgr.cache

    # Test set/get
    cache.set("test_key", {"test": "value"}, ttl=60)
    value = cache.get("test_key")

    assert value == {"test": "value"}, f"Expected {{'test': 'value'}}, got {value}"
    print("✓ Memory cache set/get works")

    # Test stats
    stats = cache.get_stats()
    assert stats["backend"] == "memory", f"Expected memory backend, got {stats['backend']}"
    assert stats["hits"] >= 1, "Should have at least 1 hit"
    print(f"✓ Cache stats: {stats}")

    # Test expiration (set with 0 TTL should expire immediately)
    cache.set("expire_test", "value", ttl=0)
    import time
    time.sleep(0.1)
    value = cache.get("expire_test")
    assert value is None, "Expired value should return None"
    print("✓ Cache expiration works")

    # Test deletion
    cache.set("delete_test", "value", ttl=60)
    cache.delete("delete_test")
    value = cache.get("delete_test")
    assert value is None, "Deleted value should return None"
    print("✓ Cache deletion works")

    print("\n✅ All memory cache tests passed!\n")


def test_cache_strategies():
    """Test that cache strategies are defined correctly."""
    print("Testing cache strategies...")

    # Verify all strategies have TTL and prefix
    for strategy in CacheStrategy:
        assert hasattr(strategy, 'ttl'), f"{strategy} missing ttl"
        assert hasattr(strategy, 'prefix'), f"{strategy} missing prefix"
        assert strategy.ttl > 0, f"{strategy} has invalid TTL: {strategy.ttl}"
        assert len(strategy.prefix) > 0, f"{strategy} has empty prefix"

    print(f"✓ All {len(CacheStrategy)} cache strategies are valid")

    # Print some examples
    print("\nExample TTL strategies:")
    print(f"  - Track metadata: {CacheStrategy.TRACK_METADATA.ttl}s (24 hours)")
    print(f"  - Playlist metadata: {CacheStrategy.PLAYLIST_METADATA.ttl}s (5 minutes)")
    print(f"  - Playback state: {CacheStrategy.PLAYBACK_STATE.ttl}s (10 seconds)")
    print(f"  - Search results: {CacheStrategy.SEARCH_RESULTS.ttl}s (10 minutes)")

    print("\n✅ Cache strategy tests passed!\n")


def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        # Test cache infrastructure imports (don't require spotipy)
        from spotify_mcp.infrastructure.cache.decorators import cached
        print("✓ Cache decorators import successfully")

        from spotify_mcp.infrastructure.cache import MemoryCache, RedisCache, REDIS_AVAILABLE
        print(f"✓ Cache backends import successfully (Redis available: {REDIS_AVAILABLE})")

        from spotify_mcp.infrastructure.cache.strategies import CacheStrategy, CacheKeyGenerator
        print("✓ Cache strategies import successfully")

        from spotify_mcp.infrastructure.cache.manager import get_cache_manager
        print("✓ Cache manager imports successfully")

        print("\n✅ All import tests passed!\n")

    except Exception as e:
        print(f"\n❌ Import test failed: {e}\n")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Spotify MCP Server - Caching Integration Tests")
    print("=" * 60 + "\n")

    try:
        test_imports()
        test_memory_cache()
        test_cache_strategies()

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe caching layer is working correctly.")
        print("The server will use memory cache by default.")
        print("To use Redis cache, set: CACHE_BACKEND=redis")
        print()

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
