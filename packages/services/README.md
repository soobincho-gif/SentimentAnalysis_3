# Services Package

- Purpose: Explain what belongs in the orchestration layer.
- Owner: Backend maintainers.
- When to read: Before adding image analysis, sequencing, generation, or session workflow code.
- Decisions that belong here: Service ownership, adapter boundaries, and orchestration rules.

## Scope

`packages/services` coordinates use cases across analysis, sequence linking, generation, and regeneration. It should compose domain models, prompts, and provider adapters without owning prompt text or transport logic.
