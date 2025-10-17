# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-17

### Added

- **High-level KVM interface**: New `KVM` class in `kvm.py` providing type-safe, structured interface for library usage
- **Multi-device addressing**: Support for controlling multiple KVM switches on the same serial bus (addresses 0-99)
- **Device discovery**: New `discover` command to find all devices on the serial bus with their firmware versions
- **Comprehensive CLI commands** (replacing simple console.py):
  - `status`: Show system status with firmware version and address
  - `help`: Display device help information
  - `input switch`: Switch inputs with output selection
  - `output routing`: Query current input-to-output routing
  - `output stream`: Check output stream status
  - `edid get/set`: Manage EDID data for inputs
  - `discover`: Find all devices on the serial bus
  - Multiple output formats: `--format raw|json|pretty`
- **Comprehensive test suite**: Full test coverage with pytest
  - Unit tests for `Device`, `KVM`, and CLI commands
  - Integration tests for end-to-end workflows
  - Hardware replay tests using pytest-reserial (no hardware needed for CI)
  - Test coverage reporting with pytest-cov
- **Test scripts** for different testing scenarios:
  - `test-record.sh`: Record serial traffic from real hardware
  - `test-replay.sh`: Run tests using recorded traffic (CI-friendly)
  - `test-with-hardware.sh`: Run tests with actual hardware
- **Enhanced documentation**:
  - Extensive README with installation, usage examples, and library usage guide
  - Development setup instructions with uv
  - Testing documentation
- **Product documentation**: Added official EZCOO KVM switch manual (PDF) in `docs/`
- **CI/CD workflows**: GitHub Actions for automated testing and building on pull requests
  - Composite actions for check and build steps
  - Reusable workflow for check-and-build
  - CI workflow triggered on PRs to main
- **Release documentation**: Complete manual release process guide in `RELEASING.md` including:
  - Version bumping and changelog updates
  - GitHub release creation
  - PyPI publishing
  - AUR package updates

### Changed

- **BREAKING**: License changed from Apache-2.0 to GPL-3.0-or-later
- **BREAKING**: Migrated from Poetry to uv for dependency management
  - Removed `poetry.lock` and `poetry.toml`
  - Added `uv.lock` and updated `pyproject.toml` to use PEP 621 format
  - Changed build backend from poetry-core to hatchling
- **BREAKING**: Migrated from flake8 to ruff for linting and formatting
  - Removed flake8, flake8-black, flake8-import-order
  - Added ruff with comprehensive rule configuration
  - Removed `.flake8` configuration file
- **BREAKING**: Complete CLI rewrite (`cli.py` replaces `console.py`)
  - New command structure with subcommands and groups
  - Added `--address` option for multi-device support
  - Added `--format` option for output formatting (raw/json/pretty)
  - Default output format changed from raw device response to human-readable pretty format
  - Removed direct device command exposure
  - All commands now use high-level KVM interface
- **BREAKING**: Enhanced `Device` class with improved error handling
  - Added `DeviceError` and `DeviceConnectionError` exceptions
  - Added command validation to prevent injection attacks
  - Better error messages for connection and communication failures
  - Configurable baudrate and timeout parameters
  - Type hints updated to use modern Python 3.10+ syntax (`Self`, `type[]`)
- **BREAKING**: Response parsing now returns structured `KVMResponse[T]` objects
  - Generic type parameter ensures type safety
  - Includes raw command, raw response lines, and parsed response
  - Enables both programmatic access and raw output
- **Type safety improvements**:
  - Added `StreamState` enum for on/off states
  - Generic `KVMResponse[T]` wrapper for all responses
  - Proper type hints throughout codebase
  - Dataclasses for all structured data
- **Dependencies**:
  - Removed: `attrs`, `mypy`, `flake8` family
  - Added: `pytest`, `pytest-cov`, `pytest-reserial`, `ruff`
  - Updated: `click` to 8.1.3+, `pyserial` to 3.5+
  - Minimum Python version: 3.10

### Removed

- **console.py**: Replaced by comprehensive `cli.py` with structured commands
- **Poetry configuration**: Migrated to uv
- **flake8 configuration**: Migrated to ruff
- **attrs dependency**: Replaced with standard library dataclasses

### Fixed

- Improved error handling in device communication with specific exception types
- Better validation of command responses with structured parsing
- More reliable serial port handling with proper connection error handling
- Command injection prevention through input validation

### Development

- Added `.vscode/settings.json` with Python and testing configurations
- Updated `.gitignore` with uv-specific patterns and test artifacts
- Enhanced `pyproject.toml` with:
  - Ruff configuration (line length, linting rules)
  - Pytest configuration (test paths, coverage options)
  - Coverage configuration (source paths, exclusions)
  - Dependency groups for dev dependencies

## [0.1.1] - 2024-XX-XX

### Changed

- Bump dependencies

## [0.1.0] - 2024-XX-XX

### Fixed

- Fix wrong baudrate

### Changed

- Move things around and refactoring

## [0.0.1] - 2024-XX-XX

### Added

- Initial PoC implementation

[0.2.0]: https://github.com/Luminger/ezcoo-cli/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/Luminger/ezcoo-cli/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/Luminger/ezcoo-cli/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/Luminger/ezcoo-cli/releases/tag/0.0.1