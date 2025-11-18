"""
Playlist commands - Manage Spotify playlists.
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box

from ..utils import (
    get_client,
    create_track_table,
    show_success,
    handle_api_error,
    show_error
)


@click.group()
def playlist():
    """
    Playlist management commands.

    List, create, and modify playlists.
    """
    pass


@playlist.command('list')
@click.option('--limit', '-l', default=20, help='Number of playlists to show')
@click.pass_context
def list_playlists(ctx, limit):
    """List your playlists."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        result = client.get_user_playlists(limit=limit)
        items = result.get('items', [])

        if not items:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Owner", style="green")
        table.add_column("Tracks", justify="right", style="blue")
        table.add_column("Public", style="yellow")
        table.add_column("URI", style="dim")

        for idx, pl in enumerate(items, 1):
            name = pl.get('name', 'Unknown')
            owner = pl.get('owner', {}).get('display_name', 'Unknown')
            total = str(pl.get('tracks', {}).get('total', 0))
            public = "✓" if pl.get('public') else ""
            uri = pl.get('uri', '')

            table.add_row(str(idx), name, owner, total, public, uri)

        console.print(f"\n[bold magenta]📚 Your Playlists ({len(items)}/{result.get('total', 0)}):[/bold magenta]")
        console.print(table)

    except Exception as e:
        handle_api_error(e, console)


@playlist.command('show')
@click.argument('playlist_id')
@click.option('--limit', '-l', default=20, help='Number of tracks to show')
@click.pass_context
def show_playlist(ctx, playlist_id, limit):
    """
    Show playlist details and tracks.

    PLAYLIST_ID: Spotify playlist ID or URI
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Extract ID from URI if needed
        if playlist_id.startswith('spotify:playlist:'):
            playlist_id = playlist_id.split(':')[-1]

        playlist_data = client.get_playlist(playlist_id)

        name = playlist_data.get('name', 'Unknown')
        owner = playlist_data.get('owner', {}).get('display_name', 'Unknown')
        description = playlist_data.get('description', 'No description')
        total_tracks = playlist_data.get('tracks', {}).get('total', 0)

        console.print(f"\n[bold magenta]📚 {name}[/bold magenta]")
        console.print(f"[dim]By {owner} • {total_tracks} tracks[/dim]")
        if description:
            console.print(f"[dim]{description}[/dim]\n")

        # Get tracks
        tracks_data = playlist_data.get('tracks', {})
        items = tracks_data.get('items', [])[:limit]

        if items:
            tracks = [item['track'] for item in items if item.get('track')]
            table = create_track_table(tracks, console)
            console.print(table)

    except Exception as e:
        handle_api_error(e, console)


@playlist.command('create')
@click.argument('name')
@click.option('--description', '-d', default='', help='Playlist description')
@click.option('--public/--private', default=False, help='Make playlist public')
@click.pass_context
def create_playlist(ctx, name, description, public):
    """
    Create a new playlist.

    NAME: Playlist name
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Get current user ID
        user = client.get_current_user()
        user_id = user.get('id')

        if not user_id:
            show_error("Could not get user ID", console)
            return

        playlist = client.create_playlist(
            user_id=user_id,
            name=name,
            description=description,
            public=public
        )

        playlist_id = playlist.get('id')
        show_success(f"Created playlist '{name}' (ID: {playlist_id})", console)

    except Exception as e:
        handle_api_error(e, console)


@playlist.command('add-track')
@click.argument('playlist_id')
@click.argument('track_id')
@click.pass_context
def add_track(ctx, playlist_id, track_id):
    """
    Add a track to a playlist.

    PLAYLIST_ID: Spotify playlist ID or URI
    TRACK_ID: Spotify track ID or URI
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Extract IDs from URIs if needed
        if playlist_id.startswith('spotify:playlist:'):
            playlist_id = playlist_id.split(':')[-1]

        if not track_id.startswith('spotify:track:'):
            track_id = f'spotify:track:{track_id}'

        client.add_tracks_to_playlist(playlist_id, [track_id])
        show_success(f"Track added to playlist", console)

    except Exception as e:
        handle_api_error(e, console)
