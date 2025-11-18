"""
Playback commands - Control Spotify playback.
"""

import click
from rich.console import Console

from ..utils import (
    get_client,
    show_success,
    show_error,
    handle_api_error
)


@click.group()
def playback():
    """
    Playback control commands.

    Play, pause, skip, volume control, shuffle, and repeat settings.
    """
    pass


@playback.command()
@click.argument('uri', required=False)
@click.option('--context', '-c', help='Context URI (playlist, album, artist)')
@click.pass_context
def play(ctx, uri, context):
    """
    Start or resume playback.

    URI: Optional Spotify URI (track, playlist, album, artist)
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        kwargs = {}
        if uri:
            if uri.startswith('spotify:track:'):
                kwargs['uris'] = [uri]
            else:
                kwargs['context_uri'] = uri
        elif context:
            kwargs['context_uri'] = context

        client.play(**kwargs)
        show_success("Playback started", console)

    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.pass_context
def pause(ctx):
    """Pause playback."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.pause()
        show_success("Playback paused", console)
    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.pass_context
def next(ctx):
    """Skip to next track."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.skip_next()
        show_success("Skipped to next track", console)
    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.pass_context
def previous(ctx):
    """Skip to previous track."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.skip_previous()
        show_success("Skipped to previous track", console)
    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.argument('level', type=click.IntRange(0, 100))
@click.pass_context
def volume(ctx, level):
    """
    Set playback volume.

    LEVEL: Volume level (0-100)
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.set_volume(level)
        show_success(f"Volume set to {level}%", console)
    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.argument('state', type=click.Choice(['on', 'off', 'toggle']))
@click.pass_context
def shuffle(ctx, state):
    """
    Set shuffle mode.

    STATE: on, off, or toggle
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        if state == 'toggle':
            # Get current state and toggle
            playback_state = client.current_playback()
            if playback_state:
                current = playback_state.get('shuffle_state', False)
                state = 'off' if current else 'on'
            else:
                show_error("No active playback to toggle", console)
                return

        shuffle_on = (state == 'on')
        client.set_shuffle(shuffle_on)
        show_success(f"Shuffle turned {state}", console)

    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.argument('mode', type=click.Choice(['off', 'track', 'context']))
@click.pass_context
def repeat(ctx, mode):
    """
    Set repeat mode.

    MODE: off, track, or context (playlist/album)
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.set_repeat(mode)
        show_success(f"Repeat mode set to {mode}", console)
    except Exception as e:
        handle_api_error(e, console)


@playback.command()
@click.argument('position', type=int)
@click.pass_context
def seek(ctx, position):
    """
    Seek to position in current track.

    POSITION: Position in seconds
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        position_ms = position * 1000
        client.seek_to_position(position_ms)
        show_success(f"Seeked to {position} seconds", console)
    except Exception as e:
        handle_api_error(e, console)
