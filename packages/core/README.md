# Core Package

- Purpose: Explain what belongs in the domain layer.
- Owner: Backend maintainers.
- When to read: Before adding models, policies, or canonical schemas.
- Decisions that belong here: Domain ownership and what the core layer must stay independent from.

## Scope

`packages/core` owns domain entities, validation, and business policies that should remain independent from frameworks and model providers.

## Not Here

- HTTP handlers
- SDK clients
- Prompt text
