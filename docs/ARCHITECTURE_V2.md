# Continuum: Architecture v2

**Author:** Justin + Claude
**Date:** December 2024
**Status:** Revised architecture based on refinement analysis

---

## Name Decision

**Continuum** — context that flows with you.

The name captures the core value: continuity across interfaces, sessions, and time. It's not "sync" (which overpromises). It's not generic (like "context"). It evokes what you actually experience: Claude that remembers, adapts, and feels continuous.

CLI: `continuum` (alias: `ct`)

---

## System Architecture

### High-Level View

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTINUUM                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   CONTEXT STORE                          │   │
│  │                   ~/.continuum/                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ identity │ │  voice/  │ │ context  │ │ memory/  │   │   │
│  │  │   .md    │ │ examples │ │   .md    │ │ entries  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  │                      │                                    │   │
│  │            ┌─────────┴─────────┐                         │   │
│  │            │  projects/        │                         │   │
│  │            │  ├── navari/      │                         │   │
│  │            │  ├── axon/        │                         │   │
│  │            │  └── ...          │                         │   │
│  │            └───────────────────┘                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     CLI      │  │  MCP Server  │  │  Python API  │          │
│  │  (primary)   │  │  (phase 2)   │  │  (library)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  Static  │      │  Claude  │      │  Custom  │
    │  Export  │      │   Code   │      │  Agents  │
    │(CLAUDE.md)│     │via MCP   │      │  & Apps  │
    └──────────┘      └──────────┘      └──────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │Claude.ai │      │ Claude   │      │  Claude  │
    │(manual)  │      │  Code    │      │   API    │
    └──────────┘      └──────────┘      └──────────┘
```

### Core Principles (Revised)

1. **Files as source of truth** — Human-readable, git-friendly, no database
2. **YAML frontmatter + Markdown body** — Structured metadata, prose content
3. **Examples over descriptions** — Voice is demonstrated, not documented
4. **Local wins, but show divergence** — You curate; system surfaces conflicts
5. **Agent-native design** — Context can be queried and updated programmatically
6. **Compose at export time** — Simple storage, smart assembly

---

## Directory Structure

```
~/.continuum/
├── identity.md                    # Who you are (stable)
├── voice/                         # How you communicate
│   ├── profile.md                # Directives and metadata
│   └── examples/                 # First-class voice demonstrations
│       ├── email-internal.md
│       ├── email-external.md
│       ├── technical-peer.md
│       ├── technical-beginner.md
│       ├── feedback.md
│       └── casual.md
├── context.md                     # Current working context
├── memory/                        # Accumulated knowledge
│   ├── index.md                  # Memory metadata and stats
│   └── entries/                  # Individual memories (YAML frontmatter)
│       ├── 2024-12-19-fastapi-decision.md
│       ├── 2024-12-18-navari-timeline.md
│       └── ...
├── projects/                      # Project-specific context
│   ├── navari/
│   │   ├── context.md           # Project context (extends global)
│   │   ├── voice.md             # Voice overrides (optional)
│   │   └── memory/              # Project-scoped memories
│   └── axon/
│       └── context.md
├── config.yaml                    # System configuration
├── exports/                       # Generated exports
│   └── claude-code.md
└── sync/                          # Sync state tracking
    ├── last-export.yaml
    └── changelog.md
```

---

## File Formats

### identity.md (Pure Markdown, Optional Frontmatter)

```markdown
---
version: 1
updated: 2024-12-19
---

# Identity

## Core
- **Name**: Justin
- **Role**: Executive Director, Oncology Data Science at AstraZeneca
- **Location**: US East Coast (ET timezone)

## Background

I lead ODSP, an 80-person team across seven global locations. I serve as Head of Agents, Foundation Models, Data Strategy, and all Data Science/AI platforms for Oncology R&D.

My career arc: genomics at TIGR/Venter Institute (2000s) → EdgeBio (2010s) → AstraZeneca. I've built distributed computing systems, trained foundation models, shipped hundreds of data science projects.

I'm deeply technical but operate at strategic level. I write at rundatarun.io (10,000+ followers). I've built a DGX Spark personal AI lab.

## Values

- Authenticity over corporate polish
- Ship and iterate over perfect plans
- Technical depth matters at leadership level
- Direct communication respects everyone's time

## Key Relationships

