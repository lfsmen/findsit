#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install Python dependencies when a requirements.txt exists
if [ -f "${CLAUDE_PROJECT_DIR}/requirements.txt" ]; then
  echo "Installing Python dependencies..."
  pip install -r "${CLAUDE_PROJECT_DIR}/requirements.txt"
fi

echo "Session start hook complete."
