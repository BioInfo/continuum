"""File operations for Continuum."""

import importlib.resources
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .config import Config, find_project_root


def init_directory(base_path: Path, force: bool = False) -> list[str]:
    """
    Initialize the Continuum directory structure.

    Returns list of actions taken.
    """
    actions = []

    # Create base directory
    if not base_path.exists():
        base_path.mkdir(parents=True)
        actions.append(f"Created {base_path}")

    # Create exports subdirectory
    exports_dir = base_path / "exports"
    if not exports_dir.exists():
        exports_dir.mkdir()
        actions.append(f"Created {exports_dir}")

    # Copy templates
    templates = ["identity.md", "voice.md", "context.md", "memory.md", "config.yaml"]

    for template_name in templates:
        dest = base_path / template_name
        if dest.exists() and not force:
            actions.append(f"Skipped {template_name} (exists)")
        else:
            content = load_template(template_name)
            # Replace placeholder date with today
            content = content.replace("[Today's date]", datetime.now().strftime("%Y-%m-%d"))
            dest.write_text(content)
            actions.append(f"Created {template_name}")

    return actions


def init_project(project_root: Path | None = None, force: bool = False) -> list[str]:
    """
    Initialize project-level .continuum/ directory.

    Creates context.md and memory.md for project-specific context.
    Returns list of actions taken.
    """
    actions = []

    # Find project root if not specified
    if project_root is None:
        project_root = find_project_root()
        if project_root is None:
            project_root = Path.cwd()

    continuum_dir = project_root / ".continuum"

    # Create directory
    if not continuum_dir.exists():
        continuum_dir.mkdir(parents=True)
        actions.append(f"Created {continuum_dir}")

    # Project uses minimal templates: context and memory
    # Identity and voice are typically inherited from global
    project_templates = {
        "context.md": f"""# Project Context

## Project

**Name:** {project_root.name}
**Path:** {project_root}

## Tech Stack

<!-- Languages, frameworks, key dependencies -->

## Team

<!-- Key collaborators on this project -->

## Current Focus

<!-- What you're currently working on in this project -->
""",
        "memory.md": """# Project Memory

<!-- Project-specific decisions, learnings, and context -->
<!-- Format: [YYYY-MM-DD] Entry text -->

""",
    }

    for filename, content in project_templates.items():
        dest = continuum_dir / filename
        if dest.exists() and not force:
            actions.append(f"Skipped {filename} (exists)")
        else:
            content = content.replace("[Today's date]", datetime.now().strftime("%Y-%m-%d"))
            dest.write_text(content)
            actions.append(f"Created {filename}")

    # Add to .gitignore if it exists and .continuum not already ignored
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        gitignore_content = gitignore.read_text()
        if ".continuum/" not in gitignore_content and ".continuum\n" not in gitignore_content:
            with open(gitignore, "a") as f:
                f.write("\n# Continuum local context\n.continuum/\n")
            actions.append("Added .continuum/ to .gitignore")

    return actions


def load_template(name: str) -> str:
    """Load a template file from the package."""
    try:
        # Try to load from package resources
        files = importlib.resources.files("continuum") / "templates" / name
        return files.read_text()
    except Exception:
        # Fallback to relative path during development
        template_path = Path(__file__).parent / "templates" / name
        if template_path.exists():
            return template_path.read_text()
        raise FileNotFoundError(f"Template not found: {name}")


def open_in_editor(path: Path) -> bool:
    """Open a file in the user's editor."""
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

    try:
        subprocess.run([editor, str(path)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        # Editor not found, try common fallbacks
        for fallback in ["nano", "vim", "vi"]:
            try:
                subprocess.run([fallback, str(path)], check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        return False


def get_file_age_str(path: Path) -> str:
    """Get human-readable file age."""
    if not path.exists():
        return "missing"

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - mtime

    if age.days == 0:
        if age.seconds < 3600:
            minutes = age.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        hours = age.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif age.days == 1:
        return "1 day ago"
    elif age.days < 7:
        return f"{age.days} days ago"
    elif age.days < 14:
        return "1 week ago"
    elif age.days < 30:
        weeks = age.days // 7
        return f"{weeks} weeks ago"
    elif age.days < 60:
        return "1 month ago"
    else:
        months = age.days // 30
        return f"{months} months ago"


def is_stale(path: Path, stale_days: int) -> bool:
    """Check if a file is stale (older than threshold)."""
    if not path.exists():
        return False

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - mtime
    return age.days > stale_days


def count_memory_entries(path: Path) -> int:
    """Count memory entries in memory.md."""
    if not path.exists():
        return 0

    content = path.read_text()
    # Count lines that start with [YYYY-MM-DD] or [YYYY-MM]
    count = 0
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("[") and "]" in line:
            # Check if it looks like a date
            bracket_content = line[1 : line.index("]")]
            if "-" in bracket_content and len(bracket_content) >= 7:
                count += 1
    return count


def extract_current_focus(path: Path) -> str | None:
    """Extract current focus from context.md."""
    if not path.exists():
        return None

    content = path.read_text()

    # Look for "## Current Focus" section
    lines = content.split("\n")
    in_focus_section = False
    focus_lines = []

    for line in lines:
        if line.strip().lower() == "## current focus":
            in_focus_section = True
            continue
        elif line.startswith("## ") and in_focus_section:
            break
        elif in_focus_section and line.strip():
            focus_lines.append(line.strip())

    if focus_lines:
        # Return first non-empty line, truncated
        focus = focus_lines[0]
        if len(focus) > 60:
            focus = focus[:57] + "..."
        return focus

    return None


def get_last_export_time(exports_path: Path) -> datetime | None:
    """Get the timestamp of the last export."""
    export_file = exports_path / "claude-code.md"
    if export_file.exists():
        return datetime.fromtimestamp(export_file.stat().st_mtime)
    return None
