"""Tests for the high-level KVM class using pytest-reserial."""

# pyright: reportPrivateUsage=false

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ezcoo_cli.kvm import KVM
from ezcoo_cli.models import StreamState

# KVM initialization tests


def test_kvm_init(mock_device_path: Path, test_baudrate: int, test_timeout: float) -> None:
    """Test KVM initialization."""
    kvm = KVM(mock_device_path, test_baudrate, test_timeout)
    assert kvm.device_path == mock_device_path
    assert kvm.baudrate == test_baudrate
    assert kvm.timeout == test_timeout


def test_kvm_init_defaults(mock_device_path: Path) -> None:
    """Test KVM initialization with default parameters."""
    kvm = KVM(mock_device_path)
    assert kvm.device_path == mock_device_path
    assert kvm.baudrate == 115200
    assert kvm.timeout == 1.0


# Validation tests


def test_switch_input_invalid_input(mock_device_path: Path) -> None:
    """Test switch_input with invalid input numbers."""
    kvm = KVM(mock_device_path)

    with pytest.raises(ValueError, match="Input number must be between 1 and 4"):
        kvm.switch_input(0)

    with pytest.raises(ValueError, match="Input number must be between 1 and 4"):
        kvm.switch_input(5)


def test_switch_input_invalid_output(mock_device_path: Path) -> None:
    """Test switch_input with invalid output numbers."""
    kvm = KVM(mock_device_path)

    with pytest.raises(ValueError, match="Only output 1 is supported"):
        kvm.switch_input(1, output_num=2)


def test_get_output_routing_invalid_output(mock_device_path: Path) -> None:
    """Test get_output_routing with invalid output number."""
    kvm = KVM(mock_device_path)

    with pytest.raises(ValueError, match="Only output 1 is supported"):
        kvm.get_output_routing(output_num=2)


def test_get_stream_status_invalid_output(mock_device_path: Path) -> None:
    """Test get_stream_status with invalid output number."""
    kvm = KVM(mock_device_path)

    with pytest.raises(ValueError, match="Only output 1 is supported"):
        kvm.get_stream_status(output_num=2)


# Device interaction tests (uses reserial for record/replay)


def test_get_system_status(reserial: Any, mock_device_path: Path) -> None:
    """Test get_system_status with recorded traffic."""
    kvm = KVM(mock_device_path)
    status_response = kvm.get_system_status()

    assert status_response.response.system_address is not None
    assert status_response.response.firmware_version is not None


def test_get_help(reserial: Any, mock_device_path: Path) -> None:
    """Test get_help with recorded traffic."""
    kvm = KVM(mock_device_path)
    help_response = kvm.get_help()

    assert len(help_response.response.commands) > 0
    assert help_response.response.total_commands > 0


def test_switch_input_valid(reserial: Any, mock_device_path: Path) -> None:
    """Test switch_input with valid inputs."""
    kvm = KVM(mock_device_path)

    # Test switching to each valid input
    for input_num in range(1, 5):
        kvm.switch_input(input_num)  # Should not raise exception


def test_get_output_routing(reserial: Any, mock_device_path: Path) -> None:
    """Test get_output_routing with recorded traffic."""
    kvm = KVM(mock_device_path)
    routing_response = kvm.get_output_routing()

    assert 1 <= routing_response.response.input <= 4
    assert routing_response.response.output == 1


def test_get_stream_status(reserial: Any, mock_device_path: Path) -> None:
    """Test get_stream_status with recorded traffic."""
    kvm = KVM(mock_device_path)
    stream_response = kvm.get_stream_status()

    assert stream_response.response.output == 1
    assert isinstance(stream_response.response.enabled, bool)
    assert stream_response.response.status in [StreamState.ON, StreamState.OFF]


# Address management tests


def test_kvm_init_with_address(mock_device_path: Path) -> None:
    """Test KVM initialization with custom address."""
    kvm = KVM(mock_device_path, address=5)
    assert kvm.address == 5


def test_kvm_init_default_address(mock_device_path: Path) -> None:
    """Test KVM initialization with default address."""
    kvm = KVM(mock_device_path)
    assert kvm.address == 0


def test_kvm_address_validation(mock_device_path: Path) -> None:
    """Test address validation during initialization."""
    # Valid addresses
    for addr in [0, 1, 50, 99]:
        kvm = KVM(mock_device_path, address=addr)
        assert kvm.address == addr

    # Invalid addresses
    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        KVM(mock_device_path, address=-1)

    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        KVM(mock_device_path, address=100)


def test_address_property_setter(mock_device_path: Path) -> None:
    """Test address property setter."""
    kvm = KVM(mock_device_path, address=0)

    # Valid address changes
    kvm.address = 5
    assert kvm.address == 5

    kvm.address = 99
    assert kvm.address == 99

    # Invalid addresses
    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        kvm.address = -1

    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        kvm.address = 100


def test_set_device_address_validation(mock_device_path: Path) -> None:
    """Test set_device_address validation."""
    kvm = KVM(mock_device_path)

    # Invalid addresses
    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        kvm.set_device_address(-1)

    with pytest.raises(ValueError, match="Address must be between 0 and 99"):
        kvm.set_device_address(100)


def test_set_device_address(reserial: Any, mock_device_path: Path) -> None:
    """Test set_device_address with recorded traffic.

    This test changes the device address and must restore it even if the test fails.
    """
    kvm = KVM(mock_device_path)

    # Read the original address from the device
    status_response = kvm.get_system_status()
    original_address = status_response.response.system_address
    new_address = 5

    try:
        # Change address to 5
        kvm.set_device_address(new_address)

        # Note: The address property is NOT automatically updated
        # User must manually update it after changing device address
        assert kvm.address == original_address  # Still at old address
    finally:
        # Always restore the original address, even if test fails
        # Update KVM instance to use new address to send reset command
        kvm.address = new_address
        kvm.set_device_address(original_address)


def test_address_in_commands(mock_device_path: Path) -> None:
    """Test that address prefix is included in commands."""
    # Mock Device to avoid actual serial communication
    with patch("ezcoo_cli.kvm.Device") as mock_device_class:
        mock_device = mock_device_class.return_value.__enter__.return_value

        # Test with address 0 (no prefix)
        kvm = KVM(mock_device_path, address=0)
        kvm.switch_input(2)
        mock_device.write.assert_called_with("EZS OUT1 VS IN2")

        # Reset mock
        mock_device.write.reset_mock()

        # Test with address 5 (A05 prefix)
        kvm = KVM(mock_device_path, address=5)
        kvm.switch_input(2)
        mock_device.write.assert_called_with("A05EZS OUT1 VS IN2")


def test_address_prefix_in_command(mock_device_path: Path) -> None:
    """Test that address prefix is correctly included in commands."""
    # Mock Device to verify command format without actual device communication
    with patch("ezcoo_cli.kvm.Device") as mock_device_class:
        mock_device = mock_device_class.return_value.__enter__.return_value

        # Test with address 5 - should include A05 prefix
        kvm = KVM(mock_device_path, address=5)
        kvm.switch_input(2)
        mock_device.write.assert_called_with("A05EZS OUT1 VS IN2")
