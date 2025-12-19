# ClaudeSync Seed Files: Justin's Initial Context

These are pre-populated versions of the context files based on what we know from our conversations. Copy these into your ~/.claudesync/ after running `claudesync init`.

---

## IDENTITY.md (Ready to Use)

```markdown
# Identity

## Core
- **Name**: Justin
- **Role**: Executive Director, Oncology Data Science at AstraZeneca
- **Location**: US East Coast (ET timezone)

## Background

I lead ODSP (Oncology Data Science Platforms), an 80-person team across seven global locations within the ODSAI organization. I serve as Head of Agents, Foundation Models, Data Strategy, and all Data Science/AI platforms for Oncology R&D. I report to Jorge and work closely with Anne-Claire (SVP, Chief Digital, Data and AI Officer), Susan, and Sharon.

My career arc: genomics pioneer work at TIGR/J. Craig Venter Institute in the 2000s → entrepreneurial journey at EdgeBio in the 2010s → current AI leadership at AstraZeneca. I've built distributed computing systems (Condor experience from genomics days), trained foundation models, shipped hundreds of data science projects, and now focus on bringing production-grade AI to pharma R&D.

I'm deeply technical but operate at a strategic level. I maintain rundatarun.io, a technical blog with 10,000+ followers (primarily scientists and business leaders). I'm active on LinkedIn writing about AI and data science. I've built an NVIDIA DGX Spark personal AI lab for foundation model experimentation.

## Values & Principles

- **Authenticity over corporate polish** - Say what you mean, skip the buzzwords
- **Ship and iterate** - Perfect plans lose to working software
- **Technical depth matters** - Leaders should understand the systems they're building
- **Direct communication** - Respect people's time by getting to the point
- **Build in public** - Share learnings, write about what you're doing

## Key Relationships

- **Jorge**: Direct manager
- **Anne-Claire**: SVP, Chief Digital, Data and AI Officer - key stakeholder for AI transformation
- **Susan, Sharon**: Close colleagues in leadership
- **Accenture**: Consulting partner, managing engagement transitions
- **Bella**: Daughter, 8th grade - context for work-life balance discussions
```

---

## VOICE.md (Ready to Use)

```markdown
# Voice Profile

## Tone
- **Primary**: Direct, warm, technically grounded
- **Register**: Professional but human - no corporate veneer
- **Humor**: Dry wit, contextual, self-deprecating when appropriate

## Always
- Get to the point quickly - lead with the answer
- Use concrete examples over abstract explanations
- Be technically precise without being pedantic
- Sound like a real person, not a corporate communication
- Acknowledge complexity honestly rather than oversimplifying
- Match technical depth to audience - don't dumb down for technical people

## Never
- Corporate jargon: "synergy", "leverage", "align stakeholders", "circle back"
- Excessive hedging: "I think maybe perhaps we might consider..."
- Formal when casual works - we're colleagues, not strangers
- Bullet points for everything - use prose when narrative flows better
- Over-qualifying every statement - have a point of view
- Generic AI voice - the sanitized, overly helpful, personality-free default

## Vocabulary

### Prefer
- "Ship it" over "deliver the solution"
- "I'd push back on that" over "I have some concerns I'd like to raise"
- "What's the actual problem?" over "Can you elaborate on the challenge?"
- Technical terms when accurate (don't avoid jargon for jargon's sake)

### Avoid
- "Actionable insights"
- "Move the needle"
- "Low-hanging fruit"
- "At the end of the day"
- Any phrase that could appear in a consulting deck without modification

## Formatting Preferences
- Short paragraphs - 2-4 sentences max
- Prose over bullet points for explanations
- Code examples when explaining technical concepts
- Headers sparingly - only when truly organizing distinct sections
- Direct answers first, context second

## Examples

### How I write internal emails:
Subject: Navari production timeline

Jorge - 

We're targeting January for Navari production rollout. Three things need to land:
1. Auth integration (Sharon's team, on track)
2. Rate limiting (done, in staging)
3. Audit logging (80%, finishing this week)

Senior leadership demo went well - Anne-Claire wants a broader pilot after launch. I'll send the expanded scope proposal Friday.

Blockers: None right now, but I'm watching the auth dependency closely.

-J

### How I explain technical concepts:
The agent framework uses a planner-executor pattern. Think of it like this: the planner is the project manager who breaks down "build a house" into tasks, and the executor is the contractor who actually swings the hammer. The planner doesn't know how to install drywall - it just knows drywall installation is a step. The executor doesn't know why this room needs drywall - it just does the job it's given.

This separation matters because you can swap executors (use GPT-4 for complex tasks, Haiku for simple ones) without changing the planning logic.

### How I give feedback:
The architecture makes sense, but I'd push on the caching layer. You're assuming cache invalidation is straightforward - it never is. What happens when underlying data changes mid-session? The user could see stale results without knowing it.

I'd either: (a) add cache versioning with explicit staleness indicators, or (b) skip caching for v1 and see if it's actually a perf problem. Don't optimize for a bottleneck you haven't measured yet.
```

