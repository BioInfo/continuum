#!/bin/bash
# Run Continuum MCP server with SSE transport
# Used by LaunchAgent for persistent service

cd /Users/bioinfo/apps/continuum
exec /Users/bioinfo/apps/continuum/.venv/bin/python -c "
from continuum.mcp_server import run_sse
run_sse(host='0.0.0.0', port=8765)
"