- **Jorge**: Direct manager
- **Anne-Claire**: SVP, Chief Digital, Data and AI Officer
- **Susan, Sharon**: Close leadership colleagues
- **Bella**: Daughter, 8th grade
```

### voice/profile.md (Directives + Metadata)

```markdown
---
version: 1
updated: 2024-12-19
tone: direct, warm, technically grounded
register: professional but human
humor: dry wit, contextual, self-deprecating
---

# Voice Profile

## Do

- Lead with the answer, then context
- Use concrete examples over abstractions
- Match technical depth to audience
- Sound like a real person, not a press release

## Don't

- Corporate jargon ("synergy", "leverage", "align stakeholders")
- Excessive hedging ("I think maybe we might consider...")
- Formal when casual works
- Bullet points for everything—prose when narrative flows better
- Generic AI voice—the sanitized, overly helpful default

## Vocabulary

### Prefer
- "Ship it" over "deliver the solution"
- "I'd push back" over "I have some concerns"
- "What's the actual problem?" over "Can you elaborate on the challenge?"

### Avoid
- "Actionable insights"
- "Move the needle"
- "Low-hanging fruit"
- Any phrase that could appear unmodified in a consulting deck

## Formatting

- Short paragraphs (2-4 sentences)
- Direct answers first, context second
- Code examples when explaining technical concepts
- Headers sparingly—only for genuine section breaks

## Examples

See `examples/` directory for demonstrations. These are the training signal.
```

### voice/examples/email-internal.md (First-Class Voice Example)

```markdown
---
type: voice-example
context: Weekly status update to manager
audience: Jorge (direct manager)
tone: direct, efficient
formality: low
---

Jorge -

Navari's on track for January. Three dependencies:
1. Auth integration - Sharon's team, green
2. Rate limiting - done, in staging
3. Audit logging - 80%, shipping Friday

Anne-Claire wants broader pilot after launch. Sending scope proposal tomorrow.

-J
```

### voice/examples/technical-peer.md

```markdown
---
type: voice-example
context: Explaining architecture decision
audience: Senior engineer, technical peer
tone: collaborative, precise
formality: medium
---

We went with a planner-executor pattern for the agent framework. Planner decomposes tasks; executor runs them. Why separate? Swappability—route simple tasks to Haiku, complex to Opus, without touching planning logic.

The tradeoff is coordination overhead. Coupled planning and execution would let the model self-correct mid-task. With separation, we need explicit error propagation. Worth it for our use case since we're optimizing for cost at scale.
```

### memory/entries/2024-12-19-fastapi-decision.md

```markdown
---
type: memory
category: decision
confidence: high
created: 2024-12-19
updated: 2024-12-19
scope: project:navari
tags: [architecture, api, python]
decay: on_project_completion
source: human
---

Chose FastAPI over Flask for the microservice layer.

Key factors:
- Native async support (critical for concurrent workload)
- Automatic OpenAPI generation
- Pydantic integration for type safety
- Team familiarity from SeqAuto

Considered alternatives:
- Flask: simpler but async is bolted-on
- Django: too heavy for microservices
- Go: performance overkill, team ramp-up cost
```

### context.md

```markdown
---
version: 1
updated: 2024-12-19
focus_changed: 2024-12-16
---

# Working Context

## Current Focus

Finishing 2024 strong: Navari production in January, post-announcement AI transformation comms, year-end wrap for global team.

## Active Projects

### Navari Framework
- **Status**: Active, January 2025 target
- **Context**: Agent framework, senior leadership demo successful, Anne-Claire wants broader pilot
- **Dependencies**: Auth (green), rate limiting (done), audit logging (80%)

### AI Transformation Comms
- **Status**: Active
- **Context**: Managing messaging following Enterprise AI unit announcements

### Platform Work
- SeqAuto v3: improvements in progress
- ROAM: data access implementations
- Agentis: strategic orchestration layer

## This Week
- Finalize wrap-up week comms
- Complete Navari audit logging
- Prep 2025 planning materials

## Recently Completed
- Senior leadership Navari demo
- OpenAI partnership evolution (now enterprise-level)
- DGX Spark setup
- Gemma-3-4B fine-tuning (92.4% PubMedQA)
```

### projects/navari/context.md (Project Override)

```markdown
---
extends: ~/.continuum/context.md
project: navari
updated: 2024-12-19
---

# Navari Project Context

## Technical Stack
- Python 3.11+
- FastAPI for service layer
- Redis for caching and rate limiting
- PostgreSQL for persistence
- Kubernetes deployment

## Architecture Decisions
See project memory for rationale.

