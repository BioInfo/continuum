#!/bin/bash
# Run Continuum MCP server with SSE transport
# Used by LaunchAgent for persistent service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
exec "$PROJECT_DIR/.venv/bin/python" -c "
from continuum.mcp_server import run_sse
run_sse(host='0.0.0.0', port=8765)
"
