# Testing Strategy

- Purpose: Define how the MVP will be validated as code is added.
- Owner: Engineering team.
- When to read: Before implementing services, adding prompts, or shipping API/UI behavior.
- Decisions that belong here: Test levels, coverage priorities, fixture strategy, and quality gates.

## Testing Principles

- Test domain behavior before end-to-end polish.
- Prefer deterministic contract tests around structured outputs.
- Treat prompt changes as behavior changes that deserve review.
- Grounding failures are product bugs, not just model quirks.

## Test Layers

### Unit Tests

Target:

- domain validation,
- sequencing policies,
- sentiment mapping,
- regeneration rules,
- prompt variable assembly.

Location:

- `tests/unit/`

### Integration Tests

Target:

- session orchestration,
- adapter boundaries,
- API-to-service contract mapping.

Location:

- `tests/integration/`

### Contract Tests

Target:

- request and response payload compatibility,
- canonical DTO structure,
- prompt input and output expectations.

Location:

- `tests/contracts/`

### UI Flow Tests

Target:

- upload ordering behavior,
- sentiment selection state,
- loading and failure state visibility.

Location:

- `tests/ui/` once the frontend exists.

## MVP Quality Priorities

The earliest required tests should cover:

- image order preservation,
- grounded observation parsing,
- separation between analysis and generation stages,
- reuse of analysis during sentiment-only regeneration,
- API contract stability.

## Test Data Guidance

- Keep a small, curated image fixture set for repeatable analysis experiments.
- Store expected observations as structured fixtures, not only prose snapshots.
- Use prompt snapshots sparingly and always pair them with higher-level behavior assertions.

## What We Will Not Rely On

- Manual QA alone.
- Golden story prose snapshots as the only signal of correctness.
- Untyped ad hoc fixtures that hide contract drift.
