#!/usr/bin/env python3
"""
Spotify MCP CLI - Main entry point.

Beautiful command-line interface for controlling Spotify.
"""

import sys

# Check for required dependencies
try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    click = None
    Console = None

if not CLI_AVAILABLE:
    def cli():
        print("Error: CLI dependencies not installed")
        print("Install with: pip install -e \".[cli]\" or pip install click rich")
        sys.exit(1)
else:
    from .commands import (
        playback,
        search,
        library,
        playlist,
        status,
        device,
        interactive
    )

    console = Console()

    @click.group()
    @click.version_option(version='1.1.0', prog_name='spotify-mcp')
    @click.pass_context
    def cli(ctx):
        """
        🎵 Spotify MCP CLI - Control Spotify from your terminal

        A beautiful, intuitive interface for managing your Spotify experience.
        Built with ♥ using Click and Rich.
        """
        # Ensure context object exists
        ctx.ensure_object(dict)
        ctx.obj['console'] = console

    # Add command groups
    cli.add_command(playback.playback)
    cli.add_command(search.search)
    cli.add_command(library.library)
    cli.add_command(playlist.playlist)
    cli.add_command(status.status)
    cli.add_command(device.device)
    cli.add_command(interactive.interactive)


def main():
    """Main entry point for the CLI."""
    if not CLI_AVAILABLE:
        print("Error: CLI dependencies not installed")
        print("Install with: pip install -e \".[cli]\" or pip install click rich")
        sys.exit(1)

    cli(obj={})


if __name__ == '__main__':
    main()
