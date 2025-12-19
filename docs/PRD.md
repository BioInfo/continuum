# ClaudeSync: Unified Memory & Voice System

## Product Requirements Document

**Author:** Justin  
**Version:** 1.0  
**Date:** December 2024  
**Status:** Draft for Claude Code Execution

---

## Executive Summary

ClaudeSync is a personal context management system that creates a unified identity, voice, and memory layer across all Claude interfaces (Claude.ai web/desktop, Claude Code, API). The core insight is that **you** should own and control your context, not have it siloed in platform-specific implementations.

This isn't just about remembering facts—it's about encoding how you think, communicate, and work so that every Claude interaction feels like a continuation of a long-term collaboration.

---

## Problem Statement

### Current State Pain Points

1. **Siloed Memory**: Claude.ai's memory system extracts what *it* thinks is important. Claude Code uses CLAUDE.md files that are project-local. API has no persistence. None of these talk to each other.

2. **Voice Loss**: Every new session starts with Claude's default voice. You repeatedly have to correct tone, formatting preferences, and communication style.

3. **Context Amnesia**: Complex projects spanning web research (Claude.ai) and implementation (Claude Code) lose continuity. You become the integration layer, re-explaining context constantly.

4. **Passive Extraction**: You have no control over what gets remembered. The system decides; you react.

5. **No Portability**: If you switch interfaces or start fresh, you lose everything.

### The Deeper Problem

The current paradigm treats memory as a feature of the *platform*. But memory and identity are properties of the *relationship*. You should be able to carry your context anywhere Claude exists.

---

## Vision

**One sentence:** A portable, user-controlled context system that makes every Claude feel like *your* Claude.

**Success looks like:**
- Start a Claude Code session → it already knows your voice, current projects, preferences
- Ask Claude.ai a question → it has context from your coding sessions
- Voice and style are consistent across all interfaces
- You curate what matters; noise decays naturally
- Your context is versioned, portable, and yours

---

## First Principles Architecture

### What Constitutes "Context"?

Drawing from cognitive science, we model context as four distinct layers:

```
┌─────────────────────────────────────────────────┐
│                  IDENTITY                        │
│   Who you are. Stable over years.               │
│   Name, role, background, values, style         │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│                   VOICE                          │
│   How you communicate. Stable over months.      │
│   Tone, vocabulary, anti-patterns, examples     │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│               WORKING CONTEXT                    │
│   What you're focused on. Changes weekly.       │
│   Current projects, priorities, relationships   │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              EPISODIC MEMORY                     │
│   What happened. Accumulates over time.         │
│   Decisions made, lessons learned, history      │
└─────────────────────────────────────────────────┘
```

### Design Principles

1. **Files as Source of Truth**: Plain text/markdown files you control, version, and can read
2. **Graceful Degradation**: Works even if only partially available
3. **Active Curation Over Passive Extraction**: You decide what matters
4. **Voice is First-Class**: Not an afterthought—explicit encoding of communication style
5. **Temporal Awareness**: Context has freshness; old things can decay
6. **Composable**: Project context extends base identity, doesn't replace it

---

## System Architecture

### Directory Structure

```
~/.claudesync/
├── IDENTITY.md           # Core identity - who you are
├── VOICE.md              # Communication style encoding
├── CONTEXT.md            # Current working context
├── MEMORY.md             # Accumulated episodic memory
├── config.yaml           # System configuration
├── sync/
│   ├── web-export.md     # Last sync to Claude.ai memory
│   └── changelog.md      # What changed and when
└── voice-samples/
    ├── writing/          # Examples of your writing
    ├── code-reviews/     # How you give feedback
    └── emails/           # Communication samples
```

### File Specifications

#### IDENTITY.md
```markdown
# Identity

## Core
- **Name**: [Full name]
- **Role**: [Title, organization]
- **Location**: [Timezone-relevant]

## Background
[2-3 paragraphs of relevant professional/personal background]

## Values & Principles
[What matters to you in work and communication]

## Key Relationships
[People you frequently reference or work with]
```

#### VOICE.md
```markdown
# Voice Profile

## Tone
- **Primary**: [e.g., Direct, warm, technical]
- **Register**: [e.g., Professional but not corporate]
- **Humor**: [e.g., Dry wit, self-deprecating, contextual]

## Preferences
### Always
- [Things to always do: be direct, use examples, etc.]

### Never
- [Anti-patterns: no corporate speak, no excessive hedging, etc.]

## Vocabulary
### Prefer
- [Words/phrases you like]

### Avoid
- [Words/phrases that feel wrong]

## Examples
[Links to voice-samples/ directory or inline examples]

### How I write emails:
[Example]

### How I explain technical concepts:
[Example]

### How I give feedback:
[Example]
```

