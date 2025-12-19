# ClaudeSync: Philosophy & Standard Operating Procedures

## Supplemental Document (Non-Development)

---

## Part 1: The Philosophy of Portable AI Identity

### Why This Matters

The current state of AI assistants treats memory and context as platform features—something the service provider controls. But this gets the relationship backwards.

When you work with a human colleague over years, they build a mental model of:
- How you think
- How you communicate  
- What you value
- Your history together

This model belongs to the *relationship*, not to either party alone. When AI assistants treat context as a platform feature, they're essentially saying "your relationship with Claude is owned by the interface you happen to be using."

ClaudeSync inverts this. **You** own your context. **You** control what's remembered. **You** carry your identity to wherever Claude exists.

### The Voice Problem

Most memory systems focus on facts: "User lives in Boston", "User prefers Python". But facts are the easy part.

The hard part is **voice**—the ineffable quality that makes someone's communication distinctly *theirs*. Voice includes:

- **Rhythm**: Short punchy sentences? Long flowing ones? Varied?
- **Register**: Formal? Casual? Context-dependent?
- **Directness**: Do you hedge or assert?
- **Warmth**: Personal or professional distance?
- **Humor**: Where does wit appear? What kind?
- **Structure**: How do you organize thoughts?

Voice is what makes you read an email and know who wrote it before seeing the signature. It's what Claude needs to sound like *your* Claude, not *a* Claude.

### The Curation Principle

Passive memory extraction (what Claude.ai does) optimizes for what the *system* thinks is important. But the system doesn't know:

- That offhand comment was actually crucial
- That seemingly important fact is now outdated
- That project is confidential and shouldn't be remembered
- That preference has changed

Active curation puts you in control. Yes, it requires effort. But the effort is minimal compared to the cost of constantly correcting an AI that has a subtly wrong model of you.

### Temporal Decay

Human memory forgets. This isn't a bug—it's a feature. Forgetting:
- Reduces noise
- Keeps context relevant
- Allows change
- Prevents the past from over-determining the present

ClaudeSync builds in decay. Old context fades unless actively refreshed. This keeps your context clean and current.

---

## Part 2: Voice Capture SOP

### Overview

Capturing voice is a multi-step process. You're not trying to describe your voice (that's surprisingly hard). You're trying to **show** it through examples, then let analysis extract patterns.

### Step 1: Gather Samples (30 minutes)

Collect 10-20 samples of your writing across different contexts:

**Required categories:**
- 3-5 emails (mix of internal and external)
- 2-3 technical explanations or documentation
- 2-3 feedback instances (code review, document comments)
- 2-3 casual messages (Slack, texts)

**Where to find samples:**
- Sent email folder
- Slack/Teams message history
- Google Docs comments
- GitHub PR reviews
- LinkedIn posts
- Personal blog (rundatarun.io)

**What makes a good sample:**
- At least 50 words (enough to show patterns)
- Written naturally (not heavily edited)
- Representative of how you actually communicate
- Diverse contexts (not all the same type)

### Step 2: Prepare Sample Files

Create files in `~/.claudesync/voice-samples/`:

```
voice-samples/
├── emails/
│   ├── internal-update.txt
│   ├── external-proposal.txt
│   └── quick-response.txt
├── technical/
│   ├── architecture-doc.txt
│   └── api-explanation.txt
├── feedback/
│   ├── code-review.txt
│   └── doc-comment.txt
└── casual/
    ├── slack-thread.txt
    └── linkedin-post.txt
```

Each file should contain:
```
# Context: [Brief description of what this was]
# Audience: [Who you were writing to]
# Date: [Approximate date]

[The actual content]
```

### Step 3: Run Voice Analysis

```bash
claudesync voice analyze ~/.claudesync/voice-samples/
```

This will:
1. Read all samples
2. Extract quantitative signals (sentence length, question frequency, etc.)
3. Use Claude to identify qualitative patterns
4. Generate a draft VOICE.md

### Step 4: Review and Refine

The generated VOICE.md is a starting point. Review it with these questions:

- Does this sound like me when I read it?
- Are there patterns it missed?
- Are there patterns it identified that aren't really me?
- What anti-patterns should be explicit? (Things I never do)

Edit manually until it feels right.

### Step 5: Test the Voice

Create a new Claude Code session with only your VOICE.md as context. Ask it to:
- Write an email declining a meeting
- Explain a technical concept
- Give feedback on (hypothetical) code

Does the output sound like you? If not, refine VOICE.md.

### Voice Maintenance

Voice drifts over time. Every quarter:
1. Add new samples from recent communication
2. Re-run analysis
3. Compare to existing VOICE.md
4. Update if needed

---

## Part 3: Memory Curation SOP

### Daily Practice (2 minutes)

At end of day, ask yourself:
- Did I make any decisions Claude should remember?
- Did I learn anything that changes how I work?
- Did any facts change? (new role, new project, etc.)

If yes: `claudesync remember "..."` or edit CONTEXT.md

### Weekly Review (10 minutes)

Every Friday or Monday:
1. Review CONTEXT.md - is "Current Focus" still accurate?
2. Scan MEMORY.md - anything outdated?
3. Check sync status - any drift between local and Claude.ai?

### Monthly Decay (15 minutes)

Once a month:
```bash
claudesync decay --older-than 60d
```

This surfaces old entries. For each:
- **Keep**: Still relevant, refresh timestamp
- **Archive**: Historically interesting but not active
- **Delete**: No longer relevant

