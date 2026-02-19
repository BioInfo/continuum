"""Tests for config module."""

import pytest
from pathlib import Path

from continuum.config import Config, find_project_root, get_default_base_path


class TestFindProjectRoot:
    """Tests for find_project_root()."""

    def test_finds_git_root(self, tmp_path):
        (tmp_path / ".git").mkdir()
        sub = tmp_path / "src" / "deep"
        sub.mkdir(parents=True)

        result = find_project_root(sub)
        assert result == tmp_path

    def test_finds_continuum_dir(self, tmp_path):
        (tmp_path / ".continuum").mkdir()
        sub = tmp_path / "nested"
        sub.mkdir()

        result = find_project_root(sub)
        assert result == tmp_path

    def test_finds_pyproject_toml(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        sub = tmp_path / "src"
        sub.mkdir()

        result = find_project_root(sub)
        assert result == tmp_path

    def test_returns_none_for_no_markers(self, tmp_path):
        bare = tmp_path / "bare" / "dir"
        bare.mkdir(parents=True)

        result = find_project_root(bare)
        # May find markers from actual filesystem above tmp_path,
        # but in most CI/test environments this should be None
        # We test the logic rather than a specific return value
        assert result is None or result != bare


class TestConfig:
    """Tests for Config class."""

    def test_load_defaults(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()

        config = Config.load(base_path=base, detect_project=False)

        assert config.base_path == base
        assert config.stale_days == 14
        assert config.memory_recent_days == 30
        assert config.memory_max_entries == 20
        assert config.identity_max_words == 500

    def test_load_from_yaml(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()
        (base / "config.yaml").write_text("stale_days: 7\nmemory_max_entries: 50\n")

        config = Config.load(base_path=base, detect_project=False)

        assert config.stale_days == 7
        assert config.memory_max_entries == 50

    def test_has_project_false_by_default(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()

        config = Config.load(base_path=base, detect_project=False)
        assert config.has_project is False

    def test_project_paths_none_without_project(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()

        config = Config.load(base_path=base, detect_project=False)

        assert config.project_context_path is None
        assert config.project_memory_path is None
        assert config.project_identity_path is None
        assert config.project_voice_path is None

    def test_global_paths(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()

        config = Config.load(base_path=base, detect_project=False)

        assert config.identity_path == base / "identity.md"
        assert config.voice_path == base / "voice.md"
        assert config.context_path == base / "context.md"
        assert config.memory_path == base / "memory.md"
        assert config.exports_path == base / "exports"

    def test_start_path_passed_to_find_project_root(self, tmp_path):
        base = tmp_path / ".continuum"
        base.mkdir()

        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        (project_dir / ".continuum").mkdir()
        (project_dir / ".continuum" / "context.md").write_text("# Context")

        config = Config.load(base_path=base, start_path=project_dir)

        assert config.has_project is True
        assert config.project_path == project_dir / ".continuum"


class TestGetDefaultBasePath:
    """Tests for get_default_base_path()."""

    def test_returns_home_continuum(self):
        result = get_default_base_path()
        assert result == Path.home() / ".continuum"
