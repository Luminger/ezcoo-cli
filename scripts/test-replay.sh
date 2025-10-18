#!/usr/bin/env bash
# Run tests using recorded serial traffic (no hardware needed)
# This uses the .jsonl files created by test-record.sh

set -e

# Check if any .jsonl files exist
if ! ls tests/*.jsonl 1> /dev/null 2>&1; then
    echo "ERROR: No recorded traffic files found. Run ./scripts/test-record.sh first."
    exit 1
fi

uv run pytest tests/ --replay -v "$@"