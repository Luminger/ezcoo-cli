#!/usr/bin/env python
from pathlib import Path

import click

from . import __version__
from .device import Device

device_option = click.option(
    "-d",
    "--device",
    type=click.Path(
        exists=True, dir_okay=False, writable=True, readable=True, path_type=Path
    ),
    required=True,
    default="/dev/ttyUSB0",
)


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    pass


@main.group()
def input() -> None:
    pass


@input.command()
@device_option
@click.argument("input", type=click.IntRange(1, 8), required=True)
@click.option("--output", type=click.IntRange(1, 2), default=1, help="Output to switch")
def switch(device: Path, input: int, output: int) -> None:
    with Device(device) as client:
        client.write(f"EZS OUT{output} VS IN{input}")


@input.command()
@device_option
def edid(device: Path) -> None:
    with Device(device) as client:
        client.write("EZG IN0 EDID")
        for line in client.readlines():
            print(line, end="")


@main.command()
@device_option
def help(device: Path) -> None:
    with Device(device) as client:
        client.write("EZH")
        for line in client.readlines():
            print(line, end="")
