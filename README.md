# ezcoo-cli

A tool to control EZCOO KVM switches via the serial interface.

**Tested Devices:** EZCOO EZ-SW41HA-KVMU3L with firmware version 2.03 (should work with EZ-SW41HA-KVMU3P as well)

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

### Output Formats

> [!IMPORTANT]
> Most query commands support multiple output formats using the `--format` (or `-f`) flag.

**Available output formats:**
- `pretty` - Human-readable formatted output (default)
- `json` - Machine-readable JSON output
- `raw` - Raw device response

**Commands that support the format flag:**
- `ezcoo-cli status` - System status information
- `ezcoo-cli help` - Device help information
- `ezcoo-cli output routing` - Output routing information
- `ezcoo-cli output stream` - Stream status information
- `ezcoo-cli system discover` - Device discovery results

### Basic Commands

```bash
# Show version
ezcoo-cli version

# Switch input 2 to output 1 (default output)
ezcoo-cli input switch 2

# Switch input 3 to output 2
ezcoo-cli input switch 3 --output 2

# Get device help (pretty formatted - default)
ezcoo-cli help

# Get device help (raw output)
ezcoo-cli help --format raw

# Get device help (JSON output)
ezcoo-cli help --format json

# Short form using -f
ezcoo-cli help -f json

# Get system status (pretty by default)
ezcoo-cli status

# Get output routing as JSON
ezcoo-cli output routing --format json
```

### Device Connection and Addressing

By default, the tool connects to `/dev/ttyUSB0` at address 0 (single device mode). You can specify a different device and address:

```bash
# Use a different serial device
ezcoo-cli -d /dev/ttyUSB1 input switch 2

# Communicate with device at address 5
ezcoo-cli --address 5 status

# Short form
ezcoo-cli -a 5 status
```

### Address Management

The tool supports managing device addresses for multi-device setups on the same serial port:

```bash
# Discover all devices on the current serial port (scans addresses 0-99)
ezcoo-cli system discover

# Discover devices in a specific address range on the serial port
ezcoo-cli system discover --start 0 --end 10

# Get discovery results as JSON
ezcoo-cli system discover --format json

# Change device address from 0 to 5
ezcoo-cli system set-address 5

# Change address with confirmation skip
ezcoo-cli system set-address 5 --yes

# Change address of device currently at address 5 to address 10
ezcoo-cli --address 5 system set-address 10
```

> [!NOTE]
> Device discovery scans different addresses on the **same serial port**, not different serial devices. Multiple EZCOO devices can share a single serial connection by using different addresses (0-99).

> [!NOTE]
> **Device Chaining:** The EZCOO devices support a "device chaining" feature that allows multiple devices to be connected on the same serial interface. While we have not been able to observe behavioral changes when using this feature, it is assumed to enable serial interface chaining for multi-device setups. Each device in the chain should be configured with a unique address (0-99) for proper communication.

> [!WARNING]
> After changing a device's address, you must use the `--address` option to communicate with it at its new address.

## Library Usage

You can use ezcoo-cli as a library in your Python projects. There are two interfaces available:

### High-Level KVM Interface (Recommended)

The high-level interface provides type-safe, structured access to KVM functionality:

```python
from pathlib import Path
from ezcoo_cli.kvm import KVM

# Create KVM instance (default address 0)
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

# Working with devices at specific addresses
kvm_at_5 = KVM(Path("/dev/ttyUSB0"), address=5)
status = kvm_at_5.get_system_status()

# Change device address
kvm.set_device_address(5)  # Change from 0 to 5
kvm.address = 5  # Update instance to use new address

# Access raw response for any command
print(status.raw_response)  # Raw device output
print(status.command)  # Command that was sent
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
from ezcoo_cli.kvm import KVM, KVMError
from ezcoo_cli.device import DeviceError, DeviceConnectionError

try:
    kvm = KVM(Path("/dev/ttyUSB0"))
    kvm.switch_input(2)
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
print(status.system_address)      # 0
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

## Testing

The test suite uses pytest-reserial to record and replay serial device interactions, allowing tests to run without physical hardware.

### Quick Start

```bash
# Run tests with recorded traffic (no hardware needed)
./scripts/test-replay.sh

