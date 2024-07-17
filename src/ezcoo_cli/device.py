import contextlib
from pathlib import Path
from types import TracebackType
from typing import Generator, Type

import serial


class Device(contextlib.AbstractContextManager):
    def __init__(self, path: Path) -> None:
        self._serial = serial.Serial()
        self._serial.port = str(path)
        self._serial.baudrate = 115200
        self._serial.timeout = 1

    def __enter__(self) -> "Device":
        self._serial.open()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._serial.close()

    def write(self, cmd: str) -> None:
        buffer = (cmd + "\n").encode("ascii")
        self._serial.write(buffer)

    def readlines(self) -> Generator[str, None, None]:
        while True:
            read = self._serial.read_until()
            if not read:
                break

            yield read.decode("ascii")
