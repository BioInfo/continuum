# Continuum MVP Specification

**Author:** Justin + Claude
**Date:** December 2024
**Status:** Ready for implementation

---

## What's the MVP?

The smallest thing that delivers real value: **Context export for Claude Code that actually works.**

Not sync. Not MCP. Not voice analysis. Just this:

1. A place to store your context (files you can edit)
2. A way to export it for Claude Code (merged, formatted)
3. A way to add memories quickly (CLI command)

If that's useful, everything else follows. If that's not useful, nothing else matters.

---

## MVP Scope

### In Scope

- `continuum init` - Create ~/.continuum with templates
- `continuum edit` - Open files in $EDITOR
- `continuum status` - Show what exists and when it was updated
- `continuum remember` - Add memory entry with timestamp
- `continuum export` - Generate CLAUDE.md for Claude Code

### Out of Scope (Phase 2+)

- MCP server
- Voice analysis
- Project-specific context
- Semantic memory search
- Decay management
- Claude.ai sync/reconciliation
- Voice drift detection

---

## Technical Spec

### Project Structure

```
continuum/
├── pyproject.toml
├── README.md
├── src/
│   └── continuum/
│       ├── __init__.py
│       ├── cli.py              # Click CLI
│       ├── config.py           # Config loading
│       ├── files.py            # File operations
│       ├── export.py           # Export generation
│       └── templates/          # Default templates
│           ├── identity.md
│           ├── voice.md
│           ├── context.md
│           └── memory.md
└── tests/
    ├── test_cli.py
    └── test_export.py
```

### Dependencies (Minimal)

```toml
[project]
name = "continuum"
version = "0.1.0"
description = "Portable context for Claude"
requires-python = ">=3.11"
dependencies = [
    "click>=8.0",
    "rich>=13.0",
    "pyyaml>=6.0",
]

[project.scripts]
continuum = "continuum.cli:cli"
ct = "continuum.cli:cli"  # alias
```

### Data Directory

```
~/.continuum/
├── identity.md         # Who you are
├── voice.md           # How you communicate (with examples inline for MVP)
├── context.md         # Current working context
├── memory.md          # Accumulated memories
├── config.yaml        # Optional configuration
└── exports/           # Generated exports
    └── claude-code.md
```

For MVP, voice examples stay inline in voice.md rather than separate files. Simpler to implement and edit.

---

## Command Specifications

### `continuum init`

**Purpose:** Create ~/.continuum with template files.

**Behavior:**
```bash
$ continuum init
Creating ~/.continuum/...
  Created identity.md
  Created voice.md
  Created context.md
  Created memory.md
  Created config.yaml

Next steps:
  1. Run 'continuum edit identity' to add your information
  2. Run 'continuum edit voice' to define your communication style
  3. Run 'continuum export' to generate context for Claude Code
```

**Options:**
- `--path <path>` - Custom location (default: ~/.continuum)
- `--force` - Overwrite existing files

**Logic:**
1. Check if directory exists
2. Create directory and subdirectories
3. Copy templates (skip existing unless --force)
4. Print summary and next steps

### `continuum edit <file>`

**Purpose:** Open a context file in $EDITOR.

**Behavior:**
```bash
$ continuum edit identity
# Opens ~/.continuum/identity.md in $EDITOR

$ continuum edit voice
# Opens ~/.continuum/voice.md in $EDITOR
```

**Arguments:**
- `file` - One of: identity, voice, context, memory

**Logic:**
1. Map file name to path
2. Check file exists (suggest init if not)
3. Open in $EDITOR (fallback: nano)
4. After close, optionally show "Updated: {path}"

### `continuum status`

**Purpose:** Show current context state.

