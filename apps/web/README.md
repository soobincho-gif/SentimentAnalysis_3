# Web App

- Purpose: Describe the responsibility of the future web client.
- Owner: Frontend maintainers.
- When to read: Before implementing screens, client state, or UI contracts.
- Decisions that belong here: Web app scope, interaction ownership, and client-side boundaries.

## Scope

`apps/web` will host the upload experience, ordering UI, sentiment selection, workflow states, analysis trace, and story presentation.

## Not Here

- Canonical business rules
- Hidden contract definitions
- Inline copies of prompt logic

Those belong in shared docs and backend packages.
