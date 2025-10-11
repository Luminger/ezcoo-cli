"""Shared pytest fixtures and configuration for EZCOO CLI tests."""

from pathlib import Path

import pytest


@pytest.fixture
def mock_device_path() -> Path:
    """Mock device path for testing."""
    return Path("/dev/ttyUSB0")


@pytest.fixture
def test_baudrate() -> int:
    """Standard baudrate for testing."""
    return 115200


@pytest.fixture
def test_timeout() -> float:
    """Standard timeout for testing."""
    return 1.0