**Behavior:**
```bash
$ continuum status
╭─────────────────── Continuum Status ───────────────────╮
│ Location: ~/.continuum                                  │
├─────────────────────────────────────────────────────────┤
│ identity.md    ✓  Updated 3 days ago                   │
│ voice.md       ✓  Updated 1 week ago                   │
│ context.md     ⚠  Updated 15 days ago (stale?)        │
│ memory.md      ✓  23 entries                           │
├─────────────────────────────────────────────────────────┤
│ Current focus: Navari production deployment            │
│ Last export: 2024-12-18                                │
╰─────────────────────────────────────────────────────────╯
```

**Logic:**
1. Check each file exists and get mtime
2. Parse memory.md to count entries
3. Extract current focus from context.md
4. Check exports/ for last export
5. Render with Rich panel/table

### `continuum remember <text>`

**Purpose:** Add a timestamped memory entry.

**Behavior:**
```bash
$ continuum remember "Decided to use FastAPI for the microservice"
Added to memory.md:
[2024-12-19] DECISION - Decided to use FastAPI for the microservice

$ continuum remember "Team standup moved to 10am" --category fact
Added to memory.md:
[2024-12-19] FACT - Team standup moved to 10am
```

**Arguments:**
- `text` - The memory content (required)

**Options:**
- `--category` / `-c` - One of: fact, decision, lesson, preference (default: auto-detect)

**Logic:**
1. Auto-detect category from keywords if not specified
2. Format entry: `[{date}] {CATEGORY} - {text}`
3. Append to memory.md
4. Print confirmation

**Auto-detection:**
- Contains "decided", "chose", "going with" → DECISION
- Contains "learned", "realized", "discovered" → LESSON
- Contains "prefer", "always", "never" → PREFERENCE
- Otherwise → FACT

### `continuum export`

**Purpose:** Generate merged context file for Claude Code.

**Behavior:**
```bash
$ continuum export
Exported to ~/.continuum/exports/claude-code.md
Copy this to your project's CLAUDE.md or reference it directly.

$ continuum export --output ./CONTEXT.md
Exported to ./CONTEXT.md

$ continuum export --stdout
# Prints to stdout instead of file
```

**Options:**
- `--output` / `-o` - Output path (default: ~/.continuum/exports/claude-code.md)
- `--stdout` - Print to stdout instead of file

**Logic:**
1. Load all source files
2. Condense identity (first ~500 words or key sections)
3. Include voice in full
4. Include context in full
5. Filter memory to recent entries (last 30 days or last 20, whichever is more)
6. Render using template
7. Write to output

**Output Format:**
```markdown
<!-- Continuum Export -->
<!-- Generated: 2024-12-19T10:30:00-05:00 -->
<!-- Source: ~/.continuum -->
<!-- Refresh: continuum export -->

# User Context

## Identity

[Condensed identity content]

## Voice & Communication Style

[Voice content including examples]

## Current Context

[Context content]

## Relevant Memory

[Recent memory entries]

---
*Generated by Continuum*
```

---

## Template Content

### templates/identity.md

```markdown
# Identity

## Core
- **Name**: [Your name]
- **Role**: [Your title/role]
- **Location**: [City, timezone]

## Background

[2-3 paragraphs about your professional background, what shapes how you work, and what you bring to collaborations.]

## Values

- [Value 1]
- [Value 2]
- [Value 3]

## Key Relationships

- **[Name]**: [Role, context for why they matter]
```

### templates/voice.md

```markdown
# Voice Profile

## Tone
- **Primary**: [e.g., Direct, warm, analytical]
- **Humor**: [When and how wit appears, if at all]

## Do
- [Directive 1: e.g., "Lead with the answer"]
- [Directive 2: e.g., "Use concrete examples"]
- [Directive 3]

## Don't
- [Anti-pattern 1: e.g., "Corporate jargon"]
- [Anti-pattern 2: e.g., "Excessive hedging"]
- [Anti-pattern 3]

## Formatting
- [Preference 1: e.g., "Short paragraphs"]
- [Preference 2: e.g., "Code examples when relevant"]

## Examples

### Email (internal):
[Paste a representative example of how you write internal emails]

### Technical explanation:
[Paste an example of how you explain technical concepts]

### Feedback:
[Paste an example of how you give feedback]
```

