"""Data models for EZCOO KVM switch responses."""

from dataclasses import dataclass


@dataclass
class DeviceResponse:
    """Base class for all device responses.

    Contains the raw command and response for fallback display.
    """

    command: str
    raw_response: list[str]


@dataclass
class SystemStatus(DeviceResponse):
    """System status information."""

    system_address: int
    firmware_version: str


@dataclass
class Command:
    """Device command information."""

    command: str
    description: str


@dataclass
class HelpInfo(DeviceResponse):
    """Device help information."""

    firmware_version: str | None
    commands: list[Command]
    total_commands: int


@dataclass
class OutputRouting(DeviceResponse):
    """Output routing information."""

    output: int
    input: int


@dataclass
class StreamStatus(DeviceResponse):
    """Output stream status."""

    output: int
    status: str
    enabled: bool


@dataclass
class DiscoveredDevice:
    """Information about a discovered device."""

    address: int
    firmware: str
    system_address: int
