"""Configuration management for Continuum."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def find_project_root(start_path: Path | None = None) -> Path | None:
    """
    Find project root by looking for .continuum/, .git/, or pyproject.toml.

    Searches from start_path up to filesystem root.
    Returns None if no project markers found.
    """
    if start_path is None:
        start_path = Path.cwd()

    start_path = start_path.resolve()
    markers = [".continuum", ".git", "pyproject.toml", "package.json", "Cargo.toml"]

    current = start_path
    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    return None


@dataclass
class Config:
    """Continuum configuration."""

    # Thresholds
    stale_days: int = 14
    memory_recent_days: int = 30
    memory_max_entries: int = 20

    # Export settings
    identity_max_words: int = 500

    # Paths (set after load)
    base_path: Path = field(default_factory=lambda: Path.home() / ".continuum")
    project_path: Path | None = None  # .continuum/ in project root, if exists

    @classmethod
    def load(cls, base_path: Path | None = None, detect_project: bool = True) -> "Config":
        """
        Load configuration from config.yaml if it exists.

        If detect_project is True, also looks for .continuum/ in project root.
        Project config values override global config values.
        """
        if base_path is None:
            base_path = Path.home() / ".continuum"

        # Start with defaults
        config_data: dict[str, Any] = {}

        # Load global config
        global_config_file = base_path / "config.yaml"
        if global_config_file.exists():
            try:
                with open(global_config_file) as f:
                    config_data = yaml.safe_load(f) or {}
            except Exception:
                pass

        # Detect project path
        project_path = None
        if detect_project:
            project_root = find_project_root()
            if project_root:
                candidate = project_root / ".continuum"
                if candidate.exists() and candidate.is_dir():
                    project_path = candidate

                    # Load and merge project config (overrides global)
                    project_config_file = candidate / "config.yaml"
                    if project_config_file.exists():
                        try:
                            with open(project_config_file) as f:
                                project_data = yaml.safe_load(f) or {}
                                config_data.update(project_data)
                        except Exception:
                            pass

        return cls._from_dict(config_data, base_path, project_path)

    @classmethod
    def _from_dict(
        cls, data: dict[str, Any], base_path: Path, project_path: Path | None = None
    ) -> "Config":
        """Create config from dictionary."""
        return cls(
            stale_days=data.get("stale_days", 14),
            memory_recent_days=data.get("memory_recent_days", 30),
            memory_max_entries=data.get("memory_max_entries", 20),
            identity_max_words=data.get("identity_max_words", 500),
            base_path=base_path,
            project_path=project_path,
        )

    @property
    def has_project(self) -> bool:
        """Check if project-level context exists."""
        return self.project_path is not None

    # Global paths
    @property
    def identity_path(self) -> Path:
        return self.base_path / "identity.md"

    @property
    def voice_path(self) -> Path:
        return self.base_path / "voice.md"

    @property
    def context_path(self) -> Path:
        return self.base_path / "context.md"

    @property
    def memory_path(self) -> Path:
        return self.base_path / "memory.md"

    @property
    def exports_path(self) -> Path:
        return self.base_path / "exports"

    # Project paths (return None if no project)
    @property
    def project_identity_path(self) -> Path | None:
        if self.project_path:
            p = self.project_path / "identity.md"
            return p if p.exists() else None
        return None

    @property
    def project_voice_path(self) -> Path | None:
        if self.project_path:
            p = self.project_path / "voice.md"
            return p if p.exists() else None
        return None

    @property
    def project_context_path(self) -> Path | None:
        if self.project_path:
            p = self.project_path / "context.md"
            return p if p.exists() else None
        return None

    @property
    def project_memory_path(self) -> Path | None:
        if self.project_path:
            p = self.project_path / "memory.md"
            return p if p.exists() else None
        return None

    def get_effective_path(self, file_type: str) -> Path | None:
        """
        Get the effective path for a file type, preferring project over global.

        For identity and voice, project overrides global.
        Returns None if file doesn't exist at either level.
        """
        project_paths = {
            "identity": self.project_identity_path,
            "voice": self.project_voice_path,
            "context": self.project_context_path,
            "memory": self.project_memory_path,
        }
        global_paths = {
            "identity": self.identity_path,
            "voice": self.voice_path,
            "context": self.context_path,
            "memory": self.memory_path,
        }

        # Project overrides global for identity/voice
        if file_type in ("identity", "voice"):
            project_p = project_paths.get(file_type)
            if project_p and project_p.exists():
                return project_p

        global_p = global_paths.get(file_type)
        if global_p and global_p.exists():
            return global_p

        return None


def get_default_base_path() -> Path:
    """Get the default base path for Continuum."""
    return Path.home() / ".continuum"
