import contextlib
from pathlib import Path
from types import TracebackType
from typing import Generator, Self

import serial


class DeviceError(Exception):
    """Base exception for device-related errors."""

    pass


class DeviceConnectionError(DeviceError):
    """Raised when device connection fails."""

    pass


class Device(contextlib.AbstractContextManager["Device"]):
    """A context manager for communicating with EZCOO KVM switches via serial interface.

    This class can be used both as a CLI tool and as a library component.

    Example:
        >>> from ezcoo_cli.device import Device
        >>> from pathlib import Path
        >>>
        >>> with Device(Path("/dev/ttyUSB0")) as device:
        ...     device.write("EZS OUT1 VS IN2")
    """

    def __init__(self, path: Path, baudrate: int = 115200, timeout: float = 1.0) -> None:
        """Initialize the Device.

        Args:
            path: Path to the serial device (e.g., /dev/ttyUSB0)
            baudrate: Serial communication baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1)
        """
        self._path = path
        self._serial = serial.Serial()
        self._serial.port = str(path)
        self._serial.baudrate = baudrate
        self._serial.timeout = timeout

    def __enter__(self) -> Self:
        try:
            self._serial.open()
        except serial.SerialException as e:
            raise DeviceConnectionError(f"Failed to open device {self._path}: {e}") from e
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._serial.is_open:
            self._serial.close()

    @staticmethod
    def validate_command(cmd: str) -> None:
        """Validate that a command only contains safe characters.

        Args:
            cmd: Command string to validate

        Raises:
            DeviceError: If command contains invalid characters
        """
        # Only allow ASCII alphanumeric characters and regular spaces (not tabs, newlines, etc.)
        if not all(c.isalnum() or c == " " for c in cmd):
            raise DeviceError(
                f"Command contains invalid characters. Only ASCII alphanumeric and spaces allowed: {cmd!r}"
            )

    def write(self, cmd: str) -> None:
        """Write a command to the device.

        Args:
            cmd: Command string to send to the device

        Raises:
            DeviceError: If writing to device fails or command contains invalid characters
        """
        if not self._serial.is_open:
            raise DeviceError("Device is not open")

        # Validate command before sending
        self.validate_command(cmd)

        try:
            buffer = (cmd + "\n").encode("ascii")
            self._serial.write(buffer)
        except UnicodeEncodeError as e:
            raise DeviceError(f"Command contains non-ASCII characters: {e}") from e
        except serial.SerialException as e:
            raise DeviceError(f"Failed to write to device: {e}") from e

    def readlines(self) -> Generator[str, None, None]:
        """Read lines from the device until no more data is available.

        Yields:
            str: Each line received from the device

        Raises:
            DeviceError: If reading from device fails
        """
        if not self._serial.is_open:
            raise DeviceError("Device is not open")

        while True:
            try:
                read = self._serial.read_until()
                if not read:
                    break
                yield read.decode("ascii")
            except serial.SerialException as e:
                raise DeviceError(f"Failed to read from device: {e}") from e
            except UnicodeDecodeError as e:
                raise DeviceError(f"Failed to decode device response: {e}") from e
