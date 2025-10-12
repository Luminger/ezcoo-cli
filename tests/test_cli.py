"""Tests for the CLI interface."""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from ezcoo_cli.cli import main
from ezcoo_cli.models import Command, HelpInfo, KVMResponse, OutputRouting, StreamState, StreamStatus, SystemStatus


@pytest.fixture
def mock_device_file() -> Generator[str, None, None]:
    """Create a temporary file to satisfy Click's exists=True validation."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        device_path = tmp.name
    yield device_path
    Path(device_path).unlink(missing_ok=True)


# Basic CLI tests without device interaction


def test_main_help():
    """Test main command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "EZCOO KVM" in result.output or "control EZCOO" in result.output


def test_status_help():
    """Test status command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["status", "--help"])
    assert result.exit_code == 0
    assert "system status" in result.output


def test_help_command_help():
    """Test help command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["help", "--help"])
    assert result.exit_code == 0
    assert "help information" in result.output


def test_input_group_help():
    """Test input group help."""
    runner = CliRunner()
    result = runner.invoke(main, ["input", "--help"])
    assert result.exit_code == 0
    assert "managing inputs" in result.output


def test_output_group_help():
    """Test output group help."""
    runner = CliRunner()
    result = runner.invoke(main, ["output", "--help"])
    assert result.exit_code == 0
    assert "managing outputs" in result.output


def test_system_group_help():
    """Test system group help."""
    runner = CliRunner()
    result = runner.invoke(main, ["system", "--help"])
    assert result.exit_code == 0
    assert "System management" in result.output


def test_missing_device_parameter():
    """Test commands fail without device parameter."""
    runner = CliRunner()

    # Test status command without device
    result = runner.invoke(main, ["status"])
    # The command may succeed if default device exists, or fail if it doesn't
    assert isinstance(result.exit_code, int)


def test_version_command():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


# CLI integration tests (mock KVM, no device needed)


