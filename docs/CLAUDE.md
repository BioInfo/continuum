# CLAUDE.md - ClaudeSync Project

## What This Is

ClaudeSync is a CLI tool for managing unified context/memory across Claude interfaces (claude.ai, Claude Code, API). The goal is user-controlled, portable context that makes every Claude feel like *your* Claude.

## Project Status

**Phase 1: Foundation** - Ready to build

## Key Files

- `PRD.md` - Full product requirements document
- `SUPPLEMENT.md` - Philosophy, SOPs, non-development content  
- `IMPLEMENTATION.md` - Technical spec for Phase 1 (start here for coding)
- `SEED_FILES.md` - Pre-populated context for the user to start with

## Tech Stack

- Python 3.11+
- Click (CLI framework)
- Rich (terminal formatting)
- PyYAML (config)
- No database - files are the store

## Project Structure to Build

```
claudesync/
├── pyproject.toml
├── README.md
├── src/
│   └── claudesync/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── files.py
│       ├── export.py
│       └── templates/
└── tests/
```

## Phase 1 Commands to Implement

1. `claudesync init` - Create ~/.claudesync with templates
2. `claudesync edit <file>` - Open context file in $EDITOR
3. `claudesync status` - Show summary dashboard
4. `claudesync export claude-code` - Generate merged context
5. `claudesync remember <text>` - Add memory entry
6. `claudesync validate` - Check file integrity

## Voice Notes for Working With Justin

- Direct, no fluff
- Technically sharp - don't over-explain basics
- Ship working code > perfect architecture
- Prefers prose over excessive bullet points
- Appreciates dry humor when appropriate
- Skip corporate language entirely

## When Building

1. Start with `IMPLEMENTATION.md` - it has the full spec
2. Build iteratively - get `init` working, then `status`, etc.
3. Use Rich for nice terminal output
4. Keep dependencies minimal
5. Write tests as you go