# Run tests with real hardware
./scripts/test-with-hardware.sh

# Record new traffic from hardware
./scripts/test-record.sh
```

### Test Modes

**1. Replay Mode (CI/CD, No Hardware)**
```bash
./scripts/test-replay.sh
# or
uv run pytest tests/ --replay -v
```
Uses recorded `.jsonl` files to simulate device responses. Perfect for CI/CD pipelines and development without hardware.

**2. Hardware Mode (Real Device)**
```bash
./scripts/test-with-hardware.sh
# or
uv run pytest tests/ -v
```
Runs tests against actual EZCOO device connected to `/dev/ttyUSB0`. Use this to verify functionality with real hardware.

**3. Record Mode (Capture Traffic)**
```bash
./scripts/test-record.sh
# or
uv run pytest tests/ --record -v
```
Records serial traffic from real hardware to `.jsonl` files. Run this when:
- Adding new tests
- Updating existing tests
- Device firmware changes
- Initial setup

### Test Organization

- `tests/test_device.py` - Low-level Device class tests
- `tests/test_kvm.py` - High-level KVM interface tests
- `tests/test_cli.py` - CLI command tests
- `tests/test_integration.py` - Integration and workflow tests

### Recorded Traffic Files

Serial traffic is automatically recorded to `.jsonl` files in the `tests/` directory, with one file per test module.

**Important:** Commit these `.jsonl` files to version control so other developers can run tests without hardware.

### Prerequisites for Recording

- EZCOO device connected to `/dev/ttyUSB0`
- User has permissions to access serial device:
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in for changes to take effect
  ```

### Command Support Status

Based on testing with EZCOO EZ-SW41HA-KVMU3L devices running firmware 2.03:

#### Working Commands

| Command | Description | Response |
|---------|-------------|----------|
| `EZSTA` | Get system status | System info with address, firmware, serial config |
| `EZH` | Get help | Complete command list |
| `EZS OUTx VS INy` | Switch input | No response (SET command) |
| `EZG OUTx VS` | Get output routing | Current input routing |
| `EZG OUT1 STREAM` | Get stream status | Stream on/off status |

#### Unsupported/Unimplemented Commands

**Query commands that don't return data (Firmware 2.03):**

These commands have been tested and confirmed to return no data on firmware 2.03. They are not exposed by the project as they don't work on this firmware version.

| Command | Description | Test Result |
|---------|-------------|-------------|
| `EZG INx SIG STA` | Get input signal status | No response from device |
| `EZG INx EDID` | Get EDID information | No response from device |
| `EZG ADDR` | Get system address | No response from device |
| `EZG AUTO MODE` | Get auto switch mode status | No response from device |
| `EZG CAS` | Get cascade mode status | No response from device |
| `EZG STA` | Get system status (alternative) | No response from device (use `EZSTA` instead) |

**SET commands with unknown/unclear effect (not implemented in this tool):**

These SET commands have been tested and the device accepts them without errors (no response, which is normal for SET commands). However, their actual effect is unclear - either no observable changes occurred or the expected behavior was not seen.

| Command | Description | Test Result | Reason Not Implemented |
|---------|-------------|-------------|------------------------|
| `EZS CAS EN/DIS` | Set cascade mode enable/disable | Accepted by device, no observable effect | Effect unclear |
| `EZS OUTx VIDEOy` | Set output video mode (BYPASS/4K->2K) | Accepted by device, no observable effect | Effect unclear |
| `EZS INx EDID y` | Set input EDID | Accepted by device, no observable effect | Effect unclear |
| `EZS RST` | Reset to factory defaults | Accepted by device, but address was NOT reset (still at 01 after reset) | Effect unclear - may not work or may only reset some settings |

**Implemented SET commands:**

| Command | Description | Test Result | CLI Command |
|---------|-------------|-------------|-------------|
| `EZS ADDR xx` | Set system address | Works - successfully tested address change with prefix recovery | `ezcoo-cli system set-address <new_address>` |

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

See the [LICENSE](LICENSE) file for details.
