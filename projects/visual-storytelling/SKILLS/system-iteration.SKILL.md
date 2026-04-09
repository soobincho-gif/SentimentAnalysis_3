# System Iteration Skill

- Purpose: Define the mandatory implementation loop for AI coding agents working on the visual storytelling project.
- Owner: Project lead and engineering maintainers.
- When to read: Before changing architecture, prompts, domain contracts, or evaluation logic.
- Decisions that belong here: Loop discipline, failure taxonomy, and required evidence before closing a task.

## Loop

Every task must follow:

1. inspect current contracts,
2. change one module only,
3. run the narrowest possible test,
4. run one end-to-end smoke test when the pipeline slice exists,
5. record the observed failure type,
6. revise,
7. update docs if boundaries changed.

## Failure Taxonomy

- `GROUNDING_ERROR`
- `ENTITY_MEMORY_ERROR`
- `SEQUENCE_FLOW_ERROR`
- `SENTIMENT_MISMATCH`
- `REDUNDANCY_ERROR`
- `PROMPT_CONTRACT_ERROR`
- `API_INTEGRATION_ERROR`

## Rules

- Do not modify prompts and output schemas in the same step unless necessary.
- Do not bypass structured intermediates.
- Do not move business rules into route handlers.
- Do not hide state in globals.
- Do not add generic `utils` dumping grounds.

## Required Evidence Before Marking A Task Done

- changed files listed,
- input and output contract confirmed,
- test result shown,
- one example story shown when the pipeline is runnable,
- one known limitation acknowledged.
