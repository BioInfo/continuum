# ClaudeSync Implementation Spec: Phase 1

## Ready for Claude Code Execution

---

## Overview

This document provides the technical specification for Phase 1 of ClaudeSync. Open this in Claude Code and say: "Let's build Phase 1 of ClaudeSync following this spec."

---

## Project Setup

### Directory Structure
```
claudesync/
├── pyproject.toml
├── README.md
├── src/
│   └── claudesync/
│       ├── __init__.py
│       ├── cli.py              # Click-based CLI
│       ├── config.py           # Configuration handling
│       ├── models.py           # Data models
│       ├── files.py            # File operations
│       ├── export.py           # Export generators
│       └── templates/
│           ├── IDENTITY.md
│           ├── VOICE.md
│           ├── CONTEXT.md
│           ├── MEMORY.md
│           └── config.yaml
└── tests/
    └── test_cli.py
```

### pyproject.toml
```toml
[project]
name = "claudesync"
version = "0.1.0"
description = "Unified memory and voice system for Claude AI interfaces"
requires-python = ">=3.11"
dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "rich>=13.0",
    "python-dateutil>=2.8",
]

[project.scripts]
claudesync = "claudesync.cli:cli"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

---

## Phase 1 Deliverables

### 1. `claudesync init`

**Purpose**: Initialize ClaudeSync directory structure

**Behavior**:
```bash
$ claudesync init
# Creates ~/.claudesync/ with template files
# Does not overwrite existing files
# Prints what was created
```

**Implementation**:
```python
@cli.command()
@click.option('--path', default='~/.claudesync', help='Custom path')
def init(path):
    """Initialize ClaudeSync directory structure."""
    base_path = Path(path).expanduser()
    
    if base_path.exists():
        if not click.confirm(f'{base_path} exists. Continue?'):
            return
    
    # Create directories
    directories = [
        base_path,
        base_path / 'sync',
        base_path / 'voice-samples' / 'emails',
        base_path / 'voice-samples' / 'technical',
        base_path / 'voice-samples' / 'feedback',
        base_path / 'voice-samples' / 'casual',
    ]
    
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy templates (don't overwrite)
    templates = ['IDENTITY.md', 'VOICE.md', 'CONTEXT.md', 'MEMORY.md', 'config.yaml']
    for template in templates:
        dest = base_path / template
        if not dest.exists():
            copy_template(template, dest)
            console.print(f"Created {dest}")
        else:
            console.print(f"Skipped {dest} (exists)")
```

---

### 2. `claudesync edit <file>`

**Purpose**: Open a context file in $EDITOR

**Behavior**:
```bash
$ claudesync edit identity    # Opens IDENTITY.md
$ claudesync edit voice       # Opens VOICE.md
$ claudesync edit context     # Opens CONTEXT.md
$ claudesync edit memory      # Opens MEMORY.md
```

**Implementation**:
```python
@cli.command()
@click.argument('file', type=click.Choice(['identity', 'voice', 'context', 'memory']))
def edit(file):
    """Open a context file in your editor."""
    file_map = {
        'identity': 'IDENTITY.md',
        'voice': 'VOICE.md',
        'context': 'CONTEXT.md',
        'memory': 'MEMORY.md',
    }
    
    path = get_claudesync_path() / file_map[file]
    
    if not path.exists():
        console.print(f"[red]{path} does not exist. Run 'claudesync init' first.[/red]")
        return
    
    editor = os.environ.get('EDITOR', 'nano')
    os.system(f'{editor} {path}')
```

---

### 3. `claudesync status`

**Purpose**: Show current context summary

**Behavior**:
```bash
$ claudesync status
╭──────────────────── ClaudeSync Status ────────────────────╮
│ Location: ~/.claudesync                                    │
│ Last sync: 2024-12-18 (1 day ago)                         │
├────────────────────────────────────────────────────────────┤
│ IDENTITY.md   ✓  Updated 3 days ago                       │
│ VOICE.md      ✓  Updated 1 week ago                       │
│ CONTEXT.md    ⚠  Updated 2 weeks ago (stale?)             │
│ MEMORY.md     ✓  47 entries (3 from last 7 days)          │
├────────────────────────────────────────────────────────────┤
│ Current Focus: Navari framework production deployment      │
│ Voice samples: 12 files across 4 categories               │
╰────────────────────────────────────────────────────────────╯
```

**Implementation**:
```python
@cli.command()
def status():
    """Show current context summary."""
    base_path = get_claudesync_path()
    
    if not base_path.exists():
        console.print("[red]ClaudeSync not initialized. Run 'claudesync init'[/red]")
        return
    
    # Build status info
    files_status = []
    for fname in ['IDENTITY.md', 'VOICE.md', 'CONTEXT.md', 'MEMORY.md']:
        path = base_path / fname
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age = datetime.now() - mtime
            status = "✓" if age.days < 14 else "⚠"
            files_status.append((fname, status, format_age(age)))
        else:
            files_status.append((fname, "✗", "missing"))
    
    # Extract current focus from CONTEXT.md
    current_focus = extract_current_focus(base_path / 'CONTEXT.md')
    
    # Count memory entries
    memory_count = count_memory_entries(base_path / 'MEMORY.md')
    
    # Count voice samples
    voice_samples = count_voice_samples(base_path / 'voice-samples')
    
    # Render with Rich
    render_status_panel(files_status, current_focus, memory_count, voice_samples)
```

---

### 4. `claudesync export claude-code`

**Purpose**: Generate merged context file for Claude Code

**Behavior**:
```bash
$ claudesync export claude-code
# Outputs to stdout

$ claudesync export claude-code --output ./CLAUDESYNC.md
# Writes to file

$ claudesync export claude-code --project ./my-project
# Creates CLAUDESYNC.md in project directory
```

**Output Format**:
```markdown
<!-- ClaudeSync Export -->
<!-- Generated: 2024-12-19T10:30:00-05:00 -->
<!-- Source: ~/.claudesync -->
<!-- Refresh: Run 'claudesync export claude-code' to update -->

# User Context

## Identity

[Condensed content from IDENTITY.md - first 500 words or key sections]

## Voice & Communication Style

[Key directives from VOICE.md]

### Always
- [Bullet points]

### Never  
- [Bullet points]

## Current Context

[Full CONTEXT.md - this changes frequently so include all of it]

## Relevant Memory

[Last 30 days of MEMORY.md entries, or last 20 entries, whichever is more]

---
*This context was generated by ClaudeSync. See github.com/[you]/claudesync*
```

**Implementation**:
```python
@cli.command('export')
@click.argument('format', type=click.Choice(['claude-code', 'raw']))
@click.option('--output', '-o', help='Output file path')
@click.option('--project', '-p', help='Project directory')
def export_cmd(format, output, project):
    """Export context for different interfaces."""
    base_path = get_claudesync_path()
    
    if format == 'claude-code':
        content = generate_claude_code_export(base_path)
    else:
        content = generate_raw_export(base_path)
    
    if project:
        output = Path(project) / 'CLAUDESYNC.md'
    
    if output:
        Path(output).write_text(content)
        console.print(f"[green]Written to {output}[/green]")
    else:
        console.print(content)


def generate_claude_code_export(base_path: Path) -> str:
    """Generate the merged export for Claude Code."""
    now = datetime.now().isoformat()
    
    parts = [
        f"<!-- ClaudeSync Export -->",
        f"<!-- Generated: {now} -->",
        f"<!-- Source: {base_path} -->",
        f"<!-- Refresh: Run 'claudesync export claude-code' to update -->",
        "",
        "# User Context",
        "",
    ]
    
    # Identity (condensed)
    identity_path = base_path / 'IDENTITY.md'
    if identity_path.exists():
        identity = identity_path.read_text()
        parts.append("## Identity")
        parts.append("")
        parts.append(condense_content(identity, max_words=500))
        parts.append("")
    
    # Voice (key points only)
    voice_path = base_path / 'VOICE.md'
    if voice_path.exists():
        voice = voice_path.read_text()
        parts.append("## Voice & Communication Style")
        parts.append("")
        parts.append(extract_voice_directives(voice))
        parts.append("")
    
    # Context (full - it's current)
    context_path = base_path / 'CONTEXT.md'
    if context_path.exists():
        context = context_path.read_text()
        parts.append("## Current Context")
        parts.append("")
        parts.append(context)
        parts.append("")
    
    # Memory (recent only)
    memory_path = base_path / 'MEMORY.md'
    if memory_path.exists():
        memory = memory_path.read_text()
        parts.append("## Relevant Memory")
        parts.append("")
        parts.append(filter_recent_memory(memory, days=30, max_entries=20))
        parts.append("")
    
    parts.append("---")
    parts.append("*Context generated by ClaudeSync*")
    
    return "\n".join(parts)
```

---

### 5. `claudesync remember`

**Purpose**: Add a memory entry quickly

**Behavior**:
```bash
$ claudesync remember "Decided to use FastAPI for the new microservice"
Added to MEMORY.md:
[2024-12-19] DECISION HIGH - Decided to use FastAPI for the new microservice

$ claudesync remember --category lesson --confidence medium "AZ legal needs 2 weeks for contract review"
Added to MEMORY.md:
[2024-12-19] LESSON MEDIUM - AZ legal needs 2 weeks for contract review
```

**Implementation**:
```python
@cli.command()
@click.argument('content')
@click.option('--category', '-c', 
              type=click.Choice(['fact', 'decision', 'lesson', 'preference', 'relationship']),
              default='fact')
@click.option('--confidence', 
              type=click.Choice(['high', 'medium', 'low']),
              default='high')
def remember(content, category, confidence):
    """Add a memory entry."""
    memory_path = get_claudesync_path() / 'MEMORY.md'
    
    if not memory_path.exists():
        console.print("[red]MEMORY.md not found. Run 'claudesync init'[/red]")
        return
    
    # Auto-detect category from keywords
    if category == 'fact':
        category = auto_detect_category(content)
    
    date = datetime.now().strftime('%Y-%m-%d')
    entry = f"[{date}] {category.upper()} {confidence.upper()} - {content}"
    
    # Append to MEMORY.md
    with open(memory_path, 'a') as f:
        f.write(f"\n{entry}")
    
    console.print(f"[green]Added to MEMORY.md:[/green]")
    console.print(entry)


def auto_detect_category(content: str) -> str:
    """Infer category from content keywords."""
    content_lower = content.lower()
    
    if any(w in content_lower for w in ['decided', 'chose', 'picked', 'selected', 'going with']):
        return 'decision'
    elif any(w in content_lower for w in ['learned', 'realized', 'discovered', 'found out']):
        return 'lesson'
    elif any(w in content_lower for w in ['prefer', 'like', 'want', 'always', 'never']):
        return 'preference'
    elif any(w in content_lower for w in ['works with', 'reports to', 'manages', 'colleague']):
        return 'relationship'
    
    return 'fact'
```

---

### 6. `claudesync validate`

**Purpose**: Check files for issues

**Behavior**:
```bash
$ claudesync validate
Validating ClaudeSync files...

IDENTITY.md
  ✓ File exists
  ✓ Has required sections (Core, Background)
  ⚠ Missing 'Key Relationships' section

VOICE.md  
  ✓ File exists
  ✓ Has Always/Never sections
  ✗ No examples provided

CONTEXT.md
  ✓ File exists
  ⚠ 'Last Updated' is 14 days ago

MEMORY.md
  ✓ File exists
  ✓ 47 valid entries
  ⚠ 3 entries older than 90 days

Overall: 2 warnings, 1 issue
```

---

## Templates

### templates/IDENTITY.md
```markdown
# Identity

## Core
- **Name**: [Your name]
- **Role**: [Your title/role]
- **Location**: [City, timezone]

## Background

[Your professional background - 2-3 paragraphs that give Claude context about who you are, what you've done, and what shapes how you think]

## Values & Principles

- [Value 1]
- [Value 2]
- [Value 3]

## Key Relationships

- **[Name]**: [Role, context]
```

### templates/VOICE.md
```markdown
# Voice Profile

## Tone
- **Primary**: [e.g., Direct, warm, analytical]
- **Humor**: [When and how]

## Always
- [Directive 1]
- [Directive 2]

## Never
- [Anti-pattern 1]
- [Anti-pattern 2]

## Formatting Preferences
- [Preference 1]
- [Preference 2]

## Examples

### Email style:
[Example]

### Technical explanation:
[Example]
```

### templates/CONTEXT.md
```markdown
# Working Context

**Last Updated**: YYYY-MM-DD

## Current Focus

[What's top of mind right now?]

## Active Projects

### [Project 1]
- **Status**: Active
- **Key context**: [What Claude needs to know]

## This Week
- [Priority 1]
- [Priority 2]
```

### templates/MEMORY.md
```markdown
# Memory

Entries format: `[DATE] CATEGORY CONFIDENCE - Content`

Categories: FACT, DECISION, LESSON, PREFERENCE, RELATIONSHIP
Confidence: HIGH, MEDIUM, LOW

---

## Entries

```

### templates/config.yaml
```yaml
# ClaudeSync Configuration

version: 1

paths:
  base: ~/.claudesync

sync:
  # Days before context is considered stale
  stale_threshold: 14
  
  # Days before memory entries are candidates for decay
  decay_threshold: 90

export:
  # Max words for identity section in exports
  identity_max_words: 500
  
  # Days of memory to include in exports
  memory_days: 30
  memory_max_entries: 20
```

---

## Testing

### test_cli.py
```python
import pytest
from click.testing import CliRunner
from claudesync.cli import cli
from pathlib import Path
import tempfile

@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    """Use temp directory as home."""
    monkeypatch.setenv('HOME', str(tmp_path))
    return tmp_path

def test_init_creates_structure(temp_home):
    runner = CliRunner()
    result = runner.invoke(cli, ['init'])
    
    assert result.exit_code == 0
    assert (temp_home / '.claudesync').exists()
    assert (temp_home / '.claudesync' / 'IDENTITY.md').exists()
    assert (temp_home / '.claudesync' / 'VOICE.md').exists()

def test_init_no_overwrite(temp_home):
    runner = CliRunner()
    
    # First init
    runner.invoke(cli, ['init'])
    
    # Modify a file
    identity = temp_home / '.claudesync' / 'IDENTITY.md'
    identity.write_text('Custom content')
    
    # Second init (should not overwrite)
    runner.invoke(cli, ['init'], input='y\n')
    
    assert identity.read_text() == 'Custom content'

def test_remember_adds_entry(temp_home):
    runner = CliRunner()
    runner.invoke(cli, ['init'])
    
    result = runner.invoke(cli, ['remember', 'Test memory entry'])
    
    assert result.exit_code == 0
    memory = (temp_home / '.claudesync' / 'MEMORY.md').read_text()
    assert 'Test memory entry' in memory

def test_export_claude_code(temp_home):
    runner = CliRunner()
    runner.invoke(cli, ['init'])
    
    result = runner.invoke(cli, ['export', 'claude-code'])
    
    assert result.exit_code == 0
    assert 'ClaudeSync Export' in result.output
```

---

## Development Commands

```bash
# Setup dev environment
cd claudesync
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run CLI locally
claudesync --help

# Build package
pip install build
python -m build
```

---

## Phase 1 Completion Criteria

- [ ] `claudesync init` creates directory structure with templates
- [ ] `claudesync edit <file>` opens correct file in $EDITOR
- [ ] `claudesync status` shows file status and summary
- [ ] `claudesync export claude-code` generates merged context
- [ ] `claudesync remember` adds timestamped memory entries
- [ ] `claudesync validate` checks file structure and content
- [ ] All templates are populated with useful starting content
- [ ] Basic test coverage for CLI commands
- [ ] README with installation and usage instructions

---

## Next: Phase 2 Preview

After Phase 1 is complete:

1. **Voice Analysis**: `claudesync voice analyze` - parse writing samples
2. **Decay Management**: `claudesync decay` - clean old memories
3. **Web Sync**: `claudesync sync web` - generate Claude.ai memory updates
4. **Project Integration**: Better Claude Code workflow with auto-refresh
