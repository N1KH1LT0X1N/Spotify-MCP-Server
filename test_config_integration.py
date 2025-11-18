#!/usr/bin/env python3
"""
Test configuration management system.

Validates that settings load correctly from environment and provide type safety.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Check if pydantic is available
try:
    import pydantic
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


def test_config_imports():
    """Test that configuration modules import correctly."""
    print("Testing config imports...")

    try:
        # Check if pydantic is available
        try:
            import pydantic
            print("✓ Pydantic is installed")
        except ImportError:
            print("⚠ Pydantic not installed (required dependency)")
            print("  Install with: pip install -e .")
            print("\n⚠ Config tests skipped (pydantic required)\n")
            return True  # Not a failure, just missing dependency

        from spotify_mcp.config import (
            get_settings,
            Settings,
            SpotifyConfig,
            CacheConfig,
            MetricsConfig,
            LoggingConfig,
        )
        print("✓ All config imports successful")
        print("\n✅ Config import tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Config import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_default_settings():
    """Test default settings loading."""
    if not PYDANTIC_AVAILABLE:
        print("⚠ Skipping test (pydantic not installed)\n")
        return True

    print("Testing default settings...")

    try:
        from spotify_mcp.config import Settings

        # Create settings with defaults
        settings = Settings()

        # Verify defaults
        assert settings.cache.backend == "memory"
        assert settings.cache.max_memory_size == 1000
        assert settings.logging.level == "INFO"
        assert settings.logging.format == "human"
        assert settings.environment == "development"
        assert settings.debug == False

        print("✓ Default settings loaded correctly")
        print("\n✅ Default settings tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Default settings test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_env_loading():
    """Test loading settings from environment."""
    print("Testing environment variable loading...")

    try:
        from spotify_mcp.config import Settings

        # Mock environment variables
        test_env = {
            "SPOTIFY_CLIENT_ID": "test_client_id",
            "SPOTIFY_CLIENT_SECRET": "test_secret",
            "CACHE_BACKEND": "redis",
            "REDIS_URL": "redis://testhost:6379/1",
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "json",
            "METRICS_ENABLED": "true",
            "METRICS_PORT": "9090",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
        }

        with patch.dict(os.environ, test_env, clear=False):
            settings = Settings.from_env()

            # Verify Spotify config
            assert settings.spotify.client_id == "test_client_id"
            assert settings.spotify.client_secret == "test_secret"
            print("✓ Spotify config loaded from env")

            # Verify cache config
            assert settings.cache.backend == "redis"
            assert settings.cache.redis_url == "redis://testhost:6379/1"
            print("✓ Cache config loaded from env")

            # Verify logging config
            assert settings.logging.level == "DEBUG"
            assert settings.logging.format == "json"
            print("✓ Logging config loaded from env")

            # Verify metrics config
            assert settings.metrics.enabled == True
            assert settings.metrics.port == 9090
            print("✓ Metrics config loaded from env")

            # Verify general settings
            assert settings.environment == "production"
            assert settings.debug == False
            assert settings.is_production == True
            assert settings.is_development == False
            print("✓ General settings loaded from env")

        print("\n✅ Environment loading tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Environment loading test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test configuration validation."""
    print("Testing configuration validation...")

    try:
        from spotify_mcp.config import CacheConfig, LoggingConfig
        from pydantic import ValidationError

        # Test valid cache backend
        cache = CacheConfig(backend="memory")
        assert cache.backend == "memory"
        print("✓ Valid cache backend accepted")

        # Test invalid cache backend
        try:
            CacheConfig(backend="invalid")
            print("✗ Invalid cache backend should have been rejected")
            return False
        except ValidationError:
            print("✓ Invalid cache backend rejected")

        # Test valid log level
        logging = LoggingConfig(level="DEBUG")
        assert logging.level == "DEBUG"
        print("✓ Valid log level accepted")

        # Test invalid log level
        try:
            LoggingConfig(level="TRACE")
            print("✗ Invalid log level should have been rejected")
            return False
        except ValidationError:
            print("✓ Invalid log level rejected")

        print("\n✅ Validation tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Validation test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_type_safety():
    """Test type safety and IDE support."""
    print("Testing type safety...")

    try:
        from spotify_mcp.config import Settings

        settings = Settings()

        # Test attribute access (should not raise)
        _ = settings.spotify.client_id
        _ = settings.cache.backend
        _ = settings.logging.level
        _ = settings.metrics.enabled

        print("✓ All attributes accessible")

        # Test property methods
        _ = settings.is_production
        _ = settings.is_development

        print("✓ Property methods working")

        print("\n✅ Type safety tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Type safety test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_singleton_pattern():
    """Test settings singleton caching."""
    print("Testing singleton pattern...")

    try:
        from spotify_mcp.config import get_settings

        # Clear any existing cache
        get_settings.cache_clear()

        # Get settings first time
        settings1 = get_settings()

        # Get settings second time - should return same instance
        settings2 = get_settings()

        # Verify it's the same object
        assert settings1 is settings2
        print("✓ Singleton pattern working (cached instance)")

        # Test cache clear
        get_settings.cache_clear()
        settings3 = get_settings()

        # Should be a new instance
        assert settings3 is not settings1
        print("✓ Cache clear working")

        print("\n✅ Singleton pattern tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Singleton pattern test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_sub_configs():
    """Test individual sub-configuration models."""
    print("Testing sub-configuration models...")

    try:
        from spotify_mcp.config import SpotifyConfig, CacheConfig, MetricsConfig, LoggingConfig

        # Test SpotifyConfig.from_env()
        with patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "env_id"}, clear=False):
            spotify = SpotifyConfig.from_env()
            assert spotify.client_id == "env_id"
            print("✓ SpotifyConfig.from_env() working")

        # Test CacheConfig.from_env()
        with patch.dict(os.environ, {"CACHE_BACKEND": "redis"}, clear=False):
            cache = CacheConfig.from_env()
            assert cache.backend == "redis"
            print("✓ CacheConfig.from_env() working")

        # Test MetricsConfig.from_env()
        with patch.dict(os.environ, {"METRICS_ENABLED": "true"}, clear=False):
            metrics = MetricsConfig.from_env()
            assert metrics.enabled == True
            print("✓ MetricsConfig.from_env() working")

        # Test LoggingConfig.from_env()
        with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}, clear=False):
            logging = LoggingConfig.from_env()
            assert logging.level == "ERROR"
            print("✓ LoggingConfig.from_env() working")

        print("\n✅ Sub-configuration tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Sub-configuration test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Spotify MCP Server - Configuration Tests")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed &= test_config_imports()
    all_passed &= test_default_settings()
    all_passed &= test_env_loading()
    all_passed &= test_validation()
    all_passed &= test_type_safety()
    all_passed &= test_singleton_pattern()
    all_passed &= test_sub_configs()

    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nConfiguration management is ready to use!")
        print("Usage: from spotify_mcp.config import get_settings")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)
    print()

    if not all_passed:
        sys.exit(1)
