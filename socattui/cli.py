"""CLI interface for SocatTUI."""

import sys
import click

from .config import load_config
from .socat import start_all, stop_all, get_status, _build_socat_cmd
from .detector import detect_devices


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SocatTUI - USB Serial Bridge Manager"""
    pass


@cli.command()
def tui():
    """Launch the TUI interface."""
    from .app import run_tui
    run_tui()


@cli.command()
def up():
    """Start all configured bridges."""
    config = load_config()
    if not config.bridges:
        click.echo("No bridges configured. Run 'socattui tui' to add bridges.")
        sys.exit(1)

    results = start_all(config, detached=True)
    for name, success in results.items():
        status = "started" if success else "FAILED"
        click.echo(f"  {name}: {status}")

    started = sum(1 for v in results.values() if v)
    click.echo(f"\n{started}/{len(results)} bridges started")


@cli.command()
def down():
    """Stop all configured bridges."""
    config = load_config()
    if not config.bridges:
        click.echo("No bridges configured.")
        return

    results = stop_all(config)
    for name, success in results.items():
        status = "stopped" if success else "FAILED"
        click.echo(f"  {name}: {status}")

    stopped = sum(1 for v in results.values() if v)
    click.echo(f"\n{stopped}/{len(results)} bridges stopped")


@cli.command()
def list():
    """List configured bridges and their status."""
    config = load_config()
    if not config.bridges:
        click.echo("No bridges configured.")
        return

    status = get_status(config)
    click.echo("\nConfigured Bridges:")
    click.echo("-" * 60)

    for bridge in config.bridges:
        bridge_status = status.get(bridge.name, {})
        running = bridge_status.get("running", False)
        pid = bridge_status.get("pid")
        status_text = f"RUNNING (PID: {pid})" if running else "STOPPED"
        cmd = _build_socat_cmd(bridge)
        click.echo(f"  {bridge.name}")
        click.echo(f"    Device:  {bridge.device}")
        click.echo(f"    Port:    {bridge.port}")
        click.echo(f"    Baud:    {bridge.baudrate}")
        click.echo(f"    Status:  {status_text}")
        click.echo(f"    Command: {' '.join(cmd)}")
        click.echo()


@cli.command()
def detect():
    """Detect available USB serial devices."""
    devices = detect_devices()
    if not devices:
        click.echo("No USB serial devices detected.")
        return

    click.echo("\nDetected USB Serial Devices:")
    click.echo("-" * 40)
    for dev in devices:
        desc = f" - {dev.description}" if dev.description else ""
        click.echo(f"  {dev.path}{desc}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
