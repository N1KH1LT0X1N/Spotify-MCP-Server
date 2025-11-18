"""
Library commands - Manage your Spotify library.
"""

import click
from rich.console import Console

from ..utils import (
    get_client,
    create_track_table,
    show_success,
    handle_api_error,
    show_error
)


@click.group()
def library():
    """
    Library management commands.

    View, save, and remove tracks and albums from your library.
    """
    pass


@library.command('tracks')
@click.option('--limit', '-l', default=20, help='Number of tracks to show')
@click.pass_context
def list_tracks(ctx, limit):
    """List your saved tracks."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        result = client.get_saved_tracks(limit=limit)
        items = result.get('items', [])

        if not items:
            console.print("[yellow]No saved tracks found[/yellow]")
            return

        # Extract tracks from items
        tracks = [item['track'] for item in items if 'track' in item]

        console.print(f"\n[bold cyan]💾 Your Saved Tracks ({len(tracks)}/{result.get('total', 0)}):[/bold cyan]")
        table = create_track_table(tracks, console)
        console.print(table)

    except Exception as e:
        handle_api_error(e, console)


@library.command('save-track')
@click.argument('track_id')
@click.pass_context
def save_track(ctx, track_id):
    """
    Save a track to your library.

    TRACK_ID: Spotify track ID or URI
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Extract ID from URI if needed
        if track_id.startswith('spotify:track:'):
            track_id = track_id.split(':')[-1]

        client.save_tracks([track_id])
        show_success(f"Track saved to library", console)

    except Exception as e:
        handle_api_error(e, console)


@library.command('remove-track')
@click.argument('track_id')
@click.pass_context
def remove_track(ctx, track_id):
    """
    Remove a track from your library.

    TRACK_ID: Spotify track ID or URI
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Extract ID from URI if needed
        if track_id.startswith('spotify:track:'):
            track_id = track_id.split(':')[-1]

        client.remove_saved_tracks([track_id])
        show_success(f"Track removed from library", console)

    except Exception as e:
        handle_api_error(e, console)