#### CONTEXT.md
```markdown
# Working Context

**Last Updated**: [ISO date]

## Current Focus
[What's top-of-mind this week/month]

## Active Projects
### [Project 1]
- Status: [Active/Blocked/Wrapping up]
- Key context: [What Claude needs to know]
- Related files: [Links to project CLAUDE.md if applicable]

### [Project 2]
...

## Upcoming
[What's coming that Claude should be aware of]

## Recently Completed
[Context that might still be relevant]
```

#### MEMORY.md
```markdown
# Memory

## Format
Each entry: `[DATE] [CATEGORY] [CONFIDENCE] - Content`

Categories: FACT, DECISION, LESSON, PREFERENCE, RELATIONSHIP
Confidence: HIGH (verified), MEDIUM (inferred), LOW (uncertain)

---

## Entries

[2024-12-19] DECISION HIGH - Chose React over Vue for Navari dashboard because...
[2024-12-15] LESSON HIGH - Learned that AZ legal requires 2-week review for...
[2024-12-10] PREFERENCE MEDIUM - Prefers morning meetings before 10am ET
```

---

## CLI Tool Specification

### Commands

```bash
# Initialize a new ClaudeSync directory
claudesync init

# Open interactive editor for a specific file
claudesync edit identity|voice|context|memory

# Add a memory entry
claudesync remember "Decided to use FastAPI for the microservice"

# Capture voice sample from clipboard or file
claudesync voice capture [--from clipboard|file] [--type email|writing|feedback]

# Analyze your writing to extract voice patterns
claudesync voice analyze [file or directory]

# Generate a merged context file for Claude Code
claudesync export claude-code [--project path]

# Sync to Claude.ai memory (generates commands/suggestions)
claudesync sync web

# Show what's changed since last sync
claudesync diff

# Decay old memories (interactive cleanup)
claudesync decay [--older-than 90d]

# Validate all files
claudesync validate

# Show current context summary
claudesync status
```

### Export Formats

#### For Claude Code (CLAUDE.md injection)
```markdown
<!-- BEGIN CLAUDESYNC IMPORT -->
<!-- Source: ~/.claudesync | Generated: 2024-12-19T10:30:00Z -->

## Identity
[Condensed from IDENTITY.md]

## Voice
[Key points from VOICE.md]

## Current Context
[From CONTEXT.md]

## Relevant Memory
[Filtered, recent entries from MEMORY.md]

<!-- END CLAUDESYNC IMPORT -->
```

#### For Claude.ai Web (Memory sync suggestions)
```
Suggested memory updates for Claude.ai:

ADD: "User prefers direct communication without corporate language"
ADD: "User is currently focused on Navari framework production deployment"
UPDATE: "User's team size" → "80 people across 7 global locations"
REMOVE: "User is exploring DGX purchase" (completed)
```

---

## Voice Analysis Engine

The hardest problem: how do you encode "voice" computationally?

### Approach: Multi-Signal Extraction

```
┌─────────────────────────────────────────────────┐
│            INPUT: Writing Samples               │
│     Emails, docs, code reviews, messages        │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           SIGNAL EXTRACTION                     │
│                                                 │
│  • Sentence length distribution                 │
│  • Question frequency                           │
│  • Hedge word usage (maybe, perhaps, might)     │
│  • Direct vs. passive constructions             │
│  • Technical depth markers                      │
│  • Humor/wit patterns                           │
│  • Opening/closing patterns                     │
│  • Vocabulary fingerprint                       │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           PATTERN SYNTHESIS                     │
│                                                 │
│  Use Claude to:                                 │
│  1. Analyze samples against signals             │
│  2. Generate "always/never" rules              │
│  3. Create style guide                          │
│  4. Identify distinctive patterns               │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              OUTPUT: VOICE.md                   │
│    Structured encoding of communication style   │
└─────────────────────────────────────────────────┘
```

### Voice Signals to Extract

