# AGENTS.md

## 1. Purpose

This repository is built for a visual storytelling system:
the user uploads multiple images, selects a sentiment, and the system generates a short grounded story that follows the image order naturally.

This file defines how coding agents must work in this repository.

The goal is not just to make the code run.
The goal is to keep the system:
- modular,
- grounded,
- testable,
- easy to extend,
- resistant to spaghetti code.

Agents must optimize for clarity, traceability, and revision-friendliness.

---

## 2. Mission

Your job is to help build and improve a Python-based visual storytelling system with the following product goals:

1. Accept multiple user-uploaded images
2. Preserve or allow user-controlled image order
3. Accept one user-selected sentiment
4. Analyze each image for observable content
5. Link images into a coherent sequence
6. Generate a short story that reflects the selected sentiment
7. Keep the story grounded in visible content
8. Support future UI refinement and regeneration flows

You must treat this as a structured multimodal system, not as a single prompt wrapper.

---

## 3. Project philosophy

This project is based on four design beliefs:

### 3.1 Facts come before narration
The system must first extract observable scene-level facts before attempting story generation.

### 3.2 Sequence matters
This is not independent caption generation.
The system must reason across images as a sequence.

### 3.3 Sentiment is style, not truth
Sentiment should affect tone and pacing, not fabricate unsupported events.

### 3.4 Evaluation is part of generation
A story is not "done" just because text was generated.
It must be checked for grounding, coherence, and redundancy.

---

## 4. Document priority order

If instructions conflict, follow this order:

1. `AGENTS.md`
2. `projects/visual-storytelling/PROJECT.md`
3. `projects/visual-storytelling/SKILLS/*.SKILL.md`
4. `docs/02_architecture/*.md`
5. `docs/01_planning/*.md`
6. `DESIGN.md`
7. `README.md`

### Interpretation rule
- `AGENTS.md` defines how to work
- `PROJECT.md` defines what this project is trying to achieve
- `SKILL.md` files define how specific subsystems should be implemented
- architecture docs define boundaries and contracts
- planning docs define scope and rationale
- `DESIGN.md` defines UI/interaction style
- `README.md` is for orientation, not authoritative architecture control

If you discover a real contradiction, do not silently choose one.
State the conflict clearly and follow the higher-priority file.

---

## 5. Mandatory work loop

Every meaningful task must follow this loop:

1. Inspect
2. Design
3. Attempt
4. Evaluate
5. Revise
6. Record

You must not skip directly from reading the task to broad implementation.

---

## 6. Detailed loop rules

### 6.1 Inspect
Before changing code:
- identify which module or boundary is being changed
- read the relevant contracts and docs
- determine whether this is a domain, service, infra, prompt, or UI concern
- identify what must remain unchanged

Minimum files to inspect before most changes:
- `AGENTS.md`
- relevant `SKILL.md`
- relevant contract/model files
- the target module itself

### 6.2 Design
Before coding, explicitly state:
- what is being changed
- why it is being changed
- input contract
- output contract
- expected failure modes
- how success will be checked

Do not make broad unscoped changes.

### 6.3 Attempt
Implement one focused change at a time.

Examples of good task granularity:
- add `SceneObservation` contract
- implement sequence linker heuristic
- refine suspenseful sentiment profile
- add grounding evaluator flag for unsupported objects

Examples of bad task granularity:
- "rewrite the whole pipeline"
- "improve everything"
- "clean up the architecture"

### 6.4 Evaluate
After each change, run the narrowest meaningful verification first.

Order:
1. syntax / import sanity
2. unit test
3. contract test
4. smoke test
5. end-to-end qualitative check

Do not jump straight to broad manual testing if a small contract test would catch the issue faster.

### 6.5 Revise
If the change fails:
- identify the failure category
- fix the smallest cause first
- do not start unrelated refactors
- do not change prompts, schemas, and orchestration all at once unless absolutely necessary

