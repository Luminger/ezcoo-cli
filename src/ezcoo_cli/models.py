"""Data models for EZCOO KVM switch responses."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class StreamState(str, Enum):
    """Stream status state."""

    ON = "on"
    OFF = "off"


@dataclass
class KVMResponse(Generic[T]):
    """Generic response wrapper for KVM commands.

    Contains the raw command, response lines, and parsed response.
    """

    command: str
    raw_response: list[str]
    response: T


@dataclass
class SystemStatus:
    """System status information."""

    system_address: int
    firmware_version: str


@dataclass
class Command:
    """Device command information."""

    command: str
    description: str


@dataclass
class HelpInfo:
    """Device help information."""

    firmware_version: str | None
    commands: list[Command]
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
    status: StreamState
    enabled: bool


@dataclass
class DiscoveredDevice:
    """Information about a discovered device."""

    address: int
    firmware: str
    system_address: int