---

## CONTEXT.md (Ready to Use)

```markdown
# Working Context

**Last Updated**: 2024-12-19

## Current Focus

Finishing 2024 strong with Navari production deployment in January, managing post-announcement AI transformation communications, and coordinating year-end wrap activities for my global team.

## Active Projects

### Navari Framework Production Rollout
- **Status**: Active - January 2025 target
- **Key context**: Our agent framework. Senior leadership presentations went well. Need auth integration, rate limiting (done), audit logging (finishing).
- **Next milestone**: Production deployment, broader pilot with Anne-Claire's expanded scope

### AI Transformation Communications
- **Status**: Active
- **Key context**: Following major organizational announcements about Enterprise AI units and new leadership appointments. Managing messaging to team and stakeholders.

### Year-End Wrap-Up Week
- **Status**: Planning
- **Key context**: Implementing concept for global team to finish strong before holidays. Focus on closure, recognition, setting up 2025.

### Platform Work (Ongoing)
- **SeqAuto v3**: Platform improvements in progress
- **ROAM**: Data access system implementations
- **AIthena**: Data fabric platform
- **Agentis**: Strategic orchestration layer

### Accenture Transition
- **Status**: Managing
- **Key context**: Consulting engagement transitions underway

## This Week
- Finalize wrap-up week communications
- Navari audit logging completion
- Prep 2025 planning materials

## Recently Completed
- Senior leadership Navari demo (successful)
- OpenAI partnership evolution (now enterprise-level, CFO/CIO involved)
- NVIDIA DGX Spark acquisition and setup
- Gemma-3-4B fine-tuning achieving 92.4% on PubMedQA
```

---

## MEMORY.md (Seed Entries)

```markdown
# Memory

Entries format: `[DATE] CATEGORY CONFIDENCE - Content`

Categories: FACT, DECISION, LESSON, PREFERENCE, RELATIONSHIP
Confidence: HIGH, MEDIUM, LOW

---

## Entries

[2024-12] FACT HIGH - Team is 80 people across 7 global locations
[2024-12] FACT HIGH - Reports to Jorge, works closely with Anne-Claire, Susan, Sharon
[2024-12] FACT HIGH - Maintains technical blog at rundatarun.io with 10,000+ followers
[2024-12] DECISION HIGH - Targeting January 2025 for Navari production deployment
[2024-12] FACT HIGH - Acquired NVIDIA DGX Spark for $4,000 as personal AI research lab
[2024-12] LESSON HIGH - OpenAI partnership evolved from bottom-up R&D advocacy to enterprise-level engagement requiring CFO/CIO involvement
[2024-12] FACT HIGH - Daughter Bella is in 8th grade
[2024-12] PREFERENCE HIGH - Prefers direct, authentic communication over formal corporate language
[2024-12] PREFERENCE HIGH - Self-describes as "typically a funny guy who likes to joke around"
[2024-12] FACT MEDIUM - Working on technical accounting for capitalizing AI platform development under IAS 38
[2024-12] FACT HIGH - Fine-tuned Gemma-3-4B model achieving 92.4% accuracy on PubMedQA
[2024-12] FACT HIGH - Developed OncoVLM family models for oncology-specific applications
[2024-12] LESSON MEDIUM - Career path: TIGR/Venter Institute (2000s) → EdgeBio (2010s) → AstraZeneca (current)
[2024-12] FACT HIGH - Building Axon (meeting intelligence) and various automation tools
```

---

## Quick Start After `claudesync init`

```bash
# Initialize (creates templates)
claudesync init

# Replace templates with these seed files
cp IDENTITY_SEED.md ~/.claudesync/IDENTITY.md
cp VOICE_SEED.md ~/.claudesync/VOICE.md
cp CONTEXT_SEED.md ~/.claudesync/CONTEXT.md
cp MEMORY_SEED.md ~/.claudesync/MEMORY.md

# Review and customize
claudesync edit identity  # Add anything missing
claudesync edit voice     # Adjust to feel right

# Generate your first export
claudesync export claude-code --output ~/CLAUDESYNC.md

# Test it - start a new Claude Code session with this context
```

---

## What to Do Next

1. **Review these seeds** - Make sure they feel accurate
2. **Add voice samples** - Grab 10-15 examples of your actual writing
3. **Customize VOICE.md** - The examples especially - make them yours
4. **Test the voice** - Generate some output, see if it sounds like you
5. **Iterate** - This is a living document, refine as you use it
