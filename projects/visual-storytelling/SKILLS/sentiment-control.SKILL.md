# sentiment-control.SKILL.md

## Purpose

This skill defines how user-selected sentiment is converted into structured narrative control settings.

This stage exists to keep tone control explicit and bounded.
It prevents raw sentiment labels from being handled loosely inside story generation.

---

## When to read

Read this file before changing:
- sentiment options
- sentiment profile mappings
- style control logic
- tone constraints
- regeneration style behavior

---

## Responsibilities

This stage must:
- accept a user-selected sentiment label
- translate it into a structured `SentimentProfile`
- define tone guidance for downstream generation
- preserve grounding constraints

---

## Non-responsibilities

This stage must not:
- analyze images
- decide overall sequence flow
- generate the final story by itself
- override factual constraints
- introduce story events

---

## Required input

Input:
- sentiment label chosen by the user

Optional input:
- strength or style mode in future versions

---

## Required output

The required output contract is `SentimentProfile`.

Fields:
- `label`
- `tone_keywords`
- `pacing_style`
- `sentence_style`
- `ending_style`
- `metaphor_tolerance`
- `inference_strictness`

---

## Design rule

Sentiment is a style layer, not a truth layer.

That means:
- it influences how the story sounds
- it does not justify inventing new facts

This rule is mandatory.

---

## Recommended baseline profiles

### happy
- tone_keywords: warm, bright, gentle, cheerful
- pacing_style: smooth
- sentence_style: clear and warm
- ending_style: affirming
- metaphor_tolerance: low-to-medium
- inference_strictness: strict

### sad
- tone_keywords: quiet, reflective, soft, subdued
- pacing_style: slower
- sentence_style: simple and reflective
- ending_style: restrained
- metaphor_tolerance: medium
- inference_strictness: strict

### suspenseful
- tone_keywords: tense, alert, uncertain, sharp
- pacing_style: brisk
- sentence_style: shorter and tighter
- ending_style: unresolved or lightly tense
- metaphor_tolerance: low
- inference_strictness: strict

### mysterious
- tone_keywords: quiet, curious, shadowed, uncertain
- pacing_style: controlled
- sentence_style: slightly suggestive but clear
- ending_style: open-ended
- metaphor_tolerance: medium
- inference_strictness: strict

### heartwarming
- tone_keywords: tender, gentle, comforting, sincere
- pacing_style: smooth
- sentence_style: warm and soft
- ending_style: emotionally satisfying
- metaphor_tolerance: low-to-medium
- inference_strictness: strict

### playful
- tone_keywords: lively, light, energetic, cheerful
- pacing_style: quick
- sentence_style: crisp and upbeat
- ending_style: smiling and light
- metaphor_tolerance: low
- inference_strictness: strict

---

## Constraints

All sentiment profiles must:
- preserve grounding priority
- avoid melodrama by default
- avoid genre conversion
- remain suitable for short-form story output

Example:
Selecting “mysterious” should not transform ordinary park photos into a crime thriller.

---

## Common failure patterns

### 1. Sentiment invisibility
The story sounds neutral even when sentiment is selected.

### 2. Sentiment dominance
The tone overwhelms the visible sequence.

### 3. Genre drift
A simple emotional tone gets converted into a full genre shift.

### 4. Inference inflation
Emotional control causes unsupported emotional claims.

---

## Failure taxonomy for this stage

- `SENTIMENT_MISMATCH`
- `GROUNDING_ERROR`
- `STYLE_OVERREACH_ERROR`
- `PROFILE_MAPPING_ERROR`
- `SCHEMA_DRIFT_ERROR`

---

## Implementation rules

1. sentiment mapping should be explicit
2. avoid magic style behavior hidden inside prompts only
3. keep profile fields stable and typed
4. profile changes should be documented
5. keep inference strictness high in MVP

---

## Test expectations

At minimum:
- valid label returns valid `SentimentProfile`
- unsupported label handled clearly
- profile fields are not missing
- two different sentiments produce meaningfully different style settings

Qualitative checks:
- happy should feel lighter than sad
- suspenseful should feel tighter than heartwarming
- mysterious should remain controlled, not wildly speculative

---

## Done criteria

A sentiment-control change is done when:
- profile output is valid
- tone differences are meaningful
- grounding protection remains intact
- at least one qualitative comparison was checked

---

## Notes for future agents

If sentiment control feels weak, first check:
1. profile too vague?
2. generation prompt ignoring profile?
3. evaluator not checking sentiment fit?
4. sentence structure too rigid?

Do not fix sentiment problems by allowing more hallucination.
