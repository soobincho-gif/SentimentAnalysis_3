# ADR-001: Monorepo Structure

- Purpose: Record the decision to use a documentation-first monorepo with separated apps, packages, docs, and project execution files.
- Owner: Tech lead.
- When to read: Before questioning the high-level repo layout or proposing a new folder convention.
- Decisions that belong here: Structural decisions that will persist across multiple implementation phases.

## Status

Accepted

## Context

The project needs both backend and UI work, prompt iteration, evolving model behavior, and clear documentation for future AI-agent handoff. If prompt logic, service orchestration, and UI behavior are mixed together early, the MVP will drift into spaghetti code and make later iteration expensive.

## Decision

We will use a monorepo with these primary layers:

- `apps/` for deployable applications,
- `packages/` for reusable domain and service code,
- `docs/` for planning, architecture, engineering standards, and ADRs,
- `projects/` for project-specific execution docs and skill-level rules,
- `tests/` for cross-cutting validation.

We will also maintain:

- `AGENTS.md` for repo-wide engineering rules,
- `DESIGN.md` for repo-wide UI design rules.

## Consequences

Positive:

- Clear dependency boundaries.
- Better handoff for future agents.
- Prompt iteration can happen without contaminating service code.
- UI and backend can evolve in parallel against explicit contracts.

Tradeoffs:

- More initial documentation work.
- Contributors must learn the document hierarchy.
- Some folders will stay light until implementation catches up.

## Alternatives Considered

### Single app folder with mixed modules

Rejected because it would blur domain, prompt, API, and UI concerns too early.

### Separate repos for backend and frontend

Rejected for the MVP because prompt contracts, shared concepts, and project docs need to stay tightly aligned while the product is still forming.
