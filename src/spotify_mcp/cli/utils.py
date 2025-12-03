"""
Utility functions for the Spotify MCP CLI.
"""

import sys
import io
from typing import Optional, Any

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, io.UnsupportedOperation):
        pass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient

# Global client instance
_client: Optional[SpotifyClient] = None


def get_client() -> SpotifyClient:
    """
    Get or create Spotify client.

    Returns:
        Initialized Spotify client
    """
    global _client
    if _client is None:
        try:
            sp = get_spotify_client()
            _client = SpotifyClient(sp)
        except Exception as e:
            if RICH_AVAILABLE:
                console = Console()
                console.print(f"[red]Error:[/red] Failed to initialize Spotify client: {e}")
            else:
                print(f"Error: Failed to initialize Spotify client: {e}")
            sys.exit(1)
    return _client


def format_duration(ms: int) -> str:
    """
    Format duration in milliseconds to MM:SS.

    Args:
        ms: Duration in milliseconds

    Returns:
        Formatted duration string
    """
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def format_track(track: dict, show_album: bool = True) -> str:
    """
    Format track information for display.

    Args:
        track: Track data from Spotify API
        show_album: Whether to show album name

    Returns:
        Formatted track string
    """
    artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
    name = track.get('name', 'Unknown')

    if show_album and 'album' in track:
        album = track['album'].get('name', 'Unknown')
        return f"{name} - {artists} ({album})"
    return f"{name} - {artists}"


def create_track_table(tracks: list, console: Console) -> Table:
    """
    Create a beautiful table for displaying tracks.

    Args:
        tracks: List of track dictionaries
        console: Rich console instance

    Returns:
        Rich Table object
    """
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Track", style="cyan")
    table.add_column("Artist", style="green")
    table.add_column("Album", style="yellow")
    table.add_column("Duration", justify="right", style="blue")

    for idx, track in enumerate(tracks, 1):
        name = track.get('name', 'Unknown')
        artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
        album = track.get('album', {}).get('name', 'Unknown') if 'album' in track else 'Unknown'
        duration = format_duration(track.get('duration_ms', 0))

        table.add_row(str(idx), name, artists, album, duration)

    return table


def show_error(message: str, console: Optional[Console] = None):
    """
    Display an error message.

    Args:
        message: Error message to display
        console: Rich console instance (optional)
    """
    if console and RICH_AVAILABLE:
        console.print(f"[red]✗ Error:[/red] {message}")
    else:
        print(f"Error: {message}")


def show_success(message: str, console: Optional[Console] = None):
    """
    Display a success message.

    Args:
        message: Success message to display
        console: Rich console instance (optional)
    """
    if console and RICH_AVAILABLE:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"✓ {message}")


def show_info(message: str, console: Optional[Console] = None):
    """
    Display an info message.

    Args:
        message: Info message to display
        console: Rich console instance (optional)
    """
    if console and RICH_AVAILABLE:
        console.print(f"[blue]ℹ[/blue] {message}")
    else:
        print(f"ℹ {message}")


def handle_api_error(e: Exception, console: Optional[Console] = None):
    """
    Handle and display API errors gracefully.

    Args:
        e: Exception that was raised
        console: Rich console instance (optional)
    """
    error_msg = str(e)

    # Common error patterns
    if "401" in error_msg or "Unauthorized" in error_msg:
        show_error("Authentication failed. Please check your credentials.", console)
    elif "403" in error_msg or "Forbidden" in error_msg:
        show_error("Access forbidden. You may need Spotify Premium for this feature.", console)
    elif "404" in error_msg or "Not found" in error_msg:
        show_error("Resource not found.", console)
    elif "429" in error_msg or "rate limit" in error_msg.lower():
        show_error("Rate limit exceeded. Please try again later.", console)
    else:
        show_error(f"API error: {error_msg}", console)