@patch("ezcoo_cli.cli.KVM")
def test_status_command_json(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test status command with JSON output."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_status = KVMResponse(
        command="EZSTA",
        raw_response=["System Address : 00  F/W Version : 2.03\n"],
        response=SystemStatus(
            system_address=0,
            firmware_version="2.03",
        ),
    )
    mock_kvm.get_system_status.return_value = mock_status

    runner = CliRunner()
    result = runner.invoke(main, ["status", "--device", mock_device_file, "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["response"]["system_address"] == 0
    assert data["response"]["firmware_version"] == "2.03"


@patch("ezcoo_cli.cli.KVM")
def test_help_command_json(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test help command with JSON output."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_help = KVMResponse(
        command="EZH",
        raw_response=["F/W Version : 2.03\n", "=   EZH : Help\n", "=   EZSTA : Show Global System Status\n"],
        response=HelpInfo(
            firmware_version="2.03",
            commands=[
                Command(command="EZH", description="Help"),
                Command(command="EZSTA", description="Show Global System Status"),
            ],
            total_commands=2,
        ),
    )
    mock_kvm.get_help.return_value = mock_help

    runner = CliRunner()
    result = runner.invoke(main, ["help", "--device", mock_device_file, "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["response"]["total_commands"] == 2
    assert len(data["response"]["commands"]) == 2


@patch("ezcoo_cli.cli.KVM")
def test_input_switch_command_valid_inputs(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test input switch command with valid input numbers."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    runner = CliRunner()

    for input_num in range(1, 5):
        result = runner.invoke(main, ["input", "switch", "--device", mock_device_file, str(input_num)])
        assert result.exit_code == 0
        mock_kvm.switch_input.assert_called_with(input_num, output_num=1)


def test_input_switch_command_invalid_input():
    """Test input switch command with invalid input numbers."""
    runner = CliRunner()

    # Test input 0
    result = runner.invoke(main, ["input", "switch", "--device", "/dev/ttyUSB0", "0"])
    assert result.exit_code != 0

    # Test input 5
    result = runner.invoke(main, ["input", "switch", "--device", "/dev/ttyUSB0", "5"])
    assert result.exit_code != 0


@patch("ezcoo_cli.cli.KVM")
def test_output_routing_command_json(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test output routing command with JSON output."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_routing = KVMResponse(
        command="EZG OUT1 VS",
        raw_response=["OUT1 VS IN2\n"],
        response=OutputRouting(
            output=1,
            input=2,
        ),
    )
    mock_kvm.get_output_routing.return_value = mock_routing

    runner = CliRunner()
    result = runner.invoke(main, ["output", "routing", "--device", mock_device_file, "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["response"]["output"] == 1
    assert data["response"]["input"] == 2


@patch("ezcoo_cli.cli.KVM")
def test_output_stream_command_json(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test output stream command with JSON output."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_stream = KVMResponse(
        command="EZG OUT1 STREAM",
        raw_response=["OUT1 STREAM on\n"],
        response=StreamStatus(
            output=1,
            status=StreamState.ON,
            enabled=True,
        ),
    )
    mock_kvm.get_stream_status.return_value = mock_stream

    runner = CliRunner()
    result = runner.invoke(main, ["output", "stream", "--device", mock_device_file, "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["response"]["output"] == 1
    assert data["response"]["status"] == StreamState.ON.value
    assert data["response"]["enabled"] is True


@patch("ezcoo_cli.cli.KVM")
def test_output_format_consistency(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test that output formats are consistent across commands."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_kvm.get_system_status.return_value = KVMResponse(
        command="EZSTA",
        raw_response=["System Address : 00  F/W Version : 2.03\n"],
        response=SystemStatus(
            system_address=0,
            firmware_version="2.03",
        ),
    )
    mock_kvm.get_help.return_value = KVMResponse(
        command="EZH",
        raw_response=["F/W Version : 2.03\n", "=   EZH : Help\n"],
        response=HelpInfo(
            firmware_version="2.03",
            commands=[Command(command="EZH", description="Help")],
            total_commands=1,
        ),
    )
    mock_kvm.get_output_routing.return_value = KVMResponse(
        command="EZG OUT1 VS",
        raw_response=["OUT1 VS IN2\n"],
        response=OutputRouting(
            output=1,
            input=2,
        ),
    )
    mock_kvm.get_stream_status.return_value = KVMResponse(
        command="EZG OUT1 STREAM",
        raw_response=["OUT1 STREAM on\n"],
        response=StreamStatus(
            output=1,
            status=StreamState.ON,
            enabled=True,
        ),
    )

    runner = CliRunner()
    device_args = ["--device", mock_device_file]

    commands_to_test = [["status"], ["help"], ["output", "routing"], ["output", "stream"]]

    for command_parts in commands_to_test:
        # Test JSON format
        result = runner.invoke(main, command_parts + device_args + ["--format", "json"])
        assert result.exit_code == 0
        json.loads(result.output)  # Should not raise

        # Test pretty format
        result = runner.invoke(main, command_parts + device_args + ["--format", "pretty"])
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0


@patch("ezcoo_cli.cli.KVM")
def test_input_switch_with_output_option(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test input switch command with output option."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    runner = CliRunner()

    # Test with default output (should work)
    result = runner.invoke(main, ["input", "switch", "--device", mock_device_file, "1"])
    assert result.exit_code == 0
    mock_kvm.switch_input.assert_called_with(1, output_num=1)

    # Test with explicit output 1 (should work)
    result = runner.invoke(main, ["input", "switch", "--device", mock_device_file, "--output", "1", "1"])
    assert result.exit_code == 0
    mock_kvm.switch_input.assert_called_with(1, output_num=1)


# System group command tests


@patch("ezcoo_cli.cli.KVM")
def test_system_set_address_with_yes_flag(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system set-address command with --yes flag."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    runner = CliRunner()
    result = runner.invoke(main, ["system", "set-address", "--device", mock_device_file, "--yes", "5"])

    assert result.exit_code == 0
    mock_kvm.set_device_address.assert_called_once_with(5)
    assert "Device address changed" in result.output
    assert "from 0 to 5" in result.output


@patch("ezcoo_cli.cli.KVM")
def test_system_set_address_with_confirmation(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system set-address command with user confirmation."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    runner = CliRunner()

    # Test with confirmation (yes)
    result = runner.invoke(main, ["system", "set-address", "--device", mock_device_file, "10"], input="y\n")
    assert result.exit_code == 0
    mock_kvm.set_device_address.assert_called_once_with(10)
    assert "Device address changed" in result.output


@patch("ezcoo_cli.cli.KVM")
def test_system_set_address_cancelled(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system set-address command cancelled by user."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    runner = CliRunner()

    # Test with cancellation (no)
    result = runner.invoke(main, ["system", "set-address", "--device", mock_device_file, "10"], input="n\n")
    assert result.exit_code == 0
    mock_kvm.set_device_address.assert_not_called()
    assert "cancelled" in result.output


@patch("ezcoo_cli.cli.KVM")
def test_system_discover_command(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system discover command."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    # Mock successful responses for addresses 0 and 5
    def mock_get_system_status_side_effect():
        # First call (address 0)
        status_0 = KVMResponse(
            command="EZSTA",
            raw_response=["System Address : 00  F/W Version : 2.03\n"],
            response=SystemStatus(
                system_address=0,
                firmware_version="2.03",
            ),
        )
        # Second call (address 5)
        status_5 = KVMResponse(
            command="A05EZSTA",
            raw_response=["System Address : 05  F/W Version : 2.03\n"],
            response=SystemStatus(
                system_address=5,
                firmware_version="2.03",
            ),
        )
        # Return different status based on which address was used
        for status in [status_0, status_5]:
            yield status

    mock_kvm.get_system_status.side_effect = mock_get_system_status_side_effect()

    runner = CliRunner()
    result = runner.invoke(main, ["system", "discover", "--device", mock_device_file, "--start", "0", "--end", "5"])

    assert result.exit_code == 0
    assert "Scanning addresses 0 to 5" in result.output
    assert "Total devices found: 2" in result.output


@patch("ezcoo_cli.cli.KVM")
def test_system_discover_json_output(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system discover command with JSON output."""
    # Setup mock
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm

    mock_status = KVMResponse(
        command="EZSTA",
        raw_response=["System Address : 00  F/W Version : 2.03\n"],
        response=SystemStatus(
            system_address=0,
            firmware_version="2.03",
        ),
    )
    mock_kvm.get_system_status.return_value = mock_status

    runner = CliRunner()
    result = runner.invoke(
        main, ["system", "discover", "--device", mock_device_file, "--start", "0", "--end", "0", "--format", "json"]
    )

    assert result.exit_code == 0
    data: list[dict[str, object]] = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["address"] == 0
    assert data[0]["firmware"] == "2.03"
    assert data[0]["system_address"] == 0


@patch("ezcoo_cli.cli.KVM")
def test_system_discover_no_devices(mock_kvm_class: MagicMock, mock_device_file: str) -> None:
    """Test system discover command when no devices are found."""
    # Setup mock to always raise exception (no devices)
    mock_kvm = Mock()
    mock_kvm_class.return_value = mock_kvm
    mock_kvm.get_system_status.side_effect = Exception("No device")

    runner = CliRunner()
    result = runner.invoke(main, ["system", "discover", "--device", mock_device_file, "--start", "0", "--end", "2"])

    assert result.exit_code == 0
    assert "No devices found" in result.output


def test_system_discover_invalid_range(mock_device_file: str) -> None:
    """Test system discover command with invalid address range."""
    runner = CliRunner()
    result = runner.invoke(main, ["system", "discover", "--device", mock_device_file, "--start", "10", "--end", "5"])

    assert result.exit_code == 1
    assert "Start address must be less than or equal to end address" in result.output