## Key Stakeholders
- Anne-Claire: Executive sponsor
- Sharon's team: Auth integration
- Platform team: Infrastructure

## Current Sprint
- Audit logging completion
- Load testing prep
- Documentation for broader pilot
```

### config.yaml

```yaml
version: 1

# Core paths
paths:
  base: ~/.continuum
  exports: ~/.continuum/exports

# Thresholds
thresholds:
  context_stale_days: 14      # Warn if context older than this
  memory_decay_days: 90       # Surface memories older than this for review
  voice_refresh_days: 90      # Suggest voice review quarterly

# Export settings
export:
  identity_max_words: 500
  voice_max_examples: 5
  memory_recent_days: 30
  memory_max_entries: 25

# MCP server (phase 2)
mcp:
  enabled: false
  port: 9830

# Voice analysis
voice:
  signals:
    - sentence_length
    - question_frequency
    - hedge_ratio
    - contraction_rate
    - vocabulary_richness
```

---

## CLI Commands (Revised)

### Core Commands

```bash
# Initialize
continuum init [--path ~/.continuum]

# Edit context files
continuum edit identity|voice|context
continuum edit voice example <name>

# Quick memory add
continuum remember "Decided X because Y" [--category decision] [--scope project:navari]

# Status dashboard
continuum status

# Export for Claude Code
continuum export [--project navari] [--output path]

# Validate structure and content
continuum validate
```

### Voice Commands

```bash
# Capture voice sample interactively
continuum voice capture [--context "email to manager"] [--audience "internal"]

# Analyze writing samples
continuum voice analyze <directory-or-files>

# Check outputs against voice profile
continuum voice check [--conversation export.json]
```

### Memory Commands

```bash
# Search memories
continuum memory search "API rate limiting"

# List recent
continuum memory recent [--days 7]

# Decay review (interactive)
continuum memory decay [--older-than 90d]

# Show memory stats
continuum memory stats
```

### Project Commands

```bash
# Create project context
continuum project init navari

# Switch active project
continuum project use navari

# List projects
continuum project list
```

### Sync Commands (Phase 2+)

```bash
# Show divergence from Claude.ai
continuum reconcile

# Start MCP server
continuum serve [--port 9830]
```

---

## MCP Server Architecture (Phase 2)

### Server Registration

```json
// ~/.claude/.mcp.json
{
  "mcpServers": {
    "continuum": {
      "command": "continuum",
      "args": ["serve", "--stdio"],
      "env": {}
    }
  }
}
```

### Resources Exposed

```
continuum://identity
  → Full identity document

continuum://voice
  → Voice profile with inline examples (composed)

continuum://voice/examples
  → List of available voice examples

continuum://voice/examples/{name}
  → Specific voice example

continuum://context
  → Current working context (with project if active)

continuum://memory
  → Recent memories (last 30 days, max 25)

continuum://memory/{id}
  → Specific memory entry

continuum://project/{name}/context
  → Project-specific context
```

### Tools Exposed

```
remember(content, category?, confidence?, scope?, tags?)
  → Add a memory entry

update_focus(focus_text)
  → Update current focus in context

search_memory(query, scope?, limit?)
  → Semantic search over memories

get_relevant_context(task_description)
  → Return composed context relevant to task
```

### Prompts Exposed

```
compose_context(project?, include_memory?, memory_query?)
  → Generate full context injection for current task

voice_check(text)
  → Analyze text against voice profile, return alignment score
