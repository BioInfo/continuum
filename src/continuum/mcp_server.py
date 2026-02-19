"""MCP Server for Continuum - expose context to Claude via MCP protocol."""

import os
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import Config
from .export import generate_export
from .files import count_memory_entries, extract_current_focus

# Create server instance
server = Server("continuum")


def get_config() -> Config:
    """Load config, optionally detecting project context."""
    project_path = os.environ.get("CONTINUUM_PROJECT_PATH")
    start_path = Path(project_path) if project_path else None
    return Config.load(start_path=start_path)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_context",
            description="Get the user's full context including identity, voice, current context, and recent memories. Use this at the start of a conversation to understand who you're talking to.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_identity",
            description="Get the user's identity information (name, role, background, values).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_voice",
            description="Get the user's voice and communication style guide. Use this when writing content as or for the user.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_current_context",
            description="Get the user's current working context (active projects, focus areas, this week's priorities).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_memories",
            description="Get the user's memories (facts, decisions, lessons, preferences). Optionally filter by category or search term.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category: fact, decision, lesson, preference",
                        "enum": ["fact", "decision", "lesson", "preference"],
                    },
                    "search": {
                        "type": "string",
                        "description": "Search term to filter memories",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return (default: 20)",
                        "default": 20,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="remember",
            description="Save a new memory for the user. Use this to remember important facts, decisions, lessons learned, or preferences discovered during conversation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The memory to save",
                    },
                    "category": {
                        "type": "string",
                        "description": "Memory category",
                        "enum": ["fact", "decision", "lesson", "preference"],
                        "default": "fact",
                    },
                    "project": {
                        "type": "boolean",
                        "description": "Save to project memory instead of global (default: false)",
                        "default": False,
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="get_status",
            description="Get Continuum status including file ages, memory count, and current focus.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    config = get_config()

    if name == "get_context":
        content = generate_export(config)
        return [TextContent(type="text", text=content)]

    elif name == "get_identity":
        if config.identity_path.exists():
            content = config.identity_path.read_text()
            return [TextContent(type="text", text=content)]
        return [TextContent(type="text", text="Identity not configured. Run `continuum init` to set up.")]

    elif name == "get_voice":
        # Check project voice first, then global
        voice_path = config.project_voice_path or (
            config.voice_path if config.voice_path.exists() else None
        )
        if voice_path:
            content = voice_path.read_text()
            return [TextContent(type="text", text=content)]
        return [TextContent(type="text", text="Voice profile not configured.")]

    elif name == "get_current_context":
        parts = []

        # Global context
        if config.context_path.exists():
            parts.append("# Global Context\n")
            parts.append(config.context_path.read_text())

        # Project context
        if config.project_context_path:
            parts.append("\n\n# Project Context\n")
            parts.append(config.project_context_path.read_text())

        if parts:
            return [TextContent(type="text", text="".join(parts))]
        return [TextContent(type="text", text="No context configured.")]

    elif name == "get_memories":
        category = arguments.get("category")
        search = arguments.get("search", "").lower()
        limit = arguments.get("limit", 20)

        memories = []

        # Collect from global and project memory
        memory_paths = [config.memory_path]
        if config.project_memory_path:
            memory_paths.append(config.project_memory_path)

        for mem_path in memory_paths:
            if mem_path.exists():
                content = mem_path.read_text()
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("[") and "]" in line:
                        # Filter by category if specified
                        if category:
                            if f"] {category.upper()}" not in line.upper():
                                continue
                        # Filter by search term if specified
                        if search and search not in line.lower():
                            continue
                        memories.append(line)

        # Sort by date (most recent first) and limit
        memories.sort(reverse=True)
        memories = memories[:limit]

        if memories:
            return [TextContent(type="text", text="\n".join(memories))]
        return [TextContent(type="text", text="No memories found matching criteria.")]

    elif name == "remember":
        text = arguments.get("text", "")
        category = arguments.get("category", "fact")
        use_project = arguments.get("project", False)

        if not text:
            return [TextContent(type="text", text="Error: text is required")]

        # Determine target memory file
        if use_project and config.has_project:
            memory_path = config.project_path / "memory.md"
            location = "project memory"
        else:
            memory_path = config.memory_path
            location = "global memory"

        if not memory_path.exists():
            return [TextContent(type="text", text=f"Error: {memory_path} not found. Run `continuum init` first.")]

        # Format and append entry
        date = datetime.now().strftime("%Y-%m-%d")
        entry = f"[{date}] {category.upper()} - {text}"

        with open(memory_path, "a") as f:
            f.write(f"\n{entry}")

        return [TextContent(type="text", text=f"Saved to {location}: {entry}")]

    elif name == "get_status":
        parts = []

        # Global status
        parts.append(f"Continuum: {config.base_path}")
        parts.append("")

        files = [
            ("identity.md", config.identity_path),
            ("voice.md", config.voice_path),
            ("context.md", config.context_path),
            ("memory.md", config.memory_path),
        ]

        for name, path in files:
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                age = datetime.now() - mtime
                parts.append(f"  {name}: {age.days}d old")
            else:
                parts.append(f"  {name}: missing")

        # Memory count
        mem_count = count_memory_entries(config.memory_path)
        parts.append(f"\nMemories: {mem_count} entries")

        # Current focus
        focus = extract_current_focus(config.context_path)
        if focus:
            parts.append(f"Focus: {focus}")

        # Project status
        if config.has_project:
            parts.append(f"\nProject: {config.project_path}")
            if config.project_context_path:
                project_focus = extract_current_focus(config.project_context_path)
                if project_focus:
                    parts.append(f"Project focus: {project_focus}")

        return [TextContent(type="text", text="\n".join(parts))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main_stdio():
    """Run the MCP server with stdio transport (for local use)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run_stdio():
    """Entry point for stdio server (local Claude Code/Desktop)."""
    import asyncio
    asyncio.run(main_stdio())


def run_sse(host: str = "0.0.0.0", port: int = 8765):
    """
    Run the MCP server with SSE transport (for remote access via Tailscale).

    Args:
        host: Host to bind to. Use 0.0.0.0 for Tailscale access.
        port: Port to listen on.
    """
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import JSONResponse
    import uvicorn

    # Create SSE transport - messages endpoint relative to where SSE is served
    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    async def health_check(request):
        return JSONResponse({"status": "ok", "server": "continuum-mcp"})

    app = Starlette(
        debug=False,
        routes=[
            # Health check
            Route("/health", endpoint=health_check),
            # SSE endpoints at multiple paths for compatibility
            Route("/sse", endpoint=handle_sse),
            Route("/mcp/sse", endpoint=handle_sse),
            # Messages endpoints
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
            Route("/mcp/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )

    print(f"Starting Continuum MCP server on http://{host}:{port}")
    print(f"SSE endpoints:")
    print(f"  http://{host}:{port}/sse")
    print(f"  http://{host}:{port}/mcp/sse")
    print(f"Health check: http://{host}:{port}/health")
    uvicorn.run(app, host=host, port=port, log_level="info")


def run_http(host: str = "0.0.0.0", port: int = 8765):
    """
    Run the MCP server with Streamable HTTP transport (recommended for remote access).

    Args:
        host: Host to bind to. Use 0.0.0.0 for Tailscale access.
        port: Port to listen on.
    """
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.responses import JSONResponse
    import uvicorn

    session_manager = StreamableHTTPSessionManager(app=server, stateless=True)

    async def health_check(request):
        return JSONResponse({"status": "ok", "server": "continuum-mcp", "transport": "streamable-http"})

    app = Starlette(
        debug=False,
        routes=[
            Route("/health", endpoint=health_check),
            Mount("/mcp", app=session_manager.handle_request),
        ],
    )

    print(f"Starting Continuum MCP server (Streamable HTTP) on http://{host}:{port}")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print(f"Health check: http://{host}:{port}/health")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_stdio()
