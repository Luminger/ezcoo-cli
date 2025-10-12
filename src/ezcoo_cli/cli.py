#!/usr/bin/env python
import json
from dataclasses import asdict
from pathlib import Path

import click

from . import __version__
from .kvm import KVM, KVMError
from .models import DiscoveredDevice

device_option = click.option(
    "-d",
    "--device",
    type=click.Path(
        exists=True,
        dir_okay=False,
        writable=True,
        readable=True,
        path_type=Path,
    ),
    required=True,
    default="/dev/ttyUSB0",
)

address_option = click.option(
    "-a",
    "--address",
    type=click.IntRange(0, 99),
    default=0,
    help="Device address (0-99). Use 0 for single device mode (default).",
)

format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(["raw", "json", "pretty"], case_sensitive=False),
    default="pretty",
    help="Output format (default: pretty)",
)


@click.group()
def main() -> None:
    """A tool to control EZCOO KVM switches via the serial interface."""
    pass


@main.command()
def version() -> None:
    """Show the version and exit."""
    click.echo(__version__)


@main.command()
@device_option
@address_option
@format_option
def status(device: Path, address: int, format: str) -> None:
    """Show global system status."""
    try:
        kvm = KVM(device, address=address)
        status_response = kvm.get_system_status()

        match format:
            case "json":
                click.echo(json.dumps(asdict(status_response), indent=2))
            case "pretty":
                click.echo(f"System Address: {status_response.response.system_address:02d}")
                click.echo(f"Firmware Version: {status_response.response.firmware_version}")
            case _:  # raw
                click.echo("".join(status_response.raw_response), nl=False)
    except KVMError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@device_option
@address_option
@format_option
def help(device: Path, address: int, format: str) -> None:
    """Get help information from the device."""
    try:
        kvm = KVM(device, address=address)
        help_response = kvm.get_help()

        match format:
            case "json":
                click.echo(json.dumps(asdict(help_response), indent=2))
            case "pretty":
                click.echo("EZCOO Device Help Summary:")
                click.echo("=" * 40)

                if help_response.response.firmware_version:
                    click.echo(f"Firmware Version: {help_response.response.firmware_version}")

                for cmd in help_response.response.commands:
                    click.echo(f"  {cmd.command}: {cmd.description}")

                click.echo(f"\nTotal commands available: {help_response.response.total_commands}")
            case _:  # raw
                click.echo("".join(help_response.raw_response), nl=False)
    except KVMError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def input() -> None:
    """Commands for managing inputs."""
    pass


@input.command()
@device_option
@address_option
@click.argument("input", type=click.IntRange(1, 4), required=True)
@click.option(
    "--output",
    type=click.IntRange(1, 1),
    default=1,
    help="Output to switch (only output 1 supported)",
)
def switch(device: Path, address: int, input: int, output: int) -> None:
    """Switch an input to the specified output.

    INPUT: Input number to switch (1-4)
    """
    try:
        kvm = KVM(device, address=address)
        kvm.switch_input(input, output_num=output)
        click.echo(f"Switched input {input} to output {output}")
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def output() -> None:
    """Commands for managing outputs."""
    pass


@output.command()
@device_option
@address_option
@click.option(
    "--output",
    type=click.IntRange(1, 1),
    default=1,
    help="Output to query (only output 1 supported)",
)
@format_option
def routing(device: Path, address: int, output: int, format: str) -> None:
    """Get current output video routing."""
    try:
        kvm = KVM(device, address=address)
        routing_response = kvm.get_output_routing(output)

        match format:
            case "json":
                click.echo(json.dumps(asdict(routing_response), indent=2))
            case "pretty":
                click.echo(
                    f"Output {routing_response.response.output} is connected to Input {routing_response.response.input}"
                )
            case _:  # raw
                click.echo("".join(routing_response.raw_response), nl=False)
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@output.command()
@device_option
@address_option
@click.option(
    "--output",
    type=click.IntRange(1, 1),
    default=1,
    help="Output to query (only output 1 supported)",
)
@format_option
def stream(device: Path, address: int, output: int, format: str) -> None:
    """Get output stream status."""
    try:
        kvm = KVM(device, address=address)
        stream_response = kvm.get_stream_status(output)

        match format:
            case "json":
                click.echo(json.dumps(asdict(stream_response), indent=2))
            case "pretty":
                click.echo(f"Output {stream_response.response.output} stream is {stream_response.response.status}")
            case _:  # raw
                click.echo("".join(stream_response.raw_response), nl=False)
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def system() -> None:
    """System management commands."""
    pass


@system.command()
@device_option
@address_option
@click.argument("new_address", type=click.IntRange(0, 99), required=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def set_address(device: Path, address: int, new_address: int, yes: bool) -> None:
    """Set the device address.

    NEW_ADDRESS: New address to set (0-99)

    Warning: After changing the address, you must use --address option
    to communicate with the device at its new address.
    """
    try:
        # Confirm the change unless --yes is used
        if not yes:
            click.echo(f"This will change the device address from {address} to {new_address}")
            click.echo("After this change, you must use --address {new_address} to communicate with the device")
            if not click.confirm("Do you want to continue?"):
                click.echo("Address change cancelled")
                return

        kvm = KVM(device, address=address)
        kvm.set_device_address(new_address)
        click.echo(f"Device address changed from {address} to {new_address}")
        click.echo(f"\nTo communicate with the device now, use: --address {new_address}")
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@system.command()
@device_option
@click.option("--start", type=click.IntRange(0, 99), default=0, help="Start address (default: 0)")
@click.option("--end", type=click.IntRange(0, 99), default=99, help="End address (default: 99)")
@format_option
def discover(device: Path, start: int, end: int, format: str) -> None:
    """Discover devices by scanning address range.

    This command scans the specified address range to find all responding devices.
    """
    if start > end:
        click.echo("Error: Start address must be less than or equal to end address", err=True)
        raise click.Abort()

    try:
        if format != "json":
            click.echo(f"Scanning addresses {start} to {end}...", err=True)

        found_devices: list[DiscoveredDevice] = []

        for addr in range(start, end + 1):
            try:
                kvm = KVM(device, address=addr)
                status = kvm.get_system_status()
                found_devices.append(
                    DiscoveredDevice(
                        address=addr,
                        firmware=status.response.firmware_version,
                        system_address=status.response.system_address,
                    )
                )
                if format != "json":
                    click.echo(f"Found device at address {addr} (firmware: {status.response.firmware_version})")
            except (KVMError, Exception):
                # No device at this address
                continue

        match format:
            case "json":
                click.echo(json.dumps([asdict(d) for d in found_devices], indent=2))
            case _:
                if not found_devices:
                    click.echo("\nNo devices found in the specified range")
                else:
                    click.echo(f"\nTotal devices found: {len(found_devices)}")

    except Exception as e:
        click.echo(f"Error during discovery: {e}", err=True)
        raise click.Abort() from e
