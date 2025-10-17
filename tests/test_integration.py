"""Integration tests demonstrating pytest-reserial recording and replay."""

from pathlib import Path
from typing import Any

import pytest

from ezcoo_cli.device import Device, DeviceConnectionError
from ezcoo_cli.kvm import KVM
from ezcoo_cli.models import StreamState

# Integration tests (uses reserial for record/replay)


def test_system_status(reserial: Any, mock_device_path: Path) -> None:
    """Test EZSTA command."""
    with Device(mock_device_path) as device:
        device.write("EZSTA")
        lines = list(device.readlines())

        # Verify we got a response
        assert len(lines) > 0

        # Look for expected content
        response_text = "".join(lines)
        assert any(keyword in response_text for keyword in ["System Address", "F/W Version", "RS232"])


def test_help_command(reserial: Any, mock_device_path: Path) -> None:
    """Test EZH command."""
    with Device(mock_device_path) as device:
        device.write("EZH")
        lines = list(device.readlines())

        # Verify we got a response
        assert len(lines) > 0

        # Look for help content
        response_text = "".join(lines)
        assert any(keyword in response_text for keyword in ["Help", "EZH", "EZSTA", "Commands"])


def test_input_switching(reserial: Any, mock_device_path: Path) -> None:
    """Test input switching commands."""
    with Device(mock_device_path) as device:
        for input_num in range(1, 5):
            device.write(f"EZS OUT1 VS IN{input_num}")
            list(device.readlines())


def test_routing_query(reserial: Any, mock_device_path: Path) -> None:
    """Test routing query command."""
    with Device(mock_device_path) as device:
        device.write("EZG OUT1 VS")
        lines = list(device.readlines())

        # Should get routing information
        if lines:
            response_text = "".join(lines)
            assert "OUT1" in response_text


def test_stream_status(reserial: Any, mock_device_path: Path) -> None:
    """Test stream status command."""
    with Device(mock_device_path) as device:
        device.write("EZG OUT1 STREAM")
        lines = list(device.readlines())

        # Should get stream status
        if lines:
            response_text = "".join(lines)
            assert "OUT1" in response_text or "OUT 1" in response_text


# KVM integration tests


def test_kvm_system_status(reserial: Any, mock_device_path: Path) -> None:
    """Test KVM system status."""
    kvm = KVM(mock_device_path)
    status_response = kvm.get_system_status()

    # Verify the parsed response
    assert status_response.response.system_address is not None
    assert status_response.response.firmware_version is not None


def test_kvm_help(reserial: Any, mock_device_path: Path) -> None:
    """Test KVM help."""
    kvm = KVM(mock_device_path)
    help_response = kvm.get_help()

    # Verify the parsed response
    assert help_response.response.total_commands > 0
    assert len(help_response.response.commands) > 0

    # Check for expected commands
    command_names = [cmd.command for cmd in help_response.response.commands]
    expected_commands = ["EZH", "EZSTA", "EZS OUTx VS INy"]
    for expected in expected_commands:
        assert any(expected in cmd for cmd in command_names)


def test_kvm_switching(reserial: Any, mock_device_path: Path) -> None:
    """Test KVM input switching."""
    kvm = KVM(mock_device_path)

    # Test switching to each input
    for input_num in range(1, 5):
        kvm.switch_input(input_num)  # Should not raise exception


def test_kvm_routing(reserial: Any, mock_device_path: Path) -> None:
    """Test KVM routing query."""
    kvm = KVM(mock_device_path)
    routing_response = kvm.get_output_routing()

    # Verify the parsed response
    assert 1 <= routing_response.response.input <= 4
    assert routing_response.response.output == 1


def test_kvm_stream(reserial: Any, mock_device_path: Path) -> None:
    """Test KVM stream status."""
    kvm = KVM(mock_device_path)
    stream_response = kvm.get_stream_status()

    # Verify the parsed response
    assert stream_response.response.output == 1
    assert isinstance(stream_response.response.enabled, bool)
    assert stream_response.response.status in [StreamState.ON, StreamState.OFF]


# Error scenario tests


def test_device_connection_error() -> None:
    """Test device connection error."""
    with pytest.raises(DeviceConnectionError):
        with Device(Path("/dev/nonexistent")):
            pass


def test_kvm_error_handling(mock_device_path: Path) -> None:
    """Test KVM error handling."""
    kvm = KVM(mock_device_path)

    # Test invalid input numbers
    with pytest.raises(ValueError):
        kvm.switch_input(0)

    with pytest.raises(ValueError):
        kvm.switch_input(5)

    # Test invalid output numbers
    with pytest.raises(ValueError):
        kvm.get_output_routing(2)

    with pytest.raises(ValueError):
        kvm.get_stream_status(2)
