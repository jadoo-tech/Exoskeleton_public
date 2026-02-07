#!/usr/bin/env bash
set -euo pipefail

uv sync --group test
uv run pytest integration/macos/tests -q
