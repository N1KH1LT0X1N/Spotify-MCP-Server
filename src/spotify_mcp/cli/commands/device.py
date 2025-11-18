"""
Device commands - Manage Spotify devices.
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box

from ..utils import (
    get_client,
    show_success,
    handle_api_error,
    show_error
)


@click.group()
def device():
    """
    Device management commands.

    List available devices and transfer playback between them.
    """
    pass


@device.command('list')
@click.pass_context
def list_devices(ctx):
    """List all available Spotify devices."""
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        result = client.get_available_devices()
        devices = result.get('devices', [])

        if not devices:
            console.print("[yellow]No devices found[/yellow]")
            return

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Active", style="magenta")
        table.add_column("Volume", justify="right", style="blue")
        table.add_column("ID", style="dim")

        for idx, dev in enumerate(devices, 1):
            name = dev.get('name', 'Unknown')
            dev_type = dev.get('type', 'Unknown')
            is_active = "✓" if dev.get('is_active') else ""
            volume = f"{dev.get('volume_percent', 0)}%"
            dev_id = dev.get('id', '')

            active_style = "[green]" if dev.get('is_active') else ""
            end_style = "[/green]" if dev.get('is_active') else ""

            table.add_row(
                str(idx),
                f"{active_style}{name}{end_style}",
                dev_type,
                is_active,
                volume,
                dev_id
            )

        console.print(table)
        console.print("\n[dim]Use 'device transfer <id>' to switch playback[/dim]")

    except Exception as e:
        handle_api_error(e, console)


@device.command()
@click.argument('device_id')
@click.option('--play/--no-play', default=True, help='Start playback on new device')
@click.pass_context
def transfer(ctx, device_id, play):
    """
    Transfer playback to another device.

    DEVICE_ID: Spotify device ID
    """
    console = ctx.obj.get('console', Console())
    client = get_client()

    try:
        client.transfer_playback(device_id, force_play=play)
        show_success(f"Playback transferred to device", console)
    except Exception as e:
        handle_api_error(e, console)
