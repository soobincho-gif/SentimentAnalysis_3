# Implementation Roadmap

- Purpose: Give the next implementer a practical order of operations for the MVP.
- Owner: Tech lead.
- When to read: Before starting implementation work or splitting tasks across agents.
- Decisions that belong here: Sequencing of implementation phases, milestones, and handoff expectations.

## Phase 1: Contracts And Skeleton

- Create domain models for ordered image sets, scene observations, sequence memory, narrative plans, sentiment profiles, story drafts, evaluation reports, and revision decisions.
- Add service interfaces for preprocessing, scene analysis, sequence linking, narrative planning, sentiment control, story generation, evaluation, revision, and session orchestration.
- Create initial prompt assets with versioned files and explicit input and output contracts.

## Phase 2: Backend MVP Flow

- Implement image preprocessing and validation flow.
- Implement scene analysis adapter and service.
- Implement sequence memory and linking service.
- Implement narrative planning and grounded story generation services.
- Add evaluation and one-pass revision loop.
- Add API routes for session submission and story generation.

## Phase 3: Evaluation And Guardrails

- Add tests for grounding, order preservation, entity continuity, redundancy, and sentiment adherence.
- Add basic logging for stage-level failures.
- Add failure messages that map cleanly to UI recovery states.
- Add failure taxonomy reporting to support targeted revision.

## Phase 4: Web MVP

- Implement upload flow, ordered image list, sentiment selector, and story view.
- Surface progress states for preprocessing, analysis, linking, planning, generation, and evaluation.
- Add regeneration entry points that reuse existing analysis when possible.

## Phase 5: Refinement

- Improve prompt quality using evaluation feedback.
- Add better uncertainty display and traceability in the UI.
- Decide whether persistence or async processing is needed.
- Harden the thin `submission/app.py` entrypoint for coursework or demo delivery.
