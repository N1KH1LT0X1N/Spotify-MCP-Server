#!/usr/bin/env python3
"""
Quick test to verify CLI infrastructure integration.
This verifies that the CLI system works without breaking existing functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_cli_imports():
    """Test that all CLI imports work correctly."""
    print("Testing CLI imports...")

    try:
        # Test main CLI module
        from spotify_mcp.cli import cli
        print("✓ CLI main module imports successfully")

        # Test CLI dependencies
        cli_available = True
        try:
            import click
            print("✓ Click is installed")
        except ImportError:
            print("⚠ Click not installed (install with: pip install click)")
            cli_available = False

        try:
            import rich
            print("✓ Rich is installed")
        except ImportError:
            print("⚠ Rich not installed (install with: pip install rich)")
            cli_available = False

        if cli_available:
            # Test command modules (only if dependencies are available)
            from spotify_mcp.cli.commands import (
                playback,
                search,
                library,
                playlist,
                status,
                device,
                interactive
            )
            print("✓ All command modules import successfully")
        else:
            print("⚠ Skipping command module tests (dependencies not installed)")

        print("\n✅ CLI import tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ CLI import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_cli_utilities():
    """Test CLI utility functions."""
    print("Testing CLI utilities...")

    try:
        # Check if dependencies are available
        try:
            import click
            import rich
            deps_available = True
        except ImportError:
            deps_available = False
            print("⚠ Skipping utility tests (click/rich not installed)")
            print("\n✅ CLI utility tests skipped!\n")
            return True

        from spotify_mcp.cli.utils import format_duration, format_track

        # Test duration formatting
        assert format_duration(60000) == "1:00"
        assert format_duration(125000) == "2:05"
        assert format_duration(0) == "0:00"
        print("✓ Duration formatting works")

        # Test track formatting
        track_data = {
            'name': 'Test Track',
            'artists': [{'name': 'Artist 1'}, {'name': 'Artist 2'}],
            'album': {'name': 'Test Album'}
        }
        formatted = format_track(track_data)
        assert 'Test Track' in formatted
        assert 'Artist 1' in formatted
        print("✓ Track formatting works")

        print("\n✅ CLI utility tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ CLI utility test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_cli_entry_point():
    """Test that CLI entry point is configured."""
    print("Testing CLI entry point...")

    try:
        from spotify_mcp.cli.main import main
        print("✓ CLI main() function exists")

        # Check that CLI can be imported
        from spotify_mcp.cli import cli
        print("✓ CLI object is available")

        print("\n✅ CLI entry point tests passed!\n")
        return True

    except Exception as e:
        print(f"\n❌ CLI entry point test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Spotify MCP CLI - Integration Tests")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed &= test_cli_imports()
    all_passed &= test_cli_utilities()
    all_passed &= test_cli_entry_point()

    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe CLI is ready to use!")
        print("Install dependencies: pip install -e \".[cli]\"")
        print("Run CLI: spotify-mcp-cli --help")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)
    print()

    if not all_passed:
        sys.exit(1)
