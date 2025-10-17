#!/usr/bin/env python
import json
from dataclasses import asdict
from pathlib import Path

import click

from . import __version__
from .device import Device
from .kvm import KVM, KVMCommandNotSupportedError, KVMError

device_option = click.option(
    "-d",
    "--device",
    type=click.Path(exists=True, dir_okay=False, writable=True, readable=True, path_type=Path),
    required=True,
    default="/dev/ttyUSB0",
)


def get_raw_output(device: Path, command: str) -> None:
    """Helper to get raw output from device for a command."""
    with Device(device) as client:
        client.write(command)
        for line in client.readlines():
            print(line, end="")


def format_pretty_status(status):
    """Format SystemStatus for pretty output."""
    click.echo(f"System Address: {status.system_address}")
    click.echo(f"Firmware Version: {status.firmware_version}")
    config = status.serial_config
    click.echo(f"Serial Port: {config.baud_rate} baud, {config.data_bits}{config.parity[0]}{config.stop_bits}")


def format_pretty_help(help_info):
    """Format HelpInfo for pretty output."""
    click.echo("EZCOO Device Help Summary:")
    click.echo("=" * 40)

    if help_info.firmware_version:
        click.echo(f"Firmware Version: {help_info.firmware_version}")

    for cmd in help_info.commands:
        click.echo(f"  {cmd.command}: {cmd.description}")

    click.echo(f"\nTotal commands available: {help_info.total_commands}")


def format_pretty_routing(routing):
    """Format OutputRouting for pretty output."""
    click.echo(f"Output {routing.output} is connected to Input {routing.input}")


def format_pretty_stream(stream):
    """Format StreamStatus for pretty output."""
    click.echo(f"Output {stream.output} stream is {stream.status}")


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
@click.option("--pretty", is_flag=True, help="Format output in human-readable form")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def status(device: Path, pretty: bool, output_json: bool) -> None:
    """Show global system status."""
    try:
        kvm = KVM(device)
        status_info = kvm.get_system_status()

        if output_json:
            click.echo(json.dumps(asdict(status_info), indent=2))
        elif pretty:
            format_pretty_status(status_info)
        else:
            get_raw_output(device, "EZSTA")
    except KVMError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@device_option
@click.option("--pretty", is_flag=True, help="Format output in human-readable form")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def help(device: Path, pretty: bool, output_json: bool) -> None:
    """Get help information from the device."""
    try:
        kvm = KVM(device)
        help_info = kvm.get_help()

        if output_json:
            click.echo(json.dumps(asdict(help_info), indent=2))
        elif pretty:
            format_pretty_help(help_info)
        else:
            get_raw_output(device, "EZH")
    except KVMError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def input() -> None:
    """Commands for managing inputs."""
    pass


@input.command()
@device_option
@click.argument("input", type=click.IntRange(1, 4), required=True)
@click.option("--output", type=click.IntRange(1, 1), default=1, help="Output to switch (only output 1 supported)")
def switch(device: Path, input: int, output: int) -> None:
    """Switch an input to the specified output.

    INPUT: Input number to switch (1-4)
    """
    try:
        kvm = KVM(device)
        kvm.switch_input(input, output)
        click.echo(f"Switched input {input} to output {output}")
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@input.command()
@device_option
def edid(device: Path) -> None:
    """Get EDID information from the device (UNCONFIRMED - may not work on F/W 2.03)."""
    click.echo("⚠️  WARNING: This command is not confirmed to work on firmware 2.03", err=True)
    try:
        kvm = KVM(device)
        kvm.get_edid_info()
    except KVMCommandNotSupportedError as e:
        click.echo(f"Command not supported: {e}", err=True)
    except KVMError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@input.command()
@device_option
@click.argument("input", type=click.IntRange(1, 4), required=True)
def signal(device: Path, input: int) -> None:
    """Get input signal status (UNCONFIRMED - may not work on F/W 2.03).

    INPUT: Input number to check (1-4)
    """
    click.echo("⚠️  WARNING: This command is not confirmed to work on firmware 2.03", err=True)
    try:
        kvm = KVM(device)
        kvm.get_input_signal_status(input)
    except KVMCommandNotSupportedError as e:
        click.echo(f"Command not supported: {e}", err=True)
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def output() -> None:
    """Commands for managing outputs."""
    pass


@output.command()
@device_option
@click.option("--output", type=click.IntRange(1, 1), default=1, help="Output to query (only output 1 supported)")
@click.option("--pretty", is_flag=True, help="Format output in human-readable form")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def routing(device: Path, output: int, pretty: bool, output_json: bool) -> None:
    """Get current output video routing."""
    try:
        kvm = KVM(device)
        routing_info = kvm.get_output_routing(output)

        if output_json:
            click.echo(json.dumps(asdict(routing_info), indent=2))
        elif pretty:
            format_pretty_routing(routing_info)
        else:
            get_raw_output(device, f"EZG OUT{output} VS")
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@output.command()
@device_option
@click.option("--output", type=click.IntRange(1, 1), default=1, help="Output to query (only output 1 supported)")
@click.option("--pretty", is_flag=True, help="Format output in human-readable form")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def stream(device: Path, output: int, pretty: bool, output_json: bool) -> None:
    """Get output stream status."""
    try:
        kvm = KVM(device)
        stream_info = kvm.get_stream_status(output)

        if output_json:
            click.echo(json.dumps(asdict(stream_info), indent=2))
        elif pretty:
            format_pretty_stream(stream_info)
        else:
            get_raw_output(device, f"EZG OUT{output} STREAM")
    except (KVMError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.group()
def system() -> None:
    """System management commands."""
    pass


@system.command()
@device_option
def address(device: Path) -> None:
    """Get system address (UNCONFIRMED - may not work on F/W 2.03)."""
    click.echo("⚠️  WARNING: This command is not confirmed to work on firmware 2.03", err=True)
    try:
        with Device(device) as client:
            client.write("EZG ADDR")
            response_found = False
            for line in client.readlines():
                response_found = True
                print(line, end="")
            if not response_found:
                click.echo("No response received - command may not be implemented in this firmware version", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@system.command()
@device_option
def auto_mode(device: Path) -> None:
    """Get auto switch mode status (UNCONFIRMED - may not work on F/W 2.03)."""
    click.echo("⚠️  WARNING: This command is not confirmed to work on firmware 2.03", err=True)
    try:
        with Device(device) as client:
            client.write("EZG AUTO MODE")
            response_found = False
            for line in client.readlines():
                response_found = True
                print(line, end="")
            if not response_found:
                click.echo("No response received - command may not be implemented in this firmware version", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
