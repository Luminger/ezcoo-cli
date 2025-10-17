# ezcoo-cli

A tool to control EZCOO KVM switches via the serial interface.

**Tested Devices:** EZCOO EZ-SW41HA-KVMU3L and EZ-SW41HA-KVMU3P with firmware version 2.03

## Installation

Install using uv:

```bash
uv add ezcoo-cli
```

Or install from source:

```bash
git clone <repository-url>
cd ezcoo-cli
uv sync
```

## CLI Usage

The CLI provides commands to control your EZCOO KVM switch through a serial connection.

### Basic Commands

```bash
# Show version
ezcoo-cli version

# Switch input 2 to output 1 (default output)
ezcoo-cli input switch 2

# Switch input 3 to output 2
ezcoo-cli input switch 3 --output 2

# Get EDID information
ezcoo-cli input edid

# Get device help
ezcoo-cli help
```

### Device Connection

By default, the tool connects to `/dev/ttyUSB0`. You can specify a different device:

```bash
ezcoo-cli -d /dev/ttyUSB1 input switch 2
```

## Library Usage

You can use ezcoo-cli as a library in your Python projects. There are two interfaces available:

### High-Level KVM Interface (Recommended)

The high-level interface provides type-safe, structured access to KVM functionality:

```python
from pathlib import Path
from ezcoo_cli.kvm import KVM

# Create KVM instance
kvm = KVM(Path("/dev/ttyUSB0"))

# Get system information
status = kvm.get_system_status()
print(f"Firmware: {status.firmware_version}")
print(f"Address: {status.system_address}")

# Switch inputs
kvm.switch_input(2)  # Switch to input 2

# Get current routing
routing = kvm.get_output_routing()
print(f"Output {routing.output} -> Input {routing.input}")

# Get stream status
stream = kvm.get_stream_status()
print(f"Stream enabled: {stream.enabled}")

# Get help information
help_info = kvm.get_help()
print(f"Available commands: {help_info.total_commands}")
```

### Low-Level Device Interface

For direct command access, use the Device class:

```python
from pathlib import Path
from ezcoo_cli.device import Device

# Basic usage
with Device(Path("/dev/ttyUSB0")) as device:
    # Switch input 2 to output 1
    device.write("EZS OUT1 VS IN2")
    
    # Get help
    device.write("EZH")
    for line in device.readlines():
        print(line, end="")
```

### Error Handling

Both interfaces provide specific exceptions for better error handling:

```python
from ezcoo_cli.kvm import KVM, KVMError, KVMCommandNotSupportedError
from ezcoo_cli.device import DeviceError, DeviceConnectionError

try:
    kvm = KVM(Path("/dev/ttyUSB0"))
    kvm.switch_input(2)
except KVMCommandNotSupportedError as e:
    print(f"Command not supported: {e}")
except KVMError as e:
    print(f"KVM operation failed: {e}")
except DeviceConnectionError as e:
    print(f"Failed to connect to device: {e}")
```

### Data Models

The high-level interface returns structured data using dataclasses:

```python
# SystemStatus dataclass
status = kvm.get_system_status()
print(status.system_address)      # "00"
print(status.firmware_version)    # "2.03"
print(status.serial_config.baud_rate)  # 115200

# OutputRouting dataclass
routing = kvm.get_output_routing()
print(routing.output)  # 1
print(routing.input)   # 2

# StreamStatus dataclass
stream = kvm.get_stream_status()
print(stream.output)   # 1
print(stream.status)   # "on"
print(stream.enabled)  # True
```

## Development

This project uses uv for dependency management and ruff for linting.

```bash
# Install development dependencies
uv sync --dev

# Run linting
uv run ruff check

# Run formatting
uv run ruff format
```

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

See the [LICENSE](LICENSE) file for details.
