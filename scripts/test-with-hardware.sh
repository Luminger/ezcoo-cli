#!/usr/bin/env bash
# Test with real hardware connected
# This runs tests against the actual EZCOO device without recording or replaying

set -e

DEVICE="/dev/ttyUSB0"

# Check if device exists
if [ ! -e "$DEVICE" ]; then
    echo "ERROR: Device $DEVICE does not exist"
    exit 1
fi

# Check if device is readable and writable
if [ ! -r "$DEVICE" ] || [ ! -w "$DEVICE" ]; then
    echo "ERROR: Device $DEVICE is not readable and writable by current user"
    echo "Try: sudo chmod 666 $DEVICE"
    exit 1
fi

uv run pytest tests/ -v "$@"