### Context Transitions

When starting a new project/role:
1. Archive old CONTEXT.md as `context-YYYY-MM.md`
2. Update IDENTITY.md if role changed
3. Start fresh CONTEXT.md
4. Keep MEMORY.md entries that are still relevant

---

## Part 4: Cross-Interface Workflow SOPs

### Starting a Claude.ai Session

1. If it's been more than a week since sync:
   ```bash
   claudesync sync web
   ```
2. Review suggested updates
3. Apply to Claude.ai memory manually (for now)
4. Proceed with session

### Starting a Claude Code Project

1. Navigate to project directory
2. Generate context export:
   ```bash
   claudesync export claude-code --output ./CLAUDESYNC.md
   ```
3. Reference in CLAUDE.md:
   ```markdown
   # Project Context
   See CLAUDESYNC.md for user identity and preferences.
   ```

### After Important Conversations

Whether in Claude.ai or Claude Code, if something important happened:

1. Copy key decision or learning
2. Add to memory:
   ```bash
   claudesync remember "Decided X because Y"
   ```
3. If it changes current focus, update CONTEXT.md

### Handling Conflicts

If Claude.ai and local context disagree:

1. **Local is source of truth** (you curated it intentionally)
2. Update Claude.ai memory to match
3. Document in sync/changelog.md why divergence happened

---

## Part 5: Template Quickstart

### Initial IDENTITY.md Template

```markdown
# Identity

## Core
- **Name**: [Your name]
- **Role**: [Title] at [Organization]
- **Location**: [City, Timezone]

## Background

[2-3 paragraphs. What's your professional story? What shaped how you work today? What do you bring to collaborations?]

## Values & Principles

- [Value 1: e.g., "Clarity over comprehensiveness"]
- [Value 2: e.g., "Ship and iterate over perfect plans"]
- [Value 3]

## Key Relationships

- **[Name]**: [Role, why they matter]
- **[Name]**: [Role, why they matter]
```

### Initial VOICE.md Template

```markdown
# Voice Profile

## Tone
- **Primary**: [One word: Direct? Warm? Analytical?]
- **Humor**: [When and how does wit appear?]

## Always
- [Do this: e.g., "Get to the point quickly"]
- [Do this: e.g., "Use concrete examples"]

## Never
- [Don't do this: e.g., "Use 'synergy' or corporate jargon"]
- [Don't do this: e.g., "Excessive hedging or qualification"]

## Formatting Preferences
- [e.g., "Short paragraphs over long blocks"]
- [e.g., "Code examples over abstract descriptions"]

## Examples

### Email (internal, quick):
[Paste a representative example]

### Technical explanation:
[Paste a representative example]
```

### Initial CONTEXT.md Template

```markdown
# Working Context

**Last Updated**: [Today's date]

## Current Focus

[1-2 sentences: What's the main thing on your mind right now?]

## Active Projects

### [Project Name]
- **Status**: [Active/Planning/Wrapping up]
- **Key context**: [What does Claude need to know?]
- **Next milestone**: [What's coming?]

## This Week

- [Priority 1]
- [Priority 2]
- [Priority 3]
```

---

## Part 6: Troubleshooting

### "Claude still doesn't sound like me"

1. Check if VOICE.md is actually being loaded
2. Add more explicit examples
3. Add more anti-patterns (what NOT to do)
4. Consider: is your VOICE.md too generic?

### "Context feels stale"

1. Run `claudesync decay`
2. Review CONTEXT.md dates
3. Archive completed projects
4. Refresh "Current Focus"

### "Too much to maintain"

1. Focus on VOICE.md and CONTEXT.md only
2. Let MEMORY.md accumulate naturally
3. Use the CLI commands—they're faster than editing
4. Weekly review takes 10 minutes; make it a habit

### "Claude.ai and local are diverging"

1. Check sync/changelog.md
2. Decide which is correct
3. Update the incorrect one
4. Set a sync reminder

---

## Appendix: Justin's Initial Context (to seed ClaudeSync)

Based on our conversations, here's a draft of your starting context:

### IDENTITY.md (Draft)
```markdown
# Identity

## Core
- **Name**: Justin
- **Role**: Executive Director, Oncology Data Science at AstraZeneca
- **Location**: US East Coast (ET)

## Background

I lead an 80-person ODSP team across seven global locations, serving as Head of Agents, Foundation Models, Data Strategy, and all Data Science/AI platforms for Oncology R&D. My career spans from genomics pioneer work at J. Craig Venter Institute in the 2000s, through entrepreneurial work at EdgeBio, to my current AI leadership role.

I'm deeply technical but operate at strategic level. I've built distributed computing systems, trained foundation models, and shipped hundreds of data science projects. I maintain a technical blog at rundatarun.io with 10,000+ followers.

## Values
- Authenticity over corporate polish
- Ship over perfect
- Direct communication
- Technical depth matters
```

### VOICE.md (Draft)
```markdown
# Voice Profile

## Tone
- **Primary**: Direct, warm, technical
- **Humor**: Dry wit, self-deprecating, contextual

## Always
- Get to the point
- Use concrete examples
- Be technically precise
- Sound human, not corporate

## Never
- Corporate jargon ("synergize", "leverage", "align")
- Excessive hedging
- Formal when casual works
- Dumbing down technical content unnecessarily

## Formatting
- Short paragraphs
- Direct sentences
- Questions to engage
- Code/examples when relevant
```

---

*End of Supplemental Document*
