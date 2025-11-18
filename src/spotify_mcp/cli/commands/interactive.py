"""
Interactive mode - Interactive shell for Spotify control.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ..utils import get_client, show_success, show_error


@click.command()
@click.pass_context
def interactive(ctx):
    """
    Interactive mode for Spotify control.

    Provides a continuous shell for quick Spotify commands.
    Type 'help' for available commands or 'exit' to quit.
    """
    console = ctx.obj.get('console', Console())

    # Welcome message
    console.print(Panel(
        "[bold cyan]🎵 Spotify Interactive Mode[/bold cyan]\n\n"
        "Quick commands: play, pause, next, prev, status, search <query>, exit\n"
        "[dim]Type 'help' for full command list[/dim]",
        border_style="cyan"
    ))

    # Initialize client
    try:
        client = get_client()
    except Exception as e:
        show_error(f"Failed to initialize client: {e}", console)
        return

    # Interactive loop
    while True:
        try:
            # Get command from user
            cmd = Prompt.ask("\n[bold cyan]spotify[/bold cyan]").strip().lower()

            if not cmd:
                continue

            # Parse command
            parts = cmd.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ''

            # Handle commands
            if command in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break

            elif command == 'help':
                console.print("""
[bold]Available Commands:[/bold]

[cyan]Playback Control:[/cyan]
  play [uri]    - Start/resume playback
  pause         - Pause playback
  next          - Skip to next track
  prev          - Skip to previous track
  status        - Show current playback status

[cyan]Search & Discovery:[/cyan]
  search <query>    - Search for tracks
  find <query>      - Alias for search

[cyan]Library:[/cyan]
  tracks        - List saved tracks
  save          - Save current track

[cyan]Other:[/cyan]
  devices       - List available devices
  help          - Show this help
  exit          - Exit interactive mode
""")

            elif command == 'play':
                if args:
                    if args.startswith('spotify:track:'):
                        client.play(uris=[args])
                    else:
                        client.play(context_uri=args)
                else:
                    client.play()
                show_success("Playback started", console)

            elif command == 'pause':
                client.pause()
                show_success("Playback paused", console)

            elif command in ['next', 'skip']:
                client.skip_next()
                show_success("Skipped to next track", console)

            elif command in ['prev', 'previous', 'back']:
                client.skip_previous()
                show_success("Skipped to previous track", console)

            elif command == 'status':
                playback = client.current_playback()
                if playback and playback.get('item'):
                    item = playback['item']
                    is_playing = playback.get('is_playing', False)
                    state = "▶ Playing" if is_playing else "⏸ Paused"

                    track = item.get('name', 'Unknown')
                    artists = ', '.join([a['name'] for a in item.get('artists', [])])

                    console.print(f"\n{state}: [cyan]{track}[/cyan] by [green]{artists}[/green]")
                else:
                    console.print("[yellow]No track currently playing[/yellow]")

            elif command in ['search', 'find']:
                if not args:
                    show_error("Please provide a search query", console)
                    continue

                results = client.search(q=args, limit=5, type='track')
                tracks = results.get('tracks', {}).get('items', [])

                if tracks:
                    console.print("\n[bold cyan]Search Results:[/bold cyan]")
                    for idx, track in enumerate(tracks, 1):
                        name = track.get('name', 'Unknown')
                        artists = ', '.join([a['name'] for a in track.get('artists', [])])
                        uri = track.get('uri', '')
                        console.print(f"  {idx}. {name} - {artists}")
                        console.print(f"     [dim]{uri}[/dim]")
                else:
                    show_error(f"No results found for '{args}'", console)

            elif command == 'tracks':
                result = client.get_saved_tracks(limit=10)
                items = result.get('items', [])

                if items:
                    console.print("\n[bold cyan]Your Saved Tracks:[/bold cyan]")
                    for idx, item in enumerate(items, 1):
                        track = item.get('track', {})
                        name = track.get('name', 'Unknown')
                        artists = ', '.join([a['name'] for a in track.get('artists', [])])
                        console.print(f"  {idx}. {name} - {artists}")
                else:
                    console.print("[yellow]No saved tracks found[/yellow]")

            elif command == 'devices':
                result = client.get_available_devices()
                devices = result.get('devices', [])

                if devices:
                    console.print("\n[bold cyan]Available Devices:[/bold cyan]")
                    for idx, dev in enumerate(devices, 1):
                        name = dev.get('name', 'Unknown')
                        is_active = "✓" if dev.get('is_active') else ""
                        console.print(f"  {idx}. {name} {is_active}")
                else:
                    console.print("[yellow]No devices found[/yellow]")

            elif command == 'save':
                playback = client.current_playback()
                if playback and playback.get('item'):
                    track_id = playback['item']['id']
                    client.save_tracks([track_id])
                    show_success("Current track saved to library", console)
                else:
                    show_error("No track currently playing", console)

            else:
                show_error(f"Unknown command: {command}. Type 'help' for available commands.", console)

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            continue

        except Exception as e:
            show_error(f"Error: {e}", console)
            continue
