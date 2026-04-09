# Prompts Package

- Purpose: Define the role of prompt assets in the repository.
- Owner: Prompt and backend maintainers.
- When to read: Before adding or changing prompt templates.
- Decisions that belong here: Prompt storage, versioning expectations, and prompt ownership boundaries.

## Scope

`packages/prompts` stores prompt templates, prompt contracts, prompt notes, and revision history for model-facing instructions.

## Rule

Prompt assets belong here even when they are used by only one service. Keep them separate from orchestration code to make prompt iteration visible and reviewable.
