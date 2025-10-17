"""Data models for EZCOO KVM switch responses."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SerialConfig:
    """Serial port configuration."""

    baud_rate: int
    data_bits: int
    parity: str
    stop_bits: int


@dataclass
class SystemStatus:
    """System status information."""

    system_address: str
    firmware_version: str
    serial_config: SerialConfig


@dataclass
class Command:
    """Device command information."""

    command: str
    description: str


@dataclass
class HelpInfo:
    """Device help information."""

    firmware_version: Optional[str]
    commands: List[Command]
    total_commands: int


@dataclass
class OutputRouting:
    """Output routing information."""

    output: int
    input: int


@dataclass
class StreamStatus:
    """Output stream status."""

    output: int
    status: str
    enabled: bool
