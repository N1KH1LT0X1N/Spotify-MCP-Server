"""
Search command - Find music on Spotify.
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box

from ..utils import (
    get_client,
    format_duration,
    create_track_table,
    handle_api_error,
    show_error
)


@click.command()
@click.argument('query')
@click.option('--type', '-t', 'search_type',
              type=click.Choice(['track', 'artist', 'album', 'playlist', 'all']),
              default='track',
              help='Type of search')
@click.option('--limit', '-l', default=10, help='Number of results')
@click.pass_context
def search(ctx, query, search_type, limit):
    """
    Search for music on Spotify.

    QUERY: Search query string
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        # Perform search
        results = client.search(q=query, limit=limit, type=search_type)

        if not results:
            show_error(f"No results found for '{query}'", console)
            return

        # Display results based on type
        if search_type == 'track' or search_type == 'all':
            tracks = results.get('tracks', {}).get('items', [])
            if tracks:
                console.print(f"\n[bold cyan]🎵 Tracks:[/bold cyan]")
                table = create_track_table(tracks, console)
                console.print(table)

        if search_type == 'artist' or search_type == 'all':
            artists = results.get('artists', {}).get('items', [])
            if artists:
                console.print(f"\n[bold green]🎤 Artists:[/bold green]")
                table = Table(box=box.ROUNDED, show_header=True, header_style="bold green")
                table.add_column("#", style="dim", width=4)
                table.add_column("Name", style="cyan")
                table.add_column("Genres", style="yellow")
                table.add_column("Popularity", justify="right", style="magenta")
                table.add_column("URI", style="dim")

                for idx, artist in enumerate(artists, 1):
                    name = artist.get('name', 'Unknown')
                    genres = ', '.join(artist.get('genres', [])[:3]) or 'N/A'
                    popularity = str(artist.get('popularity', 0))
                    uri = artist.get('uri', '')

                    table.add_row(str(idx), name, genres, popularity, uri)

                console.print(table)

        if search_type == 'album' or search_type == 'all':
            albums = results.get('albums', {}).get('items', [])
            if albums:
                console.print(f"\n[bold yellow]💿 Albums:[/bold yellow]")
                table = Table(box=box.ROUNDED, show_header=True, header_style="bold yellow")
                table.add_column("#", style="dim", width=4)
                table.add_column("Album", style="cyan")
                table.add_column("Artist", style="green")
                table.add_column("Release", style="blue")
                table.add_column("Tracks", justify="right", style="magenta")

                for idx, album in enumerate(albums, 1):
                    name = album.get('name', 'Unknown')
                    artists = ', '.join([a['name'] for a in album.get('artists', [])])
                    release_date = album.get('release_date', 'Unknown')
                    total_tracks = str(album.get('total_tracks', 0))

                    table.add_row(str(idx), name, artists, release_date, total_tracks)

                console.print(table)

        if search_type == 'playlist' or search_type == 'all':
            playlists = results.get('playlists', {}).get('items', [])
            if playlists:
                console.print(f"\n[bold magenta]📚 Playlists:[/bold magenta]")
                table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
                table.add_column("#", style="dim", width=4)
                table.add_column("Name", style="cyan")
                table.add_column("Owner", style="green")
                table.add_column("Tracks", justify="right", style="blue")
                table.add_column("URI", style="dim")

                for idx, playlist in enumerate(playlists, 1):
                    name = playlist.get('name', 'Unknown')
                    owner = playlist.get('owner', {}).get('display_name', 'Unknown')
                    total_tracks = str(playlist.get('tracks', {}).get('total', 0))
                    uri = playlist.get('uri', '')

                    table.add_row(str(idx), name, owner, total_tracks, uri)

                console.print(table)

    except Exception as e:
        handle_api_error(e, console)