### 6.6 Record
After each meaningful change, record:
- changed files
- what improved
- what remains uncertain
- what the next best step is

Record this in one of:
- `projects/visual-storytelling/TASKS.md`
- `docs/05_decisions/*.md`

For major structural work, also leave a report-friendly trail in `logs/`.

---

## 7. Failure taxonomy

Use these failure categories when diagnosing issues:

- `GROUNDING_ERROR`
- `ENTITY_MEMORY_ERROR`
- `SEQUENCE_FLOW_ERROR`
- `SENTIMENT_MISMATCH`
- `REDUNDANCY_ERROR`
- `PROMPT_CONTRACT_ERROR`
- `API_INTEGRATION_ERROR`
- `UI_STATE_ERROR`
- `SCHEMA_DRIFT_ERROR`
- `EVALUATION_LOGIC_ERROR`

### Meaning
- `GROUNDING_ERROR`: story mentions unsupported facts
- `ENTITY_MEMORY_ERROR`: recurring people/animals/objects are not linked consistently
- `SEQUENCE_FLOW_ERROR`: story does not follow image order or transitions poorly
- `SENTIMENT_MISMATCH`: tone does not match selected sentiment
- `REDUNDANCY_ERROR`: repetitive content without narrative purpose
- `PROMPT_CONTRACT_ERROR`: prompt output shape does not match expected schema
- `API_INTEGRATION_ERROR`: external model or provider call breaks
- `UI_STATE_ERROR`: interface shows stale or mismatched data
- `SCHEMA_DRIFT_ERROR`: docs, models, and services disagree about structure
- `EVALUATION_LOGIC_ERROR`: evaluator flags wrong things or misses obvious problems

Always name the failure type explicitly when possible.

---

## 8. Anti-spaghetti rules

### 8.1 No business logic in UI or route handlers
UI files and API route handlers must stay thin.

They may:
- collect input
- call the pipeline
- return output

They may not:
- implement sequencing logic
- implement generation policy
- embed evaluation rules
- contain large prompt bodies

### 8.2 No giant dumping-ground modules
Do not create broad files like:
- `utils.py`
- `helpers.py`
- `misc.py`

unless the file is narrowly scoped and clearly named.

Prefer:
- `grounding_rules.py`
- `sequence_matching.py`
- `sentiment_profiles.py`

### 8.3 Prompts must not live inside service logic
Keep prompt assets in `packages/prompts/`.
Services may assemble inputs and call prompt loaders, but should not store large prompt text inline.

### 8.4 Contracts must be explicit
All important stage boundaries must use typed models.
Do not pass loose dicts everywhere if the structure is stable enough to model.

### 8.5 One module, one reason to change
If a module changes for unrelated reasons, the boundary is probably wrong.

### 8.6 No hidden global state
Do not rely on mutable module-level globals for pipeline behavior.

### 8.7 Preserve intermediate representations
Do not collapse:
image analysis -> sequence linking -> planning -> generation -> evaluation
into a single opaque step unless the architecture docs are intentionally changed.

### 8.8 Keep infra separate from policy
External API access, file storage, config, and logging belong in infra.
Narrative rules and grounding policy do not.

---

## 9. Required package boundaries

Preferred dependency direction:

```text
apps/web or submission/app.py -> services -> core
services -> prompts
services -> infra
core -> no outward dependency
```

### Meanings

#### `packages/core`

Contains:

* domain models
* contracts
* pure rules
* validation logic
* sentiment profiles if purely domain-oriented

Should not depend on:

* Gradio
* FastAPI
* OpenAI SDK
* storage implementation

#### `packages/services`

Contains:

* orchestration logic
* pipeline stages
* flow between contracts

Should not become a dumping ground for raw UI state or provider-specific payloads.

#### `packages/prompts`

Contains:

* prompt templates
* output format instructions
* prompt versioning

#### `packages/infra`

Contains:

* model client wrappers
* config loading
* file storage
* logging
* bootstrap wiring

#### `submission/`

Contains:

* coursework-facing entrypoint
* thin app launcher
* no serious business logic

---

## 10. Contract discipline

If you change a contract:

1. update the Pydantic model
2. update the relevant docs
3. update the dependent services
4. update or add tests
5. mention the change in task or decision logs

Never silently change contract meaning.

Examples:

* renaming `visible_mood`
* changing `sentence_alignment` shape
* altering how `SequenceMemory` stores recurring entities

All of these require contract-aware updates.

---

## 11. How to approach model and prompt changes

When working on prompt-driven stages:

* define the output schema first
* define what the model is allowed to infer
* define forbidden claims
* keep prompt output easy to validate

Do not optimize only for eloquence.
Optimize for:

* schema reliability
* grounding
* controllability
* evaluability

When a prompt fails, decide whether the root cause is:

* prompt wording,
* contract design,
* orchestration,
* or post-processing.

Do not assume the prompt is always the problem.

---

## 12. Evaluation policy

A generated story is not automatically acceptable.
It must be evaluated along at least these dimensions:

* grounding
* coherence
* redundancy
* sentiment fit
* readability

### Minimum expectation

A story should:

* follow image order
* preserve major recurring entities
* avoid major unsupported claims
* reflect the selected sentiment
* read as one story rather than disconnected captions

If a draft fails obviously on one of these, revision is required.

---

## 13. Testing policy

For any meaningful change, aim to cover at least one of these:

### Unit tests

Use when logic is local and deterministic.

### Contract tests

Use when validating model shape or inter-stage boundaries.

### Smoke tests

Use for full pipeline sanity:
images -> observations -> memory -> plan -> story -> evaluation

### Qualitative checks

Use when the output quality is partly subjective.
When running qualitative checks, explicitly note:

* what looked good
* what looked weak
* whether the problem is grounding, flow, tone, or repetition

Do not rely only on subjective inspection if a contract test could have caught the issue earlier.

---

## 14. Output protocol for coding agents

When reporting work, use this structure:

### What was done

List concrete changes.

### Why it was done

Explain the failure or design goal.

### Evidence

Include:

* tests run
* smoke check result
* one example output if relevant

### Remaining issue

State what is still weak or uncertain.

### Next best step

Propose the next focused task, not a vague future direction.

This project should progress through small verified steps, not broad optimistic claims.

---

## 15. Done criteria

A task is only considered done when all are true:

* the intended module boundary is still clean
* imports and syntax work
* contract shape is preserved or explicitly updated
* at least one appropriate verification step was run
* results are recorded
* known limitations are acknowledged

"Code was written" is not a done condition.

---

## 16. Scope discipline

Prefer MVP-safe solutions first.

Good MVP choices:

* simple but explicit sequence linker
* limited sentiment set
* one revision pass
* interpretable evaluator

Avoid premature complexity such as:

* overly abstract plugin systems
* excessive configuration layers
* speculative generalization
* multi-provider architecture before needed

Build for extension, but implement for the current project.

---

## 17. UI discipline

UI should support trust and inspectability.

The user should be able to understand:

* what images were used
* what sentiment was selected
* what story was generated
* optionally, how the system interpreted the images

Debug information should be available in development or submission mode, but not forced into the final polished experience.

UI must not hide grounding failures behind attractive copy.

---

## 18. When unsure

If you are uncertain:

* make the smallest reasonable assumption
* state the assumption explicitly
* keep the change reversible
* avoid architecture-wide rewrites

If a question is not blocking, do not stop progress.
Proceed with a constrained best effort and record the uncertainty.

---

## 19. Repository success standard

This repository is successful when:

* future agents can continue without re-deriving the architecture
* modules remain replaceable
* prompts remain separable from business logic
* story generation remains traceable to image-derived observations
* the submission app stays thin and runnable
* the system improves through iteration rather than accidental complexity
