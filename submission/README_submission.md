# Visual Storytelling Submission Guide

## What this project does
This project generates a short story from multiple user-uploaded images and a selected sentiment.

The system:
1. analyzes each uploaded image,
2. extracts observable scene information,
3. links the images into a coherent sequence,
4. applies the selected sentiment as narrative tone,
5. generates a short grounded story,
6. evaluates the story for grounding and coherence.

## Submission entrypoint
The coursework-facing entrypoint is:

```bash
python submission/app.py
```

This launches a lightweight Python UI for:

* uploading multiple images,
* selecting a sentiment,
* generating a short story,
* reviewing intermediate reasoning outputs.

## Why the submission app is thin

The submission file is intentionally thin.
Core logic is implemented in reusable modules under `packages/`.

This avoids:

* business logic being mixed into UI code,
* duplicated prompt logic,
* hard-to-debug spaghetti code,
* difficulty extending the project later.

## Expected project structure

```text
submission/
  app.py
  README_submission.md

packages/
  core/
  services/
  prompts/
  infra/
```

## Core pipeline stages

The system runs the following stages:

1. Image preprocessing
2. Scene analysis
3. Sequence linking
4. Narrative planning
5. Sentiment control
6. Story generation
7. Evaluation
8. Optional revision

## Inputs

* multiple images
* one selected sentiment

Supported example sentiments:

* happy
* sad
* suspenseful
* mysterious
* heartwarming
* playful

## Outputs

The app returns:

* generated title
* generated short story
* scene observations per image
* sequence memory summary
* evaluation summary

## Grounding policy

The story should remain grounded in visible image content.

The system may use light narrative bridges such as:

* "after a while"
* "later that day"
* "soon"

However, it should avoid inventing major unsupported facts.

## Running the project

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional environment variables

If you later swap the MVP stubs for a provider-backed analyzer or generator, create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

The current MVP-safe implementation runs without requiring the key.

### 4. Run the app

```bash
python submission/app.py
```

## Notes for markers / reviewers

* The UI layer is intentionally simple.
* The main design goal is architectural clarity and grounded multimodal storytelling.
* The internal package structure separates facts, sequence reasoning, sentiment control, generation, and evaluation.
* The submission app demonstrates the full end-to-end pipeline in a coursework-friendly format.

## Known limitations

* Entity linking across images is heuristic in the MVP.
* Story quality depends on image clarity and prompt quality.
* Sentiment control is intentionally constrained so that tone does not override grounding.
* The current stage implementations are deterministic MVP stubs, not full multimodal model integrations.

## Future extensions

* richer UI
* multiple storytelling modes
* bilingual output
* downloadable story cards
* stronger evaluation metrics
* improved character consistency across images
