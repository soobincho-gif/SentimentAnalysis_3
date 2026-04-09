# ui-flow.SKILL.md

## Purpose

This skill defines how the user-facing Python UI should expose the visual storytelling pipeline.

The UI is not the place for business logic.
Its job is to make the flow understandable, usable, and inspectable.

---

## When to read

Read this file before changing:
- submission/app.py
- UI state flow
- upload interactions
- sentiment selector behavior
- debug visibility
- result presentation
- regeneration entrypoints

---

## Responsibilities

The UI must allow the user to:

1. upload multiple images
2. choose a sentiment
3. trigger story generation
4. see the generated title and story
5. optionally inspect intermediate outputs

The UI should make the system feel:
- simple
- trustworthy
- easy to demo
- easy to inspect

---

## Non-responsibilities

The UI must not:
- contain core business logic
- define sequence reasoning policy
- define grounding rules
- embed long prompts
- become the real home of the pipeline

The UI is an entry and display layer.

---

## Current submission target

The coursework-facing app is Python-first.

Preferred submission mode:
- `python submission/app.py`

Recommended implementation:
- thin Gradio wrapper

Why:
- simple Python launch
- multiple image upload support
- fast demo cycle
- easy display of debug information

---

## Required UI flow

### Step 1: Upload
The user uploads multiple images.

Rules:
- preserve selected order where possible
- handle empty submission safely
- show clear label for uploaded inputs

### Step 2: Sentiment selection
The user chooses one sentiment.

Rules:
- show a limited stable set
- avoid too many options in MVP
- keep default sensible

### Step 3: Story generation
The user presses a clear action button.

Rules:
- show loading state
- do not silently fail
- handle missing API key or invalid input clearly

### Step 4: Result display
The user sees:
- title
- story

### Step 5: Optional debug inspection
The user may expand:
- scene observations
- sequence memory
- evaluation report

This is important for trust and coursework demonstration.

---

## UI state rules

The UI should clearly separate:
- inputs
- generation action
- main output
- debug output
- error state

Avoid mixing all information into one dense panel.

---

## Error handling rules

The UI must display clear errors for:
- no image uploaded
- missing API key
- invalid sentiment
- pipeline failure
- provider call failure

Errors should be:
- specific
- readable
- non-technical where possible
- still useful for debugging in development

---

## Debug visibility rule

Intermediate outputs should be available, but optional.

Why:
- markers may want to inspect reasoning
- developers need traceability
- polished users may not want clutter

So:
- debug visibility should be behind accordion/expandable areas
- debug mode should not replace the main experience

---

## Regeneration rule

For MVP, full regeneration controls may be limited.
But UI design should leave room for:
- regenerate story
- adjust sentiment
- possibly change sentence count
- later refine style

This should be achievable without redesigning the whole interface.

---

## Result presentation rule

The main result area should prioritize:
1. title
2. story text

Then secondary details:
3. scene observations
4. sequence memory
5. evaluation report

Do not overwhelm the user before they even read the story.

---

## Common failure patterns

### 1. Logic leakage
Business rules end up inside UI callbacks.

### 2. Debug clutter
The interface shows too much intermediate detail by default.

### 3. Thin output trust gap
Only showing final story makes the system feel magical but untrustworthy.

### 4. State confusion
Old output remains after new input changes.

### 5. Error opacity
Failures are swallowed or shown as generic crashes.

---

## Failure taxonomy for this stage

- `UI_STATE_ERROR`
- `API_INTEGRATION_ERROR`
- `INPUT_VALIDATION_ERROR`
- `DEBUG_VISIBILITY_ERROR`
- `RESULT_RENDER_ERROR`

---

## Implementation rules

1. keep submission/app.py thin
2. move business logic into pipeline and services
3. UI callbacks may orchestrate, not decide policy
4. state must remain understandable
5. errors should surface clearly
6. output sections should be visually separated

---

## Test expectations

At minimum:
- empty image input handled safely
- valid input triggers pipeline call
- story output renders
- debug outputs render when enabled
- failure displays message instead of crashing silently

Manual smoke check:
- upload 3 to 5 images
- select sentiment
- generate result
- inspect debug accordions
- verify story visible first

---

## Done criteria

A UI-flow change is done when:
- the UI remains thin
- the pipeline is still called through a clean boundary
- user can complete the basic flow
- errors are understandable
- debug info is inspectable but not overwhelming

---

## Notes for future agents

If the UI becomes messy, diagnose in this order:

1. too much logic in callback?
2. missing output separation?
3. state not reset properly?
4. debug panel too prominent?
5. submission constraints ignored?

Do not solve UI problems by moving more logic into the UI.
