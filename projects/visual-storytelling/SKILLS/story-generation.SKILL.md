# story-generation.SKILL.md

## Purpose

This skill defines how the system should turn structured intermediate representations into the final short story.

This stage is the realization layer.
It should not be the hidden reasoning layer for everything else.

---

## When to read

Read this file before changing:
- story generation prompts
- story realization logic
- title generation logic
- sentence alignment behavior
- grounding note generation
- regeneration policies

---

## Responsibilities

The story generation stage must produce:
- one title
- one short story
- sentence-to-image alignment
- optional grounding notes

It must use:
- scene observations
- sequence memory
- narrative plan
- sentiment profile

---

## Non-responsibilities

This stage must not:
- re-infer the entire image understanding from scratch
- silently replace sequence logic
- define sentiment policy
- define evaluation policy
- hide unsupported story inventions behind fluent language

---

## Required input

The story generator expects:
- `SceneObservation[]`
- `SequenceMemory`
- `NarrativePlan`
- `SentimentProfile`
- optional max sentence constraint

---

## Required output

The required output contract is `StoryDraft`.

Fields:
- `title`
- `story_text`
- `sentence_alignment`
- `grounding_notes`

---

## Core generation policy

The story must:

1. follow image order
2. read as one story, not separate captions
3. reflect the selected sentiment
4. avoid major unsupported claims
5. preserve recurring entities consistently
6. stay short and readable

---

## Style versus truth rule

Sentiment affects:
- tone
- pacing
- phrasing
- ending style

Sentiment does not justify:
- unseen events
- new characters with no basis
- strong emotional backstory with no evidence
- major causal claims unsupported by the sequence

---

## Narrative bridge rule

The system may use light connective language such as:
- “after a while”
- “soon”
- “later that day”
- “before long”

These are allowed because they improve readability without inventing major plot events.

The system should avoid unsupported bridges like:
- “they remembered last summer”
- “they argued earlier”
- “the owner promised a reward”
unless explicitly grounded or clearly marked as soft inference and allowed by plan.

---

## Title policy

The title should be:
- short
- relevant
- sentiment-compatible
- grounded in the visible sequence

Good examples:
- “A Happy Walk Home”
- “Under the Quiet Tree”
- “A Small Mystery in the Park”

Bad examples:
- “The Secret of Their Lost Childhood”
- “A Destiny Written in the Stars”

---

## Sentence alignment rule

Each sentence or beat should align to one or more images.

Example:
```text
sentence 1 -> image 1
sentence 2 -> image 2
sentence 3 -> image 3
sentence 4 -> image 4
```

This makes the output:

* traceable
* debuggable
* easier to evaluate

---

## Common failure patterns

### 1. Caption chaining

The result reads like disconnected image captions.

### 2. Hallucinated plot

The story invents unsupported details for dramatic effect.

### 3. Entity drift

The same subject becomes multiple different subjects.

### 4. Sentiment overkill

The tone becomes too heavy and overwhelms the actual images.

### 5. Repetition

The story repeats the same visible fact in slightly different wording.

---

## Failure taxonomy for this stage

* `GROUNDING_ERROR`
* `SEQUENCE_FLOW_ERROR`
* `ENTITY_MEMORY_ERROR`
* `SENTIMENT_MISMATCH`
* `REDUNDANCY_ERROR`
* `PROMPT_CONTRACT_ERROR`

---

## Writing rules

The generated story should be:

* short
* natural
* coherent
* image-grounded
* sentiment-aware
* readable in one pass

Avoid:

* purple prose
* inflated symbolism
* excessive adjectives
* unexplained narrative jumps
* repetitive mention of the same object

---

## Regeneration policy

If regeneration is requested:

* do not mutate original observations in place
* keep the same factual foundation unless analysis is explicitly rerun
* allow style, rhythm, title, and sentence shape to change
* keep grounding constraints active

---

## Test expectations

At minimum, check:

### Contract-level

* `StoryDraft` fields present
* sentence alignment shape valid

### Qualitative

* story follows image order
* no obvious unsupported event
* sentiment is noticeable
* story sounds like one narrative
* repetition is limited

---

## Done criteria

A generation change is done when:

* the draft remains grounded
* the sequence is readable
* sentiment is present but controlled
* alignment data exists
* at least one smoke example was checked

---

## Notes for future agents

If the story output is weak, diagnose in this order:

1. scene observations weak?
2. sequence memory weak?
3. narrative plan weak?
4. sentiment profile weak?
5. generation prompt weak?
6. evaluator too permissive?

Do not assume the story prompt alone is the root problem.
