# UI Information Architecture

- Purpose: Define what the UI must contain and how the main workflow is organized.
- Owner: Product and frontend leads.
- When to read: Before wireframing screens, implementing the web app, or changing workflow states.
- Decisions that belong here: Screen hierarchy, content zones, primary actions, and user flow structure.

## Primary User Journey

1. User opens the storytelling workspace.
2. User uploads multiple images.
3. User reviews or adjusts image order.
4. User selects a sentiment.
5. System analyzes images and links the sequence.
6. System generates a grounded story.
7. User reviews the result and optionally regenerates with adjusted tone later.

## Core Screen Areas

### 1. Session Header

- Product title and concise explanation.
- Current workflow state.
- Optional reset or start-over action.

### 2. Upload And Sequence Area

- Multi-image upload entry point.
- Ordered thumbnail list.
- Position labels that make story sequence obvious.
- Validation messages for unsupported file types or too many images.

### 3. Sentiment Selection Area

- Small curated list of tone presets.
- Short description of the selected tone.
- Clear indication that tone shapes style, not facts.

### 4. Analysis Trace Area

- Per-image observation summary.
- Transition or sequence hints.
- Confidence or uncertainty display when the system is extrapolating.

### 5. Story Output Area

- Generated short story.
- Supporting grounding summary or trace.
- Regenerate action placed nearby but not more prominent than the story itself.

## Navigation Model

The initial MVP can be a single main workspace page with section-based progression instead of multi-page navigation. This keeps the narrative process visible from start to finish.

Future expansion may add:

- a session history page,
- saved drafts,
- evaluation or debugging views for internal use.

## State Hierarchy

The UI should clearly represent:

- empty state,
- partial upload state,
- ready-to-generate state,
- in-progress analysis/generation,
- completed result,
- recoverable failure.

## Boundaries

- This document defines what content and actions appear on the screen.
- [DESIGN.md](/Users/sarahc/Downloads/SentimentAnalysis_3/DESIGN.md) defines how those screens should look.
- `projects/visual-storytelling/SKILLS/ui-flow.SKILL.md` defines implementation-sensitive interaction rules.
