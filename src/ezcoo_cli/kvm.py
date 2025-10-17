"""High-level KVM switch interface."""

from pathlib import Path
from typing import Optional

from .device import Device
from .models import Command, HelpInfo, OutputRouting, SerialConfig, StreamStatus, SystemStatus


class KVMError(Exception):
    """Base exception for KVM-related errors."""

    pass


class KVMCommandNotSupportedError(KVMError):
    """Raised when a command is not supported by the device firmware."""

    pass


class KVM:
    """High-level interface for EZCOO KVM switches.

    This class provides a type-safe, structured interface to KVM functionality
    that can be used both by the CLI and as a library.

    Args:
        device_path: Path to the serial device (e.g., /dev/ttyUSB0)
        baudrate: Serial communication baud rate (default: 115200)
        timeout: Read timeout in seconds (default: 1.0)

    Example:
        >>> from pathlib import Path
        >>> from ezcoo_cli.kvm import KVM
        >>>
        >>> kvm = KVM(Path("/dev/ttyUSB0"))
        >>> status = kvm.get_system_status()
        >>> print(f"Firmware: {status.firmware_version}")
        >>> kvm.switch_input(2)
    """

    def __init__(self, device_path: Path, baudrate: int = 115200, timeout: float = 1.0):
        self.device_path = device_path
        self.baudrate = baudrate
        self.timeout = timeout

    def _parse_status_output(self, lines: list[str]) -> SystemStatus:
        """Parse EZSTA command output into SystemStatus."""
        system_address = None
        firmware_version = None
        serial_config = None

        for line in lines:
            line = line.strip()
            if "System Address" in line and "F/W Version" in line:
                parts = line.split()
                addr_idx = parts.index("Address") + 2 if "Address" in parts else -1
                fw_idx = parts.index("Version") + 2 if "Version" in parts else -1

                if addr_idx > 0 and addr_idx < len(parts):
                    system_address = parts[addr_idx]
                if fw_idx > 0 and fw_idx < len(parts):
                    firmware_version = parts[fw_idx]
            elif "RS232" in line and "Baud Rate" in line:
                if "115200bps" in line:
                    serial_config = SerialConfig(baud_rate=115200, data_bits=8, parity="None", stop_bits=1)

        if not all([system_address, firmware_version, serial_config]):
            raise KVMError("Failed to parse system status")

        return SystemStatus(
            system_address=system_address, firmware_version=firmware_version, serial_config=serial_config
        )

    def _parse_help_output(self, lines: list[str]) -> HelpInfo:
        """Parse EZH command output into HelpInfo."""
        commands = []
        firmware_version = None

        for line in lines:
            line = line.strip()
            if "F/W Version" in line:
                parts = line.split()
                fw_idx = parts.index("Version") + 2 if "Version" in parts else -1
                if fw_idx > 0 and fw_idx < len(parts):
                    firmware_version = parts[fw_idx]
            elif line.startswith("=   EZ"):
                if ":" in line:
                    cmd_part = line.split(":")[0].strip("= ")
                    desc_part = line.split(":", 1)[1].strip("= ")
                    commands.append(Command(command=cmd_part, description=desc_part))

        return HelpInfo(firmware_version=firmware_version, commands=commands, total_commands=len(commands))

    def _parse_routing_output(self, lines: list[str]) -> OutputRouting:
        """Parse EZG OUTx VS command output into OutputRouting."""
        for line in lines:
            line = line.strip()
            if "OUT" in line and "VS" in line:
                parts = line.split()
                if len(parts) >= 3:
                    output_num = int(parts[0].replace("OUT", ""))
                    input_num = int(parts[2])
                    return OutputRouting(output=output_num, input=input_num)

        raise KVMError("Failed to parse routing output")

    def _parse_stream_output(self, lines: list[str]) -> StreamStatus:
        """Parse EZG OUTx STREAM command output into StreamStatus."""
        for line in lines:
            line = line.strip()
            if "OUT" in line and "STREAM" in line:
                parts = line.split()
                if len(parts) >= 4:
                    output_num = int(parts[1])
                    status = parts[3].lower()
                    enabled = parts[3].upper() == "ON"
                    return StreamStatus(output=output_num, status=status, enabled=enabled)

        raise KVMError("Failed to parse stream output")

    def get_system_status(self) -> SystemStatus:
        """Get system status information.

        Returns:
            SystemStatus with device information

        Raises:
            KVMError: If the command fails or response cannot be parsed
        """
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write("EZSTA")
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_status_output(lines)

    def get_help(self) -> HelpInfo:
        """Get device help information.

        Returns:
            HelpInfo with available commands

        Raises:
            KVMError: If the command fails or response cannot be parsed
        """
        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write("EZH")
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_help_output(lines)

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

        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(f"EZS OUT{output_num} VS IN{input_num}")
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

        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(f"EZG OUT{output_num} VS")
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_routing_output(lines)

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

        with Device(self.device_path, self.baudrate, self.timeout) as device:
            device.write(f"EZG OUT{output_num} STREAM")
            lines = list(device.readlines())

            if not lines:
                raise KVMError("No response from device")

            return self._parse_stream_output(lines)

    def get_input_signal_status(self, input_num: int) -> None:
        """Get input signal status (not supported in F/W 2.03).

        Args:
            input_num: Input number to check (1-4)

        Raises:
            KVMCommandNotSupportedError: This command is not supported
            ValueError: If input number is invalid
        """
        if not 1 <= input_num <= 4:
            raise ValueError("Input number must be between 1 and 4")

        raise KVMCommandNotSupportedError("Input signal status is not supported in firmware 2.03")

    def get_edid_info(self, input_num: Optional[int] = None) -> None:
        """Get EDID information (not supported in F/W 2.03).

        Args:
            input_num: Input number to check (1-4), or None for all

        Raises:
            KVMCommandNotSupportedError: This command is not supported
            ValueError: If input number is invalid
        """
        if input_num is not None and not 1 <= input_num <= 4:
            raise ValueError("Input number must be between 1 and 4")

        raise KVMCommandNotSupportedError("EDID information is not supported in firmware 2.03")
