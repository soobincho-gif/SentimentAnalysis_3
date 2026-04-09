# image-analysis.SKILL.md

## Purpose

This skill defines how the system should analyze each uploaded image and convert it into a grounded structured observation.

This skill is about observable scene extraction.
It is not about storytelling yet.

---

## When to read

Read this file before changing:
- scene analysis logic
- image-to-JSON extraction prompts
- observation schemas
- image preprocessing behavior
- OCR extraction behavior

---

## Responsibilities

The image analysis stage must extract, per image:

- entities
- setting
- visible objects
- visible actions
- visible mood clues
- text in image if present
- uncertainty notes

The output must be reusable for:
- sequence linking
- narrative planning
- evaluation

---

## Non-responsibilities

This stage must not:
- generate the final story
- decide overall narrative arc
- invent hidden events
- over-interpret emotional meaning
- collapse multiple images into one summary

---

## Required input

Expected input:
- one preprocessed image
- stable image ID
- optional analysis config

Optional config may include:
- OCR enabled/disabled
- detail level
- strictness preference

---

## Required output

The required output contract is `SceneObservation`.

Expected fields:
- `image_id`
- `entities`
- `setting`
- `objects`
- `actions`
- `visible_mood`
- `text_in_image`
- `uncertainty_notes`

---

## Grounding rule

Only include details that are:
- clearly visible,
- weakly inferable from the image,
- or explicitly marked as uncertain.

Do not promote weak guesses into confident facts.

Bad:
- “the child is going to school”
Good:
- “a child wearing a backpack stands outdoors”
Better:
- “possibly a school setting, but uncertain”

---

## Output style rules

The observation must be:
- structured
- compact
- factual
- reusable
- traceable to image content

Avoid polished prose.
Avoid long descriptive paragraphs.
Prefer stable short fields.

---

## Recommended extraction questions

When analyzing an image, answer these internally:

1. who or what is present?
2. where does this appear to take place?
3. what objects are visible?
4. what actions are visible?
5. what mood cues are visible?
6. is there any text shown in the image?
7. what parts are uncertain?

These questions should guide extraction, but the final output must remain contract-shaped.

---

## Heuristics

### Entities
Prefer concrete recurring-friendly labels:
- “small brown dog”
- “young woman”
- “person in white shirt”

Avoid vague labels like:
- “someone”
- “thing”
- “animal” unless necessary

### Setting
Prefer observable setting phrases:
- “park”
- “living room”
- “street at night”
- “indoor cafe”

### Actions
Use visible actions, not inferred plans:
- “walking”
- “sitting”
- “holding a ball”
- “looking out the window”

### Visible mood
Mood should stay weakly descriptive:
- “calm”
- “playful”
- “tense”
- “quiet”

Avoid over-psychologizing:
- not “heartbroken”
- not “nostalgic about the past”
unless clearly supported

---

## Failure taxonomy for this stage

Use these labels when diagnosing problems:

- `GROUNDING_ERROR`
- `PROMPT_CONTRACT_ERROR`
- `OCR_EXTRACTION_ERROR`
- `OVERINTERPRETATION_ERROR`
- `MISSING_ENTITY_ERROR`
- `SCHEMA_DRIFT_ERROR`

### Examples

#### `GROUNDING_ERROR`
The observation lists an object not visible in the image.

#### `OVERINTERPRETATION_ERROR`
The analysis turns a weak visual clue into a strong narrative claim.

#### `MISSING_ENTITY_ERROR`
A recurring main subject is omitted from the observation.

---

## Implementation rules

1. image analysis must return typed output
2. prompt output must be parseable and stable
3. uncertainty must be represented explicitly
4. no story-like wording in this stage
5. image analysis and preprocessing should stay separate
6. OCR should not be tightly coupled to general entity extraction logic

---

## Test expectations

At minimum, this stage should be checked with:

### Unit or contract tests
- required fields exist
- empty lists default correctly
- parser handles missing optional values

### Qualitative checks
Verify on at least one sample:
- main subject captured
- setting plausible
- no major invented objects
- visible action captured
- uncertainty noted where appropriate

---

## Done criteria

This skill is done for a given change when:
- `SceneObservation` output is valid
- extraction remains grounded
- no story logic leaks into analysis
- test or smoke evidence exists
- failure cases are explicitly noted

---

## Notes for future agents

If the image analysis output quality is poor, do not immediately rewrite the whole pipeline.
Check in order:

1. preprocessing issue?
2. prompt issue?
3. schema too vague?
4. parser issue?
5. model call issue?

Fix the smallest cause first.