| Signal | What it captures | How to measure |
|--------|------------------|----------------|
| Directness | How quickly you get to the point | Words before main verb, hedge frequency |
| Formality | Register level | Contraction usage, vocabulary complexity |
| Technical depth | Default explanation level | Jargon density, assumed knowledge |
| Warmth | Emotional connection | Personal pronouns, acknowledgments |
| Humor style | When and how wit appears | Pattern matching, context analysis |
| Structure preference | How you organize thoughts | Headers, bullets, paragraphs |

---

## Implementation Phases

### Phase 1: Foundation (This Session)
- [ ] Create directory structure and file templates
- [ ] Implement `claudesync init`
- [ ] Implement `claudesync edit`
- [ ] Implement `claudesync export claude-code`
- [ ] Populate initial files from existing Claude.ai memory

### Phase 2: Memory Management
- [ ] Implement `claudesync remember`
- [ ] Implement `claudesync decay`
- [ ] Add temporal awareness to MEMORY.md
- [ ] Build memory search/filter

### Phase 3: Voice Capture
- [ ] Implement `claudesync voice capture`
- [ ] Build voice analysis prompts
- [ ] Implement `claudesync voice analyze`
- [ ] Create voice-sample workflows

### Phase 4: Sync & Integration
- [ ] Implement `claudesync sync web`
- [ ] Build Claude Code integration hooks
- [ ] Create bidirectional sync logic
- [ ] Add conflict resolution

### Phase 5: Intelligence Layer
- [ ] Auto-suggest memories from conversations
- [ ] Voice drift detection
- [ ] Context relevance scoring
- [ ] Smart decay algorithms

---

## Technical Requirements

### Language & Runtime
- **Primary**: Python 3.11+ (works everywhere Claude Code does)
- **Package manager**: pip with pyproject.toml
- **No heavy dependencies**: Keep it lightweight and fast

### Dependencies (Minimal)
```
click>=8.0          # CLI framework
pyyaml>=6.0         # Config parsing
rich>=13.0          # Terminal formatting
python-dateutil     # Date handling
```

### File Format Decisions
- **All content files**: Markdown (human-readable, Claude-native)
- **Config**: YAML (structured but readable)
- **No database**: Files are the database (git-friendly)

### Cross-Platform
- macOS (primary)
- Linux
- Windows (WSL recommended)

---

## Integration Points

### Claude Code
```markdown
# In project's CLAUDE.md:

@import ~/.claudesync/IDENTITY.md
@import ~/.claudesync/VOICE.md
@import ~/.claudesync/CONTEXT.md

# Or use generated export:
@import ~/.claudesync/exports/claude-code.md
```

Note: Claude Code doesn't support `@import` natively—the CLI will generate a merged file that you reference or copy.

### Claude.ai Web
Two approaches:

1. **Manual sync**: CLI generates suggested memory updates, you apply them
2. **Drive-based**: Store exports in Google Drive, reference via Drive integration

### API / Custom Apps
```python
from claudesync import load_context

context = load_context()
system_prompt = f"""
{context.identity}
{context.voice}
{context.current_context}

User's relevant memory:
{context.memory.recent(days=30)}
"""
```

---

## Success Metrics

### Quantitative
- Time to context (how fast Claude "gets" you in new sessions)
- Correction frequency (how often you fix voice/style issues)
- Memory accuracy (are recalled facts correct?)

### Qualitative
- "Claude sounds like it knows me"
- "I don't have to re-explain my preferences"
- "Switching between web and Code feels seamless"

---

## Open Questions

1. **Sync conflict resolution**: What happens when Claude.ai memory and local files diverge?
2. **Privacy/security**: Some context is sensitive. Encryption? Selective sync?
3. **Multi-project context**: How to handle project-specific overrides elegantly?
4. **Voice evolution**: How do we detect and adapt to voice drift over time?
5. **Sharing**: Could teams share partial context (org voice guidelines)?

---

## Appendix: Quick Start After Build

```bash
# Install
pip install claudesync

# Initialize
claudesync init

# Populate from what we know
claudesync edit identity  # Opens $EDITOR

# Generate Claude Code context
claudesync export claude-code --output ~/projects/navari/CONTEXT.md

# Add to your project's CLAUDE.md
echo "See CONTEXT.md for user context" >> ~/projects/navari/CLAUDE.md
```

---

## Next Steps

1. Review this PRD
2. Start Phase 1 implementation in Claude Code
3. Populate initial files from existing context
4. Test round-trip: edit → export → use in Claude Code → verify voice
