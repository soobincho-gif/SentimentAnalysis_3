# API App

- Purpose: Describe the responsibility of the backend application layer.
- Owner: Backend maintainers.
- When to read: Before adding routes, schemas, or dependency wiring.
- Decisions that belong here: API app boundaries, transport concerns, and startup responsibilities.

## Scope

`apps/api` will host the HTTP entry points for the MVP. It should validate requests, delegate work to services, and map service results back into transport responses.

## Not Here

- Prompt text
- Domain policy
- Story generation heuristics

Those belong in `packages/prompts`, `packages/core`, and `packages/services`.
