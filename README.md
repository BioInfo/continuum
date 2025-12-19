# Continuum

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**Portable context for Claude. Own your memory, voice, and identity across all Claude interfaces.**

Continuum gives you a single source of truth for your context that works with Claude Code, Claude.ai, Claude Desktop, and the API. Your identity, voice, working context, and memories live in simple markdown files that you control.

## Why Continuum?

Every Claude session starts fresh. You re-explain your role, re-establish your communication style, re-provide context. Claude.ai has memory, but it's siloed and opaque. Claude Code has CLAUDE.md, but it's project-local. None of them talk to each other.

Continuum solves this by giving you:

- **Identity**: Who you are (stable over years)
- **Voice**: How you communicate (stable over months)
- **Context**: What you're working on (changes weekly)
- **Memory**: What you've learned (accumulates over time)
- **Project overlays**: Per-project context that merges with your global context
- **MCP server**: Live integration with Claude.ai and Claude Desktop via Tailscale

## Installation

```bash
# With pip
pip install continuum-context

# With uv
uv pip install continuum-context

# From source
git clone https://github.com/justinjohnson/continuum.git
cd continuum
pip install -e .
```

## Quick Start

```bash
# Initialize your context directory
continuum init

# Edit your identity and voice
continuum edit identity
continuum edit voice

# Check status
continuum status

# Export for Claude Code
continuum export
```

## Features

### Core Context Management

```bash
continuum init                    # Create ~/.continuum with templates
continuum edit identity           # Edit who you are
continuum edit voice              # Edit communication style
continuum edit context            # Edit current working context
continuum edit memory             # Edit accumulated memories
continuum status                  # Show context status
continuum validate                # Check for issues
continuum export                  # Generate merged context file
```

### Memory System

```bash
# Add memories (category auto-detected)
continuum remember "Decided to use FastAPI for the microservice"
# → [2024-12-19] DECISION - Decided to use FastAPI for the microservice

continuum remember "Team standup moved to 10am" --category fact
# → [2024-12-19] FACT - Team standup moved to 10am
```

### Project-Specific Context

```bash
# Initialize project context in current directory
continuum init --project

# Edit project-specific files
continuum edit context --project
continuum edit memory --project

# Add project memories
continuum remember "Architecture: event-driven with Kafka" --project

# Status shows both global and project context
continuum status
```

Project context merges with global context on export. Context and memories append; identity and voice can override.

### Voice Analysis

Analyze your writing samples to generate a voice profile:

```bash
# Add samples to ~/.continuum/samples/
mkdir -p ~/.continuum/samples/emails
# Copy your writing examples there

# Set your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-..." > ~/.continuum/.env

# Analyze and generate voice.md
continuum voice analyze

# Preview without updating
continuum voice analyze --dry-run
```

### MCP Server

Continuum includes an MCP server that exposes your context to Claude.ai, Claude Desktop, and Claude Code.

**For Claude Code (local, stdio):**

```bash
# Get config to add to ~/.claude/.mcp.json
continuum serve config
```

**For Claude.ai / Claude Desktop (remote, SSE via Tailscale):**

```bash
# Start the server (runs on port 8765)
continuum serve sse

# Enable Tailscale Funnel for HTTPS
tailscale funnel --bg 8765

# Get config
continuum serve config --sse
```

Add to Claude.ai: Settings → Connectors → Add custom connector

**MCP Tools:**

| Tool | Description |
|------|-------------|
| `get_context` | Full merged context (identity + voice + context + memory) |
| `get_identity` | Identity information |
| `get_voice` | Voice/style guide |
| `get_current_context` | Current working context |
| `get_memories` | Search memories by category or text |
| `remember` | Save new memory from conversation |
| `get_status` | Continuum status check |

## Directory Structure

```
~/.continuum/                    # Global context
├── identity.md                  # Who you are
├── voice.md                     # How you communicate
├── context.md                   # Current working context
├── memory.md                    # Accumulated memories
├── config.yaml                  # Configuration
├── samples/                     # Writing samples for voice analysis
└── exports/                     # Generated exports

~/project/.continuum/            # Project context (optional)
├── context.md                   # Project-specific context
└── memory.md                    # Project-specific memories
```

## Configuration

Edit `~/.continuum/config.yaml`:

```yaml
# Days before a file is marked stale
stale_days: 14

# Memory filtering for exports
memory_recent_days: 30
memory_max_entries: 20

# Identity condensing for exports
identity_max_words: 500
```

## Philosophy

1. **You own your context.** Not platforms, not providers. You.
2. **Files are the interface.** Human-readable, git-friendly, editable with any tool.
3. **Voice matters.** It's not just what you know—it's how you communicate.
4. **Active curation beats passive extraction.** You decide what's important.

## Roadmap

- [x] Core CLI (init, edit, status, remember, export, validate)
- [x] Voice analysis from writing samples
- [x] Project-specific context overlays
- [x] MCP server for Claude.ai / Claude Desktop integration
- [ ] Semantic memory search
- [ ] Voice drift detection
- [ ] Claude Code native integration

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

**Justin Johnson** - [Run Data Run](https://rundatarun.com)

---

*Built for people who want to own their AI context, not rent it.*
