"""
Status command - Show current playback status.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

from ..utils import get_client, format_duration, handle_api_error, show_error


@click.command()
@click.pass_context
def status(ctx):
    """
    Show current playback status.

    Displays currently playing track, artist, album, playback state,
    device, volume, shuffle, and repeat mode.
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        playback = client.current_playback()

        if not playback or not playback.get('item'):
            console.print(Panel(
                "[yellow]No track currently playing[/yellow]",
                title="🎵 Spotify Status",
                border_style="yellow"
            ))
            return

        item = playback['item']
        is_playing = playback.get('is_playing', False)
        device = playback.get('device', {})
        progress_ms = playback.get('progress_ms', 0)
        duration_ms = item.get('duration_ms', 0)

        # Create status table
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Key", style="cyan", width=12)
        table.add_column("Value", style="white")

        # Track info
        track_name = item.get('name', 'Unknown')
        artists = ', '.join([artist['name'] for artist in item.get('artists', [])])
        album = item.get('album', {}).get('name', 'Unknown')

        table.add_row("Track", track_name)
        table.add_row("Artist", artists)
        table.add_row("Album", album)
        table.add_row("", "")  # Spacing

        # Playback state
        state = "▶ Playing" if is_playing else "⏸ Paused"
        state_color = "green" if is_playing else "yellow"
        table.add_row("State", f"[{state_color}]{state}[/{state_color}]")

        # Progress
        progress_str = f"{format_duration(progress_ms)} / {format_duration(duration_ms)}"
        table.add_row("Progress", progress_str)

        # Progress bar
        if duration_ms > 0:
            progress_pct = (progress_ms / duration_ms) * 100
            bar_length = 30
            filled = int(bar_length * progress_ms / duration_ms)
            bar = "█" * filled + "░" * (bar_length - filled)
            table.add_row("", f"[cyan]{bar}[/cyan] {progress_pct:.1f}%")

        table.add_row("", "")  # Spacing

        # Device info
        device_name = device.get('name', 'Unknown')
        device_type = device.get('type', 'Unknown')
        volume = device.get('volume_percent', 0)

        table.add_row("Device", f"{device_name} ({device_type})")
        table.add_row("Volume", f"{volume}%")

        # Playback settings
        shuffle = "On" if playback.get('shuffle_state') else "Off"
        repeat = playback.get('repeat_state', 'off').title()

        table.add_row("Shuffle", shuffle)
        table.add_row("Repeat", repeat)

        # Display in panel
        console.print(Panel(
            table,
            title="🎵 Now Playing",
            border_style="green" if is_playing else "yellow"
        ))

    except Exception as e:
        handle_api_error(e, console)
