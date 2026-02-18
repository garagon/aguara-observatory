---
name: intent-interview
description: Transform vague ideas into implementation-ready specifications through structured interviewing. Use when user describes a new feature/product idea, has a problem to solve, or needs to document requirements. Two-phase process: Phase A produces decisions.md, Phase B composes INTENT.md under budget constraints.
---

# Intent Interview

A structured methodology for extracting, refining, and documenting product/feature requirements through deep interviewing.

## Two-Phase Model

```
Phase A: Questioning (default)
    → Output: decisions.md (questions + user decisions)
    → Does NOT touch INTENT.md

Phase B: Compose (explicit user request)
    → Input: decisions.md
    → Output: INTENT.md (under budget constraints)
    → Checks anchor relevance + size budget
```

**Why two phases?** Interview tends to accrete — every answer becomes a new section. By separating questioning from composition, we prevent unbounded growth.

## Phase A: Questioning

### Goal

Collect all design decisions without writing any Intent structure. Output is a flat `decisions.md` file.

### Process

#### Step 1: Problem Space (1-2 rounds)

```
Questions to ask:
- What is the core problem?
- Who is the target user?
- Is this a new product or addition to existing?
- What's the priority/urgency?
```

#### Step 2: Deep Dive (iterative)

Cover these dimensions systematically, 3-4 questions per round:

| Dimension | Key Questions |
|-----------|---------------|
| Data | Sources, contracts, validation, conflicts, authentication |
| Rendering | Cross-platform strategy, components, theming, sizing |
| Sync/Update | Real-time requirements, refresh strategy, failure handling |
| Architecture | Storage, sharing, cloud/local, offline capability |
| UX | Configuration flow, error states, feedback mechanisms |
| Edge Cases | Failures, migrations, security, low-end devices |
| Scope | MVP boundaries, what's in/out, phasing |
| Tech Stack | Languages, frameworks, existing code to reuse |

#### Step 3: Contradiction Resolution

When answers conflict with earlier choices:
1. Point out the contradiction explicitly
2. Ask for clarification with specific options
3. Update decisions.md accordingly

#### Step 4: Scope Guard

**Before recording each decision, check against the anchor (if established).**

If a question or answer drifts from the declared purpose:

```
⚠️ Scope guard: This may be out of scope for:
  > "Enable type-safe binary communication between AFS nodes."

Record anyway? Or defer to a separate Intent?
```

The anchor is established early — ask "In one sentence, what is this module's reason to exist?" in round 1.

#### Step 5: Readiness Check

Before moving to Phase B, verify:
- Can a code agent implement this without asking questions?
- Are all technical choices specified?
- Are edge cases covered?

If gaps exist, continue questioning.

### decisions.md Output Format

```markdown
# Interview Decisions: {Project/Module Name}

> Anchor: {one sentence purpose}

## Decisions

### 1. {Topic}
- **Question**: {what was asked}
- **Decision**: {what was decided}
- **Rationale**: {why}

### 2. {Topic}
...

## Open Items
- {unresolved questions}

## Out of Scope
- {items deferred by scope guard}
```

### Question Design

#### Do
- Ask non-obvious, probing questions
- Probe tradeoffs ("if X fails, should we Y or Z?")
- Use concrete scenarios
- Offer 3-4 mutually exclusive options
- Match user's language (中文/English)

#### Don't
- Ask yes/no questions
- Ask obvious implementation details
- Ask multiple unrelated questions at once
- **Add sections to INTENT.md during questioning**

#### Format
Use `AskUserQuestion` tool with:
- 1-4 questions per round
- 2-4 options per question
- Short header (max 12 chars)
- Clear option descriptions

## Phase B: Compose

**Only runs when user explicitly requests it** (e.g., "compose the intent" or "generate INTENT.md").

### Process

#### Step 1: Read decisions.md

Parse all decisions and the anchor statement.

#### Step 2: Draft INTENT.md

Structure into standard Intent sections:

```markdown
# {Module} Intent

> Anchor: {one sentence from decisions.md}

## Responsibilities
- {derived from decisions}

## Non-Goals
- {from "Out of Scope" + explicit exclusions}

## Structure
{architecture diagram}

## API
{interface definitions}

## Examples
{input → output}
```

#### Step 3: Anchor Relevance Check

For each section in the draft, verify:
- Can this section trace back to the anchor?
- If not, flag it:

```
⚠️ Section "## Caching Strategy" cannot be traced to anchor:
  > "Enable type-safe binary communication between AFS nodes."

Options:
1. Remove this section
2. Move to a separate Intent
3. Keep (explain why it serves the anchor)
```

#### Step 4: Budget Check

Count the lines of the draft and check against tiered budget:

| Lines | Status | Action |
|-------|--------|--------|
| ≤ 300 | Healthy | Save |
| 300–500 | Warning | Prompt user to trim before saving |
| > 500 | Blocked | Must trim before saving |

If over budget:

```
⚠️ Budget warning: 437/300 lines (+137)

Sections by size:
1. ## API — 45 lines
2. ## Structure — 38 lines
3. ## Detailed Behavior — 35 lines
...

Suggestions to reduce:
- Merge "## Error Handling" into "## API" constraints
- Move "## Migration Guide" to a separate doc
- Simplify "## Structure" diagram
```

Present options to user via `AskUserQuestion` before saving.

#### Step 5: Save

Write the budget-compliant INTENT.md. Optionally generate overview.md if user requests.

## Output Artifacts

### decisions.md (Phase A output)
Interview record with all questions, decisions, rationale, and scope boundaries.

### records/interview-{date}.md (Phase A side-effect)
Raw interview transcript saved to `records/` for full traceability. Updates `records/INDEX.md`.

### intent.md (Phase B output)
Technical specification under budget constraints, with anchor-verified sections.

### overview.md (optional, Phase B)
One-page human summary:

```markdown
# {Project}: One-line description

## One sentence explanation

## Why?
Problem in plain language

## Core experience
ASCII flow diagram

## Architecture
ASCII component diagram

## Key decisions
| Question | Choice | Why |

## Scope
In / Out

## Risk + Mitigation

## Next steps
```

## Workflow

```
User describes idea
    ↓
Phase A: Questioning
    ├── Round 1: Problem space + establish anchor
    ├── Round 2-N: Deep dive (with scope guard)
    ├── Resolve contradictions
    └── Readiness check
    ↓
Save decisions.md
    ↓
User requests "compose" / "generate intent"
    ↓
Phase B: Compose
    ├── Draft from decisions
    ├── Anchor relevance check
    ├── Budget check
    └── Save INTENT.md
    ↓
(Optional) Generate overview.md
```
