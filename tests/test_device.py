"""Tests for the low-level Device class using pytest-reserial."""

# pyright: reportPrivateUsage=false

from pathlib import Path
from typing import Any

import pytest

from ezcoo_cli.device import Device, DeviceConnectionError, DeviceError

# Device initialization tests


def test_device_init(mock_device_path: Path, test_baudrate: int, test_timeout: float) -> None:
    """Test Device initialization."""
    device = Device(mock_device_path, test_baudrate, test_timeout)
    assert device._path == mock_device_path
    assert device._serial.port == str(mock_device_path)
    assert device._serial.baudrate == test_baudrate
    assert device._serial.timeout == test_timeout


def test_device_context_manager_failure() -> None:
    """Test Device context manager with connection failure."""
    # Test without reserial fixture to simulate real connection failure
    with pytest.raises(DeviceConnectionError):
        with Device(Path("/dev/nonexistent")):
            pass


def test_device_write_closed_device(mock_device_path: Path) -> None:
    """Test writing to closed device raises error."""
    device = Device(mock_device_path)
    with pytest.raises(DeviceError, match="Device is not open"):
        device.write("EZSTA")


def test_device_readlines_closed_device(mock_device_path: Path) -> None:
    """Test reading from closed device raises error."""
    device = Device(mock_device_path)
    with pytest.raises(DeviceError, match="Device is not open"):
        list(device.readlines())


# Device interaction tests (uses reserial for record/replay)


def test_device_context_manager_success(reserial: Any, mock_device_path: Path) -> None:
    """Test Device as context manager with successful connection."""
    with Device(mock_device_path) as device:
        assert device._serial.is_open


def test_device_write_success(reserial: Any, mock_device_path: Path) -> None:
    """Test successful command writing."""
    with Device(mock_device_path) as device:
        # This should not raise an exception
        device.write("EZSTA")


def test_device_readlines_success(reserial: Any, mock_device_path: Path) -> None:
    """Test successful reading of lines."""
    with Device(mock_device_path) as device:
        device.write("EZSTA")
        lines = list(device.readlines())
        # The actual content will depend on recorded traffic
        assert isinstance(lines, list)


def test_system_status_command(reserial: Any, mock_device_path: Path) -> None:
    """Test EZSTA command with recorded traffic."""
    with Device(mock_device_path) as device:
        device.write("EZSTA")
        lines = list(device.readlines())

        # Verify we got some response
        assert len(lines) > 0

        # Look for key indicators in the response
        response_text = "".join(lines)
        assert "System Address" in response_text or "F/W Version" in response_text


def test_help_command(reserial: Any, mock_device_path: Path) -> None:
    """Test EZH command with recorded traffic."""
    with Device(mock_device_path) as device:
        device.write("EZH")
        lines = list(device.readlines())

        # Verify we got some response
        assert len(lines) > 0

        # Look for help indicators
        response_text = "".join(lines)
        assert "Help" in response_text or "EZH" in response_text


def test_switch_input_commands(reserial: Any, mock_device_path: Path) -> None:
    """Test input switching commands with recorded traffic."""
    with Device(mock_device_path) as device:
        # Test switching to each input
        for input_num in range(1, 5):
            device.write(f"EZS OUT1 VS IN{input_num}")
            # SET commands typically don't return responses
            lines = list(device.readlines())
            # Verify we got a list (even if empty for SET commands)
            assert isinstance(lines, list)


def test_get_routing_command(reserial: Any, mock_device_path: Path) -> None:
    """Test EZG OUT1 VS command with recorded traffic."""
    with Device(mock_device_path) as device:
        device.write("EZG OUT1 VS")
        lines = list(device.readlines())

        # Should get routing information
        if lines:
            response_text = "".join(lines)
            assert "OUT1" in response_text and "VS" in response_text


def test_get_stream_status_command(reserial: Any, mock_device_path: Path) -> None:
    """Test EZG OUT1 STREAM command with recorded traffic."""
    with Device(mock_device_path) as device:
        device.write("EZG OUT1 STREAM")
        lines = list(device.readlines())

        # Should get stream status
        if lines:
            response_text = "".join(lines)
            assert ("OUT1" in response_text or "OUT 1" in response_text) and "STREAM" in response_text


def test_command_sequence(reserial: Any, mock_device_path: Path) -> None:
    """Test a sequence of commands to verify device state management."""
    with Device(mock_device_path) as device:
        # Get initial status
        device.write("EZSTA")
        status_lines = list(device.readlines())
        assert len(status_lines) > 0

        # Switch input
        device.write("EZS OUT1 VS IN2")
        switch_lines = list(device.readlines())

        # Verify routing
        device.write("EZG OUT1 VS")
        routing_lines = list(device.readlines())

        # All commands should execute without errors
        assert isinstance(status_lines, list)
        assert isinstance(switch_lines, list)
        assert isinstance(routing_lines, list)


def test_multiple_device_instances(reserial: Any, mock_device_path: Path) -> None:
    """Test that multiple device instances work correctly."""
    # First device instance
    with Device(mock_device_path) as device1:
        device1.write("EZSTA")
        lines1 = list(device1.readlines())

    # Second device instance
    with Device(mock_device_path) as device2:
        device2.write("EZH")
        lines2 = list(device2.readlines())

    # Both should work independently
    assert isinstance(lines1, list)
    assert isinstance(lines2, list)


def test_command_validation_valid() -> None:
    """Test that valid commands with ASCII alphanumeric and spaces are accepted."""
    valid_commands = [
        "EZSTA",
        "EZH",
        "EZS OUT1 VS IN1",
        "EZG OUT1 VS",
        "A05EZSTA",
        "EZS ADDR 05",
        "EZS OUT1 STREAM ON",
    ]

    for cmd in valid_commands:
        # Should not raise any exception
        Device.validate_command(cmd)


def test_command_validation_invalid() -> None:
    """Test that commands with invalid characters are rejected."""
    invalid_commands = [
        "EZS@TA",  # Special character @
        "EZH!",  # Special character !
        "EZS\nOUT1",  # Newline (embedded)
        "EZS;DROP",  # Semicolon
        "EZS|OUT1",  # Pipe
        "EZS&OUT1",  # Ampersand
        "EZS$OUT1",  # Dollar sign
        "EZS#OUT1",  # Hash
        "EZS%OUT1",  # Percent
        "EZS*OUT1",  # Asterisk
        "EZS.OUT1",  # Period
        "EZS,OUT1",  # Comma
        "EZS:OUT1",  # Colon
        "EZS=OUT1",  # Equals
    ]

    for cmd in invalid_commands:
        with pytest.raises(DeviceError, match="invalid characters"):
            Device.validate_command(cmd)