```

### Example Claude Code Interaction

Claude Code with MCP enabled:

```
User: Let's work on the Navari rate limiting
Claude: [Queries continuum://project/navari/context]
Claude: [Queries continuum://memory with search "rate limiting"]
Claude: I see rate limiting is done and in staging. The decision from Dec 15 shows
        you chose Redis for the rate limiter. What aspect should we work on?
```

Agent updating memory:

```
Claude: I've discovered the API has a 100/min rate limit with 429 responses.
        Let me remember that for future reference.
        [Calls remember tool: "API rate limit is 100/min, returns 429 on exceed"]
```

---

## Export Composition

### Algorithm

```python
def compose_export(project: str | None = None) -> str:
    """Compose context for export."""

    # 1. Load base identity (condensed)
    identity = load_and_condense("identity.md", max_words=500)

    # 2. Load voice profile
    voice_profile = load("voice/profile.md")

    # 3. Select voice examples (most relevant or diverse)
    voice_examples = select_voice_examples(
        directory="voice/examples/",
        max_examples=5,
        strategy="diverse"  # or "relevant" with task context
    )

    # 4. Load context (compose if project specified)
    if project:
        base_context = load("context.md")
        project_context = load(f"projects/{project}/context.md")
        context = compose_contexts(base_context, project_context)
    else:
        context = load("context.md")

    # 5. Filter memories (recent + relevant)
    memories = filter_memories(
        scope=f"project:{project}" if project else "global",
        days=30,
        max_entries=25
    )

    # 6. Assemble export
    return render_export(
        identity=identity,
        voice_profile=voice_profile,
        voice_examples=voice_examples,
        context=context,
        memories=memories
    )
```

### Export Template

```markdown
<!-- Continuum Export -->
<!-- Generated: {timestamp} -->
<!-- Project: {project or "global"} -->
<!-- Refresh: continuum export [--project {project}] -->

# User Context

## Identity
{condensed identity}

## Voice

{voice directives}

### Examples
{rendered voice examples with context headers}

## Current Context
{composed context}

## Relevant Memory
{filtered memory entries}

---
*Generated by [Continuum](https://github.com/justinjohnson/continuum)*
```

---

## Agent Integration Patterns

### Pattern 1: Context Injection (Basic)

```python
from continuum import Context

ctx = Context.load()
system_prompt = f"""
{ctx.identity}
{ctx.voice}
{ctx.current_context}

Relevant memories:
{ctx.memory.recent(days=30)}
"""
```

### Pattern 2: Live Query (MCP)

Agent queries context through MCP as conversation progresses, pulling relevant memories on demand.

### Pattern 3: Bidirectional (Advanced)

```python
from continuum import Context, memory

# Agent reads context
ctx = Context.load(project="navari")

# Agent does work...

# Agent learns something
memory.remember(
    content="Production deployment requires VPN",
    category="fact",
    confidence="high",
    scope="project:navari",
    source="agent:deployment-checker"
)
```

### Source Attribution

Memory entries track source:
- `source: human` - User added via CLI or manual edit
- `source: agent:<name>` - Agent added programmatically
- `source: import:<origin>` - Imported from external source

This enables filtering (show only human-curated) and auditing (what did agents learn?).

---

## Voice Analysis Pipeline

### Quantitative Analysis (Local)

```python
@dataclass
class VoiceSignals:
    avg_sentence_length: float
    sentence_length_variance: float
    question_frequency: float
    hedge_word_ratio: float
    contraction_rate: float
    active_voice_ratio: float
    first_person_frequency: float
    avg_paragraph_length: float
    vocabulary_richness: float  # type-token ratio
    top_bigrams: list[tuple[str, str, int]]

def analyze_signals(samples: list[str]) -> VoiceSignals:
    """Compute quantitative voice signals from samples."""
    # Pure Python, no ML dependencies
    ...
```

### Qualitative Analysis (Claude)

```python
def analyze_voice_qualitative(
    samples: list[str],
    signals: VoiceSignals
) -> dict:
    """Use Claude to extract qualitative patterns."""

    prompt = f"""
    Analyze these writing samples to extract voice patterns.

    Quantitative signals:
    - Avg sentence length: {signals.avg_sentence_length:.1f} words
    - Question frequency: {signals.question_frequency:.1%}
    - Hedge word ratio: {signals.hedge_word_ratio:.1%}
    - Vocabulary richness: {signals.vocabulary_richness:.2f}

    Samples:
    {format_samples(samples)}

    Extract:
    1. Primary tone (1-2 words)
    2. What makes this voice distinctive?
    3. What this writer NEVER does
    4. Key vocabulary preferences
    5. Structural patterns

    Output as YAML.
    """

    return claude.analyze(prompt, output_format="yaml")
```

### Voice Drift Detection

```python
def check_voice_drift(
    recent_outputs: list[str],
    voice_profile: VoiceProfile,
    voice_examples: list[VoiceExample]
) -> DriftReport:
    """Compare recent outputs against voice profile."""

    # Compute signals for recent outputs
    output_signals = analyze_signals(recent_outputs)

    # Compute signals for voice examples
    example_signals = analyze_signals([e.content for e in voice_examples])

    # Compare signal divergence
    divergence = compute_signal_divergence(output_signals, example_signals)

    # Claude qualitative check
    alignment = claude.analyze(f"""
    Voice profile:
    {voice_profile.directives}

    Voice examples:
    {format_examples(voice_examples[:3])}

    Recent outputs:
    {format_samples(recent_outputs[:3])}

    Rate alignment (1-10) and explain any divergence.
    """)

    return DriftReport(
        signal_divergence=divergence,
        alignment_score=alignment.score,
        issues=alignment.issues
    )
```

---

## Implementation Phases (Revised)

### Phase 1: Foundation (Week 1-2)

- [ ] Project setup (pyproject.toml, structure)
- [ ] `continuum init` - create directory structure with templates
- [ ] `continuum edit` - open files in $EDITOR
- [ ] `continuum status` - dashboard (Rich TUI)
- [ ] `continuum remember` - add memory with YAML frontmatter
- [ ] `continuum export` - compose and generate CLAUDE.md
- [ ] `continuum validate` - check file structure
- [ ] Initial templates (identity, voice, context, memory)
- [ ] Voice examples as first-class (directory structure)
- [ ] Basic tests

### Phase 2: Voice & Memory (Week 3-4)

- [ ] `continuum voice capture` - interactive sample capture
- [ ] `continuum voice analyze` - quantitative + qualitative analysis
- [ ] `continuum memory search` - text search over memories
- [ ] `continuum memory decay` - interactive cleanup
- [ ] Project support (`continuum project init/use`)
- [ ] Context composition (global + project)
- [ ] Voice example selection for exports

### Phase 3: MCP Server (Week 5-6)

- [ ] Basic MCP server implementation
- [ ] Resource handlers (identity, voice, context, memory)
- [ ] Tool handlers (remember, update_focus, search)
- [ ] Claude Code integration testing
- [ ] Documentation for MCP setup

### Phase 4: Intelligence (Week 7-8)

- [ ] Semantic memory search (embeddings)
- [ ] Voice drift detection
- [ ] Relevance scoring for memory filtering
- [ ] Agent source attribution
- [ ] Conversation import

### Future

- Team context (org-level + inheritance)
- Context snapshots (work modes)
- Claude.ai reconciliation helper
- Web UI for non-CLI users
- Voice embedding and similarity

---

## Technical Decisions

### Why No Database?

- Files are the interface (edit with any tool)
- Git-friendly (version, diff, restore)
- Human-inspectable (you can read your context)
- Portable (copy directory, done)
- Claude-native (markdown is Claude's native format)

For search at scale, consider SQLite FTS or embedded vector store (chromadb) as optional acceleration layer, not replacement.

### Why YAML Frontmatter?

- Structured metadata without losing human readability
- Well-known pattern (Jekyll, Hugo, Obsidian)
- Parser available in every language
- Backwards compatible (files without frontmatter still work)

### Why MCP Over Static Export?

- Live queries enable relevant context, not just recent
- Bidirectional updates for agent learning
- Single source of truth (no stale exports)
- Richer integration (tools, prompts, resources)

Static export remains as fallback for environments without MCP.

### Why Voice Examples as First-Class?

- Few-shot learning is Claude's strength
- Examples are more precise than descriptions
- Survive context window pressure better (dense signal)
- Can A/B test example selection strategies
- Feels more natural to author ("here's how I write")

---

## Migration from v1 Spec

If anyone builds from the original IMPLEMENTATION.md:

1. **Directory changes:**
   - `voice-samples/` → `voice/examples/`
   - `MEMORY.md` → `memory/entries/*.md`

2. **Format changes:**
   - Add YAML frontmatter to memories
   - Split voice examples into separate files

3. **New capabilities:**
   - Project support
   - MCP server
   - Source attribution

Provide `continuum migrate` command that handles these automatically.

---

## Open Questions (Reduced)

Most questions from v1 are now addressed. Remaining:

1. **Embedding model for semantic search** - Local (all-MiniLM-L6-v2) or API (OpenAI)?
2. **Voice drift threshold** - What divergence score triggers alert?
3. **Multi-device sync** - Git? Syncthing? Out of scope for v1?
4. **Privacy/encryption** - Some context is sensitive. Encrypt at rest?

---

## Conclusion

This architecture preserves what worked:
- Four-layer context model
- Files as source of truth
- CLI-first interface
- No heavy dependencies

And adds what was missing:
- YAML frontmatter for structure
- Voice examples as first-class citizens
- MCP server for live context
- Project-scoped composition
- Agent-friendly design

The result is a context system that scales from "simple export for Claude Code" to "full agent-native memory layer"—while remaining hackable, portable, and human-readable.

Let's build it.
