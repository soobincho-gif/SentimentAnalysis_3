# Code Structure

- Purpose: Define the intended module layout and dependency rules for the codebase.
- Owner: Tech lead.
- When to read: Before creating Python modules, package boundaries, service layers, or API handlers.
- Decisions that belong here: Package responsibilities, module naming, dependency direction, and anti-spaghetti implementation rules.

## Monorepo Package Layout

```text
apps/
  api/
  web/
packages/
  core/
  services/
  prompts/
  infra/
  ui/
submission/
tests/
```

## Recommended Python Module Structure

### `packages/core/src/visual_storytelling_core/`

- `models/`
  Domain entities and value objects.
- `schemas/`
  Canonical typed contracts shared conceptually across layers.
- `policies/`
  Pure business rules such as grounding constraints, sequencing rules, and revision policies.

### `packages/services/src/visual_storytelling_services/`

- `preprocessing/`
  Image validation and preprocessing orchestration.
- `analysis/`
  Scene analysis orchestration.
- `sequencing/`
  Sequence linking and entity memory logic.
- `planning/`
  Narrative planning logic.
- `sentiment/`
  Sentiment profile mapping and control logic.
- `generation/`
  Story generation orchestration.
- `evaluation/`
  Grounding, coherence, and redundancy checks.
- `revision/`
  Revision decisions and targeted retry logic.
- `sessions/`
  End-to-end workflow coordination.

### `packages/infra/src/visual_storytelling_infra/`

- `openai_client/`
  Provider wrapper and request execution.
- `file_storage/`
  Temporary file references or storage adapters.
- `config/`
  Environment and runtime settings.
- `logging/`
  Structured application logging adapters.

### `apps/api/src/visual_storytelling_api/`

- `routes/`
  HTTP handlers only.
- `schemas/`
  Transport request and response models.
- `dependencies/`
  Wiring for service construction.
- `app.py`
  Application startup and router registration.

### `submission/`

- `app.py`
  Thin Python-first entrypoint for coursework submission or local demo execution.
- `README_submission.md`
  Submission-specific run instructions and constraints.

## Dependency Rules

- `apps/api` may depend on `packages/services` and `packages/core`.
- `packages/services` may depend on `packages/core`, `packages/prompts`, and `packages/infra`.
- `packages/prompts` must remain import-light and data-oriented.
- `packages/infra` must not own domain decisions.
- `packages/core` must not depend on any application or adapter layer.
- `submission` may orchestrate `packages/services` but must not re-implement business rules.

## Naming Rules

- Name modules after a narrow responsibility: `sequence_linker.py`, not `utils.py`.
- Use nouns for models and policies, verbs or role nouns for orchestrators.
- Keep prompt names aligned with service responsibilities.
- Separate observed facts, memory, planning, generation, and evaluation in module names when they are distinct responsibilities.

## Non-Responsibilities By Layer

### `packages/core` should not own

- HTTP concerns,
- SDK clients,
- environment variable loading,
- UI formatting.

### `packages/services` should not own

- inline prompt text,
- frontend display copy,
- route-level validation details,
- provider SDK bootstrapping details.

### `packages/infra` should not own

- domain invariants,
- narrative policy,
- prompt wording decisions.

### `apps/api` should not own

- generation policy,
- image analysis heuristics,
- sentiment mapping rules.

### `submission` should not own

- business rules,
- prompt text,
- domain contract definitions.

## Anti-Spaghetti Rules

1. No business logic in route handlers.
2. No prompt strings inside service files.
3. No duplicated contract fields without a canonical owner.
4. No catch-all utility modules.
5. No hidden singleton state.
6. No mutation of original analysis results during regeneration.
7. No direct UI dependence from backend packages.
8. No direct vendor SDK dependence from domain models.
9. No multi-responsibility service classes.
10. No undocumented dependency shortcuts across package boundaries.
11. No direct final-story generation from raw images once structured observations exist.
12. No silent mixing of evaluation logic into generation prompts without an explicit evaluator boundary.
