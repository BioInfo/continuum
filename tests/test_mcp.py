"""Tests for MCP server tool handlers."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from continuum.config import Config
from continuum.mcp_server import server, call_tool


def make_config(tmp_path):
    """Create a test config with populated files."""
    base = tmp_path / ".continuum"
    base.mkdir()
    (base / "identity.md").write_text("# Identity\n\nTest user, software engineer")
    (base / "voice.md").write_text("# Voice\n\nDirect and concise")
    (base / "context.md").write_text("# Context\n\n## Current Focus\nBuilding tests")
    today = datetime.now().strftime("%Y-%m-%d")
    (base / "memory.md").write_text(
        f"# Memory\n\n[{today}] FACT - Test fact\n[{today}] DECISION - Chose pytest\n[{today}] LESSON - Tests matter"
    )
    (base / "config.yaml").write_text("")
    (base / "exports").mkdir()
    return Config.load(base_path=base, detect_project=False)


class TestCallTool:
    """Tests for MCP call_tool handler."""

    @pytest.mark.asyncio
    async def test_get_context(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_context", {})
        assert len(result) == 1
        assert "Identity" in result[0].text

    @pytest.mark.asyncio
    async def test_get_identity(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_identity", {})
        assert "Test user" in result[0].text

    @pytest.mark.asyncio
    async def test_get_voice(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_voice", {})
        assert "Direct and concise" in result[0].text

    @pytest.mark.asyncio
    async def test_get_current_context(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_current_context", {})
        assert "Building tests" in result[0].text

    @pytest.mark.asyncio
    async def test_get_memories_all(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_memories", {})
        text = result[0].text
        assert "Test fact" in text
        assert "Chose pytest" in text

    @pytest.mark.asyncio
    async def test_get_memories_filter_category(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_memories", {"category": "decision"})
        text = result[0].text
        assert "Chose pytest" in text
        assert "Test fact" not in text

    @pytest.mark.asyncio
    async def test_get_memories_search(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_memories", {"search": "pytest"})
        text = result[0].text
        assert "Chose pytest" in text
        assert "Test fact" not in text

    @pytest.mark.asyncio
    async def test_remember(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("remember", {"text": "New memory entry", "category": "fact"})
        assert "Saved" in result[0].text
        assert "New memory entry" in result[0].text
        # Verify it was written
        memory_content = config.memory_path.read_text()
        assert "New memory entry" in memory_content

    @pytest.mark.asyncio
    async def test_remember_empty_text(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("remember", {"text": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_get_status(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("get_status", {})
        text = result[0].text
        assert "identity.md" in text
        assert "Memories" in text

    @pytest.mark.asyncio
    async def test_unknown_tool(self, tmp_path):
        config = make_config(tmp_path)
        with patch("continuum.mcp_server.get_config", return_value=config):
            result = await call_tool("nonexistent_tool", {})
        assert "Unknown tool" in result[0].text
