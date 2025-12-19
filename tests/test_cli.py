"""Tests for Continuum CLI."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from continuum.cli import cli, auto_detect_category


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_continuum(tmp_path):
    """Create a temporary continuum directory."""
    return tmp_path / ".continuum"


class TestInit:
    """Tests for the init command."""

    def test_init_creates_structure(self, runner, temp_continuum):
        """Init should create directory structure with templates."""
        result = runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        assert result.exit_code == 0
        assert temp_continuum.exists()
        assert (temp_continuum / "identity.md").exists()
        assert (temp_continuum / "voice.md").exists()
        assert (temp_continuum / "context.md").exists()
        assert (temp_continuum / "memory.md").exists()
        assert (temp_continuum / "config.yaml").exists()
        assert (temp_continuum / "exports").exists()

    def test_init_no_overwrite(self, runner, temp_continuum):
        """Init should not overwrite existing files without --force."""
        # First init
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        # Modify a file
        identity = temp_continuum / "identity.md"
        identity.write_text("Custom content")

        # Second init (should skip existing)
        result = runner.invoke(cli, ["init", "--path", str(temp_continuum)], input="y\n")

        assert identity.read_text() == "Custom content"
        assert "Skipped" in result.output

    def test_init_force_overwrites(self, runner, temp_continuum):
        """Init with --force should overwrite existing files."""
        # First init
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        # Modify a file
        identity = temp_continuum / "identity.md"
        identity.write_text("Custom content")

        # Second init with --force
        runner.invoke(cli, ["init", "--path", str(temp_continuum), "--force"])

        assert identity.read_text() != "Custom content"


class TestRemember:
    """Tests for the remember command."""

    def test_remember_adds_entry(self, runner, temp_continuum):
        """Remember should add an entry to memory.md."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(
            cli, ["remember", "Test memory entry", "--path", str(temp_continuum)]
        )

        assert result.exit_code == 0
        memory = (temp_continuum / "memory.md").read_text()
        assert "Test memory entry" in memory
        assert "FACT" in memory  # Default category

    def test_remember_with_category(self, runner, temp_continuum):
        """Remember should use specified category."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(
            cli,
            [
                "remember",
                "Chose FastAPI",
                "--category",
                "decision",
                "--path",
                str(temp_continuum),
            ],
        )

        assert result.exit_code == 0
        memory = (temp_continuum / "memory.md").read_text()
        assert "DECISION" in memory

    def test_remember_autodetects_decision(self, runner, temp_continuum):
        """Remember should auto-detect decision category."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(
            cli,
            ["remember", "Decided to use Python", "--path", str(temp_continuum)],
        )

        assert result.exit_code == 0
        assert "DECISION" in result.output


class TestAutoDetectCategory:
    """Tests for category auto-detection."""

    def test_detects_decision(self):
        assert auto_detect_category("Decided to use FastAPI") == "decision"
        assert auto_detect_category("I chose Python over JavaScript") == "decision"
        assert auto_detect_category("We went with the cheaper option") == "decision"

    def test_detects_lesson(self):
        assert auto_detect_category("Learned that caching is important") == "lesson"
        assert auto_detect_category("I realized the bug was in auth") == "lesson"
        assert auto_detect_category("Turns out the API has rate limits") == "lesson"

    def test_detects_preference(self):
        assert auto_detect_category("I prefer short functions") == "preference"
        assert auto_detect_category("I always use type hints") == "preference"
        assert auto_detect_category("Never use global state") == "preference"

    def test_defaults_to_fact(self):
        assert auto_detect_category("Team size is 80 people") == "fact"
        assert auto_detect_category("The API endpoint is /v1/users") == "fact"


class TestExport:
    """Tests for the export command."""

    def test_export_creates_file(self, runner, temp_continuum):
        """Export should create a claude-code.md file."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(cli, ["export", "--path", str(temp_continuum)])

        assert result.exit_code == 0
        export_file = temp_continuum / "exports" / "claude-code.md"
        assert export_file.exists()

    def test_export_contains_sections(self, runner, temp_continuum):
        """Export should contain all main sections."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(
            cli, ["export", "--stdout", "--path", str(temp_continuum)]
        )

        assert "## Identity" in result.output
        assert "## Voice" in result.output
        assert "## Current Context" in result.output

    def test_export_to_custom_path(self, runner, temp_continuum, tmp_path):
        """Export should write to custom output path."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])
        custom_output = tmp_path / "custom.md"

        result = runner.invoke(
            cli,
            ["export", "--output", str(custom_output), "--path", str(temp_continuum)],
        )

        assert result.exit_code == 0
        assert custom_output.exists()


class TestStatus:
    """Tests for the status command."""

    def test_status_shows_files(self, runner, temp_continuum):
        """Status should show all context files."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(cli, ["status", "--path", str(temp_continuum)])

        assert result.exit_code == 0
        assert "identity.md" in result.output
        assert "voice.md" in result.output
        assert "context.md" in result.output
        assert "memory.md" in result.output

    def test_status_not_initialized(self, runner, tmp_path):
        """Status should report if not initialized."""
        result = runner.invoke(cli, ["status", "--path", str(tmp_path / "nonexistent")])

        assert "not initialized" in result.output.lower()


class TestValidate:
    """Tests for the validate command."""

    def test_validate_passes_for_valid(self, runner, temp_continuum):
        """Validate should pass for freshly initialized files."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        result = runner.invoke(cli, ["validate", "--path", str(temp_continuum)])

        assert result.exit_code == 0
        assert "All files valid" in result.output

    def test_validate_detects_missing_sections(self, runner, temp_continuum):
        """Validate should detect missing required sections."""
        runner.invoke(cli, ["init", "--path", str(temp_continuum)])

        # Remove a required section
        identity = temp_continuum / "identity.md"
        identity.write_text("# Identity\n\nNo sections here.")

        result = runner.invoke(cli, ["validate", "--path", str(temp_continuum)])

        assert "Missing" in result.output