### templates/context.md

```markdown
# Working Context

**Last Updated**: [Today's date]

## Current Focus

[1-2 sentences: What's the main thing on your mind right now?]

## Active Projects

### [Project Name]
- **Status**: [Active / Planning / Wrapping up]
- **Key context**: [What Claude needs to know]
- **Next milestone**: [What's coming]

## This Week

- [Priority 1]
- [Priority 2]
- [Priority 3]

## Recently Completed

- [Recent completion that might still be relevant]
```

### templates/memory.md

```markdown
# Memory

Format: `[DATE] CATEGORY - Content`
Categories: FACT, DECISION, LESSON, PREFERENCE

---

## Entries

```

### templates/config.yaml

```yaml
# Continuum Configuration
version: 1

# Thresholds
stale_days: 14           # Days before context is marked stale
memory_recent_days: 30   # Days of memory to include in exports
memory_max_entries: 20   # Max memory entries in exports

# Export settings
identity_max_words: 500  # Condense identity to this length
```

---

## Implementation Order

### Day 1: Setup

1. Create project structure
2. Set up pyproject.toml
3. Implement config loading
4. Create template files
5. Basic test setup

### Day 2: Core Commands

1. Implement `continuum init`
2. Implement `continuum edit`
3. Implement `continuum status`
4. Tests for init/edit/status

### Day 3: Remember & Export

1. Implement `continuum remember`
2. Implement `continuum export`
3. Export template and composition logic
4. Tests for remember/export

### Day 4: Polish

1. Rich formatting for status
2. Error handling and edge cases
3. Help text and documentation
4. End-to-end testing

### Day 5: Ship

1. README with usage examples
2. Test on fresh environment
3. Build and publish to PyPI (or just pip install from git)
4. Populate with actual context and test with Claude Code

---

## Success Criteria

MVP is successful if:

1. **Installs cleanly**: `pip install continuum` works
2. **Init creates usable templates**: You can fill them in and they make sense
3. **Export generates valid context**: Claude Code can use the output
4. **Remember is faster than editing**: Quick CLI entry beats opening a file
5. **Status shows what matters**: At a glance, you know what's current

Validation: Use it for a week. Does Claude Code feel more "you"?

---

## What's NOT in MVP (Explicitly)

To keep scope tight:

- **No YAML frontmatter**: Plain markdown for memory entries (add in v0.2)
- **No project support**: Global context only (add in v0.2)
- **No MCP server**: Static export only (add in v0.3)
- **No voice analysis**: Manual voice profile (add in v0.3)
- **No semantic search**: Text search or none (add in v0.4)
- **No decay management**: Manual cleanup (add in v0.2)

These are all good features. They're just not MVP.

---

## Seed Data

After building, populate with Justin's actual context from SEED_FILES.md. This transforms MVP from "demo" to "useful tool."

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Export too long for context window | Condense identity, limit memory entries |
| Voice profile doesn't transfer well | Include concrete examples, not just rules |
| Edit workflow too friction-y | Make templates good enough to start |
| Status too simple to be useful | Include current focus, stale warnings |
| Remember too manual | Auto-detect category, simple syntax |

---

## Post-MVP Priorities

After MVP ships and is validated:

1. **YAML frontmatter for memories** - Enables filtering, decay, scope
2. **Project support** - Compose global + project context
3. **Decay command** - Surface old memories for review
4. **Voice examples as files** - Better organization
5. **MCP server** - Live context queries

---

## Let's Build It

The MVP is intentionally constrained. It answers one question: **Does having portable context make Claude Code better?**

If yes, we have a foundation to build on.
If no, we learned something without over-investing.

Start with `continuum init`.
