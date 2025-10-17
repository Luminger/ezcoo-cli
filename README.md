# ezcoo-cli

A tool to control EZCOO KVM switches via the serial interface.

**Tested Devices:** EZCOO EZ-SW41HA-KVMU3L with firmware version 2.03 (should be equal to EZ-SW41HA-KVMU3P)

## Installation

### From PyPI

Install using uv:

```bash
uv add ezcoo-cli
```

### From AUR (Arch Linux)

Install from the Arch User Repository:

```bash
yay -S ezcoo-cli
# or
paru -S ezcoo-cli
```

AUR package: https://aur.archlinux.org/packages/ezcoo-cli

### From Source

```bash
git clone https://github.com/Luminger/ezcoo-cli
cd ezcoo-cli
uv sync
```

## CLI Usage

The CLI provides commands to control your EZCOO KVM switch through a serial connection.

### KVM Switching

**Switch between inputs:**
```bash
# Switch to input 2
ezcoo-cli input switch 2

# Switch to input 3 (output 1 is implicit)
ezcoo-cli input switch 3 --output 1
```

**Check current status:**
```bash
# View system information
ezcoo-cli status

# Check which input is currently active
ezcoo-cli output routing

# Check stream status
ezcoo-cli output stream
```

**Get device information:**
```bash
# View available commands
ezcoo-cli help

# Get raw device response (useful for debugging)
ezcoo-cli help --format raw
ezcoo-cli status --format raw
```

### Output Formats

Most query commands support multiple output formats to suit different use cases. You can specify the format using the `--format` (or `-f`) flag:

- **`pretty`** - Human-readable formatted output (default)
- **`json`** - Machine-readable JSON output for scripting and automation
- **`raw`** - Raw device response as received from the KVM

For example, to get system status as JSON:
```bash
ezcoo-cli status --format json
# or using the short form
ezcoo-cli status -f json
```

> [!NOTE]
> **Breaking Change in v0.2.0:** Version 0.1.0 always printed raw output. Starting from v0.2.0, commands default to pretty-formatted output. Use `--format raw` to get the previous behavior.

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

### Multi-Device Setup

EZCOO devices support address-based multi-device setups where multiple KVM switches can share a single serial connection. Each device needs a unique address (0-99), with 0 being the default for single-device setups.

**Discovering devices on the serial port:**
```bash
# Scan all addresses (0-99)
ezcoo-cli system discover

# Scan specific range
ezcoo-cli system discover --start 0 --end 10
```

**Changing device addresses:**
```bash
# Change device at address 0 to address 5
ezcoo-cli system set-address 5

# Change device at address 5 to address 10
ezcoo-cli --address 5 system set-address 10
```

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

### Running Tests

**Replay Mode (no hardware needed):**
```bash
./scripts/test-replay.sh
# or: uv run pytest tests/ --replay -v
```

**Hardware Mode (with real device):**
```bash
./scripts/test-with-hardware.sh
# or: uv run pytest tests/ -v
```

**Record Mode (capture new traffic):**
```bash
./scripts/test-record.sh
# or: uv run pytest tests/ --record -v
```

### Recorded Traffic

pytest-reserial automatically records serial traffic in the `tests/` directory, with one recording file per test module.

**Important:** Commit these recording files to version control so others can run tests without hardware.

### Prerequisites for Recording

- EZCOO device connected to `/dev/ttyUSB0`
- User has permissions to access serial device:
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in for changes to take effect
  ```

### Command Support Status

Based on testing with EZCOO EZ-SW41HA-KVMU3L devices running firmware 2.03:

#### Working GET Commands

| Command | Description | Response |
|---------|-------------|----------|
| `EZSTA` | Get system status | System info with address, firmware, serial config |
| `EZH` | Get help | Complete command list |
| `EZG OUTx VS` | Get output routing | Current input routing |
| `EZG OUT1 STREAM` | Get stream status | Stream on/off status |

#### Working SET Commands

| Command | Description | Response | CLI Command |
|---------|-------------|----------|-------------|
| `EZS OUTx VS INy` | Switch input | No response (SET command) | `ezcoo-cli input switch <input_num>` |
| `EZS ADDR xx` | Set system address | No response (SET command) | `ezcoo-cli system set-address <new_address>` |

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

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

See the [LICENSE](LICENSE) file for details.
