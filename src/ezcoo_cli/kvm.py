"""High-level KVM switch interface."""

import re
from pathlib import Path

from .device import Device
from .models import Command, HelpInfo, OutputRouting, SerialConfig, StreamStatus, SystemStatus


class KVMError(Exception):
    """Base exception for KVM-related errors."""

    pass


class KVM:
    """High-level interface for EZCOO KVM switches.

    This class provides a type-safe, structured interface to KVM functionality
    that can be used both by the CLI and as a library.

    Example:
        >>> from pathlib import Path
        >>> from ezcoo_cli.kvm import KVM
        >>>
        >>> kvm = KVM(Path("/dev/ttyUSB0"))
        >>> status = kvm.get_system_status()
        >>> print(f"Firmware: {status.firmware_version}")
        >>> kvm.switch_input(2)
        >>>
        >>> # For device at address 5
        >>> kvm = KVM(Path("/dev/ttyUSB0"), address=5)
        >>> status = kvm.get_system_status()  # Sends A05EZSTA
    """

    def __init__(
        self,
        device_path: Path,
        baudrate: int = 115200,
        timeout: float = 1.0,
        address: int = 0,
    ):
        """Initialize the KVM interface.

        Args:
            device_path: Path to the serial device (e.g., /dev/ttyUSB0)
            baudrate: Serial communication baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1.0)
            address: Device address (0-99). Use 0 for single device (default).
                     For addresses 1-99, commands will be prefixed with Axx.
        """
        self.device_path = device_path
        self.baudrate = baudrate
        self.timeout = timeout
        self._address = address

        if not 0 <= address <= 99:
            raise ValueError("Address must be between 0 and 99")

    @property
    def address(self) -> int:
        """Get the current address this KVM instance is configured to use."""
        return self._address

    @address.setter
    def address(self, value: int) -> None:
        """Set the address this KVM instance should use for communication.

        Args:
            value: Address to use (0-99)

        Raises:
            ValueError: If address is invalid

        Note:
            This only changes which address this KVM instance uses for commands.
            It does NOT change the device's actual address. Use set_device_address()
            to change the device's address.
        """
        if not 0 <= value <= 99:
            raise ValueError("Address must be between 0 and 99")
        self._address = value

    def _get_address_prefix(self) -> str:
        """Get the address prefix for commands.

        Returns:
            Empty string for address 0, or Axx for addresses 1-99
        """
        if self._address == 0:
            return ""
        return f"A{self._address:02d}"

    def _parse_status_output(self, command: str, lines: list[str]) -> SystemStatus:
        """Parse EZSTA command output into SystemStatus.

        Expected format:
        - "System Address = XX           F/W Version : X.XX"
        - "RS232                         : Baud Rate=115200bps ..."
        """
        system_address: int | None = None
        firmware_version: str | None = None
        serial_config: SerialConfig | None = None

        # Pattern matches: System Address = <addr>  F/W Version : <version>
        status_pattern = r"System\s+Address\s*=\s*(?P<address>\d+)\s+F/W\s+Version\s*:\s*(?P<version>[\d.]+)"
        # Pattern matches: RS232 ... 115200bps or Baud Rate=115200bps
        serial_pattern = r"(RS232.*115200bps|Baud\s+Rate\s*=\s*115200bps)"

        for line in lines:
            line = line.strip()

            # Try to match system address and firmware version
            match = re.search(status_pattern, line, re.IGNORECASE)
            if match:
                system_address = int(match.group("address"))
                firmware_version = match.group("version")

            # Try to match serial config
            if re.search(serial_pattern, line, re.IGNORECASE):
                serial_config = SerialConfig(
                    baud_rate=115200,
                    data_bits=8,
                    parity="None",
                    stop_bits=1,
                )

        if system_address is None or not firmware_version or not serial_config:
            raise KVMError("Failed to parse system status")

        return SystemStatus(
            command=command,
            raw_response=lines,
            system_address=system_address,
            firmware_version=firmware_version,
            serial_config=serial_config,
        )

    def _parse_help_output(self, command: str, lines: list[str]) -> HelpInfo:
        """Parse EZH command output into HelpInfo.

        Expected format:
        - "F/W Version : X.XX"
        - "=   COMMAND : Description"
        """
        commands: list[Command] = []
        firmware_version: str | None = None

        # Pattern matches: F/W Version : <version>
        version_pattern = r"F/W\s+Version\s*:\s*(?P<version>[\d.]+)"
        # Pattern matches: =   COMMAND_NAME : Description
        # Captures everything from EZ to the colon (trimmed)
        command_pattern = r"^=\s+(?P<command>EZ[^:]+?)\s*:\s*(?P<description>.+)$"

        for line in lines:
            line = line.strip()

            # Try to match firmware version
            version_match = re.search(version_pattern, line, re.IGNORECASE)
            if version_match:
                firmware_version = version_match.group("version")

            # Try to match command entries
            cmd_match = re.match(command_pattern, line)
            if cmd_match:
                cmd_name = cmd_match.group("command")
                cmd_desc = cmd_match.group("description").strip()
                commands.append(Command(command=cmd_name, description=cmd_desc))

        return HelpInfo(
            command=command,
            raw_response=lines,
            firmware_version=firmware_version,
            commands=commands,
            total_commands=len(commands),
        )

    def _parse_routing_output(self, command: str, lines: list[str]) -> OutputRouting:
        """Parse EZG OUTx VS command output into OutputRouting.

        Expected format: "OUTx VS y" where x is output number and y is input number.
        """
        # Pattern matches: OUT<output_num> VS <input_num>
        pattern = r"OUT(?P<output>\d+)\s+VS\s+(?P<input>\d+)"

        for line in lines:
            match = re.search(pattern, line.strip())
            if not match:
                continue

            output_num = int(match.group("output"))
            input_num = int(match.group("input"))

            return OutputRouting(
                command=command,
                raw_response=lines,
                output=output_num,
                input=input_num,
            )

        raise KVMError("Failed to parse routing output")

    def _parse_stream_output(self, command: str, lines: list[str]) -> StreamStatus:
        """Parse EZG OUTx STREAM command output into StreamStatus.

        Expected format: "OUT <output_num> STREAM <status>" where status is ON or OFF.
        """
        # Pattern matches: OUT <output_num> STREAM <status>
        pattern = r"OUT\s+(?P<output>\d+)\s+STREAM\s+(?P<status>ON|OFF)"

        for line in lines:
            match = re.search(pattern, line.strip(), re.IGNORECASE)
            if not match:
                continue

            output_num = int(match.group("output"))
            status_str = match.group("status").lower()
            enabled = match.group("status").upper() == "ON"

            return StreamStatus(
                command=command,
                raw_response=lines,
                output=output_num,
                status=status_str,
                enabled=enabled,
            )

        raise KVMError("Failed to parse stream output")

    def get_system_status(self) -> SystemStatus:
        """Get system status information.

        Returns:
            SystemStatus with device information

        Raises:
            KVMError: If the command fails or response cannot be parsed
        """
        prefix = self._get_address_prefix()
        command = f"{prefix}EZSTA"
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(command)
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_status_output(command, lines)

    def get_help(self) -> HelpInfo:
        """Get device help information.

        Returns:
            HelpInfo with available commands

        Raises:
            KVMError: If the command fails or response cannot be parsed
        """
        prefix = self._get_address_prefix()
        command = f"{prefix}EZH"
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(command)
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_help_output(command, lines)

    def switch_input(self, input_num: int, output_num: int = 1) -> None:
        """Switch an input to the specified output.

        Args:
            input_num: Input number to switch (1-4)
            output_num: Output number (default: 1, only 1 supported)

        Raises:
            KVMError: If the command fails
            ValueError: If input/output numbers are invalid
        """
        if not 1 <= input_num <= 4:
            raise ValueError("Input number must be between 1 and 4")
        if output_num != 1:
            raise ValueError("Only output 1 is supported")

        prefix = self._get_address_prefix()
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(f"{prefix}EZS OUT{output_num} VS IN{input_num}")
            # SET commands don't return responses, so no need to read

    def get_output_routing(self, output_num: int = 1) -> OutputRouting:
        """Get current output routing.

        Args:
            output_num: Output number to query (default: 1, only 1 supported)

        Returns:
            OutputRouting with current connection

        Raises:
            KVMError: If the command fails or response cannot be parsed
            ValueError: If output number is invalid
        """
        if output_num != 1:
            raise ValueError("Only output 1 is supported")

        prefix = self._get_address_prefix()
        command = f"{prefix}EZG OUT{output_num} VS"
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(command)
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_routing_output(command, lines)

    def get_stream_status(self, output_num: int = 1) -> StreamStatus:
        """Get output stream status.

        Args:
            output_num: Output number to query (default: 1, only 1 supported)

        Returns:
            StreamStatus with current stream state

        Raises:
            KVMError: If the command fails or response cannot be parsed
            ValueError: If output number is invalid
        """
        if output_num != 1:
            raise ValueError("Only output 1 is supported")

        prefix = self._get_address_prefix()
        command = f"{prefix}EZG OUT{output_num} STREAM"
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(command)
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_stream_output(command, lines)

    def set_device_address(self, new_address: int) -> None:
        """Set the device's address.

        Args:
            new_address: New address to set (0-99)

        Raises:
            ValueError: If address is invalid
            KVMError: If the command fails

        Warning:
            After changing the device's address, you must update this KVM instance's
            address property to continue communicating with the device.

        Example:
            >>> kvm = KVM(Path("/dev/ttyUSB0"), address=0)
            >>> kvm.set_device_address(5)
            >>> kvm.address = 5  # Update instance to use new address
        """
        if not 0 <= new_address <= 99:
            raise ValueError("Address must be between 0 and 99")

        prefix = self._get_address_prefix()
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(f"{prefix}EZS ADDR {new_address:02d}")
            # SET commands don't return responses
