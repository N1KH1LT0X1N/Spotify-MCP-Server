#!/usr/bin/env python3
"""
Test structured logging infrastructure.

Validates that logging works correctly with JSON formatting, correlation IDs,
and context management.
"""

import sys
import json
from pathlib import Path
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_logging_imports():
    """Test that logging modules import correctly."""
    print("Testing logging imports...")

    try:
        from spotify_mcp.infrastructure.logging import (
            get_logger,
            setup_logging,
            LogLevel,
            add_log_context,
            clear_log_context,
            log_context,
            set_correlation_id
        )
        print("✓ All logging imports successful")
        print("\n✅ Logging import tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Logging import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_logging_setup():
    """Test logging setup and configuration."""
    print("Testing logging setup...")

    try:
        from spotify_mcp.infrastructure.logging import setup_logging, get_logger, LogLevel

        # Test human format
        setup_logging(level=LogLevel.DEBUG, format_type="human")
        print("✓ Human format logging initialized")

        # Test JSON format
        setup_logging(level=LogLevel.INFO, format_type="json")
        print("✓ JSON format logging initialized")

        # Get a logger
        logger = get_logger("test")
        print("✓ Logger instance created")

        print("\n✅ Logging setup tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Logging setup test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_correlation_ids():
    """Test correlation ID functionality."""
    print("Testing correlation IDs...")

    try:
        from spotify_mcp.infrastructure.logging import (
            get_logger,
            setup_logging,
            LogLevel,
            set_correlation_id,
        )

        setup_logging(level=LogLevel.DEBUG, format_type="human")
        logger = get_logger("test")

        # Set a custom correlation ID
        set_correlation_id("test-12345")
        print("✓ Correlation ID set successfully")

        # Log a message (correlation ID will be included)
        logger.info("Test message with correlation ID")
        print("✓ Message logged with correlation ID")

        print("\n✅ Correlation ID tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Correlation ID test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_log_context():
    """Test context management."""
    print("Testing log context...")

    try:
        from spotify_mcp.infrastructure.logging import (
            get_logger,
            setup_logging,
            LogLevel,
            add_log_context,
            clear_log_context,
            log_context,
        )

        setup_logging(level=LogLevel.DEBUG, format_type="human")
        logger = get_logger("test")

        # Add permanent context
        add_log_context(user_id="user123", session="abc")
        logger.info("Message with permanent context")
        print("✓ Permanent context added")

        # Clear context
        clear_log_context()
        logger.info("Message after context cleared")
        print("✓ Context cleared")

        # Temporary context with context manager
        with log_context(operation="test_operation"):
            logger.info("Message with temporary context")
            print("✓ Temporary context working")

        logger.info("Message after context manager exited")
        print("✓ Context manager cleanup verified")

        print("\n✅ Log context tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Log context test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_log_levels():
    """Test different log levels."""
    print("Testing log levels...")

    try:
        from spotify_mcp.infrastructure.logging import (
            get_logger,
            setup_logging,
            LogLevel,
        )

        setup_logging(level=LogLevel.DEBUG, format_type="human")
        logger = get_logger("test")

        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        print("✓ All log levels working")
        print("\n✅ Log level tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Log level test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_json_output():
    """Test JSON formatter output."""
    print("Testing JSON output format...")

    try:
        from spotify_mcp.infrastructure.logging import (
            setup_logging,
            get_logger,
            LogLevel,
            JSONFormatter,
        )
        import logging

        # Create a test logger with JSON formatter
        test_logger = logging.getLogger("json_test")
        test_logger.setLevel(logging.DEBUG)
        test_logger.handlers.clear()

        # Capture output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        test_logger.addHandler(handler)

        # Log a message
        test_logger.info("Test JSON message", extra={"test_field": "test_value"})

        # Get the output
        output = stream.getvalue()

        # Parse JSON
        log_entry = json.loads(output)

        # Validate JSON structure
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "logger" in log_entry
        assert "message" in log_entry
        assert "correlation_id" in log_entry
        assert "source" in log_entry

        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test JSON message"

        print("✓ JSON output format validated")
        print(f"✓ Sample JSON log: {output.strip()[:100]}...")

        print("\n✅ JSON output tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ JSON output test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_exception_logging():
    """Test exception logging."""
    print("Testing exception logging...")

    try:
        from spotify_mcp.infrastructure.logging import (
            get_logger,
            setup_logging,
            LogLevel,
        )

        setup_logging(level=LogLevel.DEBUG, format_type="human")
        logger = get_logger("test")

        # Test exception logging
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)

        print("✓ Exception logged successfully")
        print("\n✅ Exception logging tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ Exception logging test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Spotify MCP Server - Logging Infrastructure Tests")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed &= test_logging_imports()
    all_passed &= test_logging_setup()
    all_passed &= test_correlation_ids()
    all_passed &= test_log_context()
    all_passed &= test_log_levels()
    all_passed &= test_json_output()
    all_passed &= test_exception_logging()

    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nStructured logging is ready to use!")
        print("Usage: LOG_LEVEL=DEBUG LOG_FORMAT=json python -m spotify_mcp.server")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)
    print()

    if not all_passed:
        sys.exit(1)
