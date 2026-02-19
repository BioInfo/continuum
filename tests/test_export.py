"""Tests for export module."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from continuum.config import Config
from continuum.export import condense_content, filter_recent_memory, generate_export


class TestCondenseContent:
    """Tests for condense_content()."""

    def test_short_content_unchanged(self):
        content = "# Title\n\nShort paragraph here."
        result = condense_content(content, max_words=500)
        assert result == content

    def test_truncates_at_word_limit(self):
        content = "# Title\n\n" + " ".join(["word"] * 100)
        result = condense_content(content, max_words=20)
        word_count = len(result.split())
        assert word_count <= 25  # headers + some buffer

    def test_preserves_headers(self):
        content = "# Title\n\n" + " ".join(["word"] * 50) + "\n\n## Section Two\n\nMore text."
        result = condense_content(content, max_words=10)
        assert "# Title" in result

    def test_empty_content(self):
        result = condense_content("", max_words=500)
        assert result == ""


class TestFilterRecentMemory:
    """Tests for filter_recent_memory()."""

    def test_filters_by_date(self):
        today = datetime.now().strftime("%Y-%m-%d")
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        content = f"# Memory\n\n[{today}] FACT - Recent entry\n[{old_date}] FACT - Old entry"
        result = filter_recent_memory(content, days=30, max_entries=20)
        assert "Recent entry" in result
        # Old entry may still appear due to max_entries fallback
        # but recent entry should be first
        lines = result.strip().split("\n")
        assert "Recent entry" in lines[0]

    def test_max_entries_as_minimum_when_old(self):
        """max_entries acts as a floor: old entries are kept up to max_entries even outside date range."""
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        entries = "\n".join(f"[{old_date}] FACT - Old entry {i}" for i in range(10))
        content = f"# Memory\n\n{entries}"
        result = filter_recent_memory(content, days=30, max_entries=3)
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert len(lines) == 3

    def test_empty_memory(self):
        result = filter_recent_memory("# Memory\n\n", days=30, max_entries=20)
        assert result == ""

    def test_malformed_date_not_parsed(self):
        """Entries with unparseable dates are not included (they don't match date format)."""
        content = "# Memory\n\n[bad-date] FACT - Malformed entry"
        result = filter_recent_memory(content, days=30, max_entries=20)
        # "bad-date" doesn't parse as YYYY-MM-DD or YYYY-MM, so no entries
        assert result == ""


class TestGenerateExport:
    """Tests for generate_export()."""

    def test_basic_export(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()
        (base / "identity.md").write_text("# Identity\n\n## Core\nTest user")
        (base / "voice.md").write_text("# Voice\n\n## Do\nBe direct")
        (base / "context.md").write_text("# Context\n\n## Current Focus\nTesting")
        (base / "memory.md").write_text(f"# Memory\n\n[{datetime.now().strftime('%Y-%m-%d')}] FACT - Test memory")
        (base / "config.yaml").write_text("stale_days: 14\n")
        (base / "exports").mkdir()

        config = Config.load(base_path=base, detect_project=False)
        result = generate_export(config)

        assert "## Identity" in result
        assert "## Voice" in result
        assert "## Current Context" in result
        assert "## Relevant Memory" in result
        assert "Continuum Export" in result

    def test_export_with_project_context(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()
        (base / "identity.md").write_text("# Identity\n\nGlobal user")
        (base / "voice.md").write_text("# Voice\n\nGlobal voice")
        (base / "context.md").write_text("# Context\n\n## Current Focus\nGlobal focus")
        (base / "memory.md").write_text("# Memory\n\n")
        (base / "config.yaml").write_text("")
        (base / "exports").mkdir()

        project = tmp_path / "project" / ".continuum"
        project.mkdir(parents=True)
        (project / "context.md").write_text("# Project Context\n\nProject focus here")

        config = Config._from_dict({}, base, project_path=project)
        result = generate_export(config)

        assert "Global focus" in result
        assert "Project focus here" in result
