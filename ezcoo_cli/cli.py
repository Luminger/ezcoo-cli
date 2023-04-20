#!/usr/bin/env python
import contextlib
import io

from collections.abc import Iterable
from dataclasses import dataclass
from types import TracebackType
from typing import Optional
from pathlib import Path

import attrs
import click
import serial

class Ezcoo(contextlib.AbstractContextManager):
    def __init__(self, path: Path) -> None:
        self._serial = serial.Serial()
        self._serial.port = str(path)
        self._serial.baudrate = 115600
        self._serial.timeout = 0.2


    def __enter__(self) -> "Ezcoo":
        self._serial.open()
        self._buffered = io.BufferedRWPair(self._serial, self._serial)
        self._textio = io.TextIOWrapper(self._buffered, line_buffering=True, newline='\r\n')

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._serial.close()

    def write(self, cmd: str) -> None:
        self._textio.write(cmd + "\n")

    def readlines(self) -> Iterable[str]:
        return self._textio.readlines()

device_option = click.option('-d', '--device', type=click.Path(exists=True, dir_okay=False, writable=True, readable=True, path_type=Path), default="/dev/ttyUSB0", required=True)
input_argument = click.argument("input", type=click.IntRange(1,4), required=True)

@click.group()
def cli() -> None:
    pass

@cli.group()
def input() -> None:
    pass

@input.command()
@device_option
@input_argument
@click.option("--output", type=click.IntRange(1,1), default=1, help="Output to switch")
def switch(device: Path, input: int, output: int) -> None:
    with Ezcoo(device) as client:
        client.write(f"EZS OUT{output} VS IN{input}")

@input.command()
@device_option
def edid(device: Path) -> None:
    with Ezcoo(device) as client:
        client.write("EZG IN0 EDID")
        data = client.readlines()
        for line in data:
            print(line, end='')

@cli.command()
@device_option
def help(device: Path) -> None:
    with Ezcoo(device) as client:
        client.write("EZH")
        data = client.readlines()
        for line in data:
            print(line, end='')

if __name__ == "__main__":
    cli()