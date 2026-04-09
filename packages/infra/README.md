# Infra Package

- Purpose: Define what belongs in infrastructure and provider integration code.
- Owner: Backend maintainers.
- When to read: Before adding OpenAI clients, file storage helpers, runtime config, or logging adapters.
- Decisions that belong here: Replaceable technical integrations, not domain policy.

## Scope

`packages/infra` owns provider clients, config loading, storage adapters, and logging adapters that support the storytelling pipeline.

## Not Here

- domain rules,
- scene-to-story policy,
- prompt wording,
- API route logic.
