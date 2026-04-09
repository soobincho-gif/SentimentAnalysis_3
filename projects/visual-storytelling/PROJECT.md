# PROJECT.md

## 1. Project name
Visual Storytelling from Images + Sentiment

---

## 2. Purpose

This project builds a Python-based system that generates a short story from multiple user-uploaded images and a selected sentiment.

The system must:
- accept multiple ordered images,
- analyze visible content in each image,
- link the images into a coherent sequence,
- apply the selected sentiment as tone and style,
- generate a short grounded story,
- support future UI refinement and regeneration.

This project is not a generic image captioning demo.
It is a structured visual storytelling system.

---

## 3. Product objective

The user experience should feel like this:

1. upload several images
2. choose a sentiment
3. generate a short story that follows the image order naturally
4. optionally inspect how the system interpreted the images
5. regenerate or refine the output later

The resulting story should feel:
- coherent,
- emotionally aligned,
- grounded in visible image content,
- short enough to be pleasant to read,
- traceable enough to debug.

---

## 4. Core problem statement

Naive multimodal prompting tends to produce one of these bad outcomes:

- separate captions instead of one story
- overly generic storytelling
- unsupported invented details
- broken flow across images
- sentiment overpowering truth
- inconsistent recurring entities

This project exists to solve that by separating the pipeline into:
- scene observation
- sequence memory
- narrative planning
- sentiment control
- story generation
- evaluation

---

## 5. In scope

### MVP scope
- multiple image upload
- image order preserved
- one selected sentiment
- scene-level image analysis
- sequence linking across images
- short story generation
- basic evaluation
- thin Python submission UI
- optional debug visibility for intermediate outputs

### Later scope
- richer UI
- regeneration controls
- bilingual output
- downloadable story card
- character editing / naming
- alternative writing modes
- stronger evaluation metrics

---

## 6. Out of scope for MVP

- long-form storybooks
- automatic album sorting without user confirmation
- full collaboration features
- advanced media editing
- production-grade authentication
- heavy analytics stack
- multi-provider orchestration unless needed

---

## 7. Primary users

### User type A: coursework/demo user
Needs:
- a working Python app
- clear input/output
- understandable architecture
- stable demo experience

### User type B: evaluator / marker
Needs:
- clarity of structure
- visible architectural reasoning
- a runnable Python entrypoint
- evidence that the system is more than a single prompt

### User type C: future developer or coding agent
Needs:
- explicit contracts
- clear module boundaries
- easy continuation without re-deriving intent
- non-spaghetti repository structure

---

## 8. User input

The system accepts:
- multiple images
- selected sentiment
- optional max sentence length
- optional debug mode

### Example sentiments
- happy
- sad
- suspenseful
- mysterious
- heartwarming
- playful

---

## 9. Expected output

The system should return:
- a story title
- a short story
- optional scene observations
- optional sequence memory summary
- optional evaluation summary

A strong output should:
- follow image order,
- preserve recurring entities,
- avoid major unsupported claims,
- reflect the selected sentiment,
- read like one short story rather than separate captions.

---

## 10. Success criteria

This project is successful when:

### Technical success
- the app runs from a Python entrypoint
- contracts are explicit
- pipeline stages are separated
- prompts are separated from service logic
- the system is testable

### Product success
- the story feels coherent
- the story tone matches the selected sentiment
- the story remains grounded
- debug information helps explain the result

### Repository success
- future coding agents can continue cleanly
- docs and code remain aligned
- changes can be made module-by-module

---

## 11. Architecture summary

```text
ordered images
  -> scene observations
  -> sequence memory
  -> narrative plan
  -> sentiment profile
  -> story draft
  -> evaluation report
  -> final story result
```

### Why this architecture

We explicitly separate:

* what is visible,
* how images connect,
* how the story is planned,
* how the tone is controlled,
* how the draft is evaluated.

This is required to reduce hallucination, improve coherence, and keep the system debuggable.

---

## 12. Core design rules

1. Facts before narration
2. Sequence matters
3. Sentiment is style, not truth
4. Evaluation is part of generation
5. Submission file must stay thin
6. Business logic must stay out of UI wrappers
7. Typed contracts must define major stage boundaries

---

## 13. Key repository locations

```text
submission/
  app.py

packages/core/
  typed domain models and rules

packages/services/
  pipeline stage orchestration

packages/prompts/
  prompt assets and contracts

packages/infra/
  bootstrap, config, external model access

docs/
  planning, architecture, decisions

projects/visual-storytelling/
  project-specific execution docs
```

---

## 14. Main risks

* hallucinated story details
* inconsistent recurring entities
* sentiment mismatch
* repetitive writing
* fragile prompt outputs
* schema drift between docs and code
* business logic leaking into submission app

---

## 15. Delivery strategy

The project should be built in small loops:

1. define or inspect contract
2. implement one stage
3. verify with narrow test
4. run one smoke flow
5. inspect output
6. record what broke
7. revise

Do not attempt broad “improve everything” changes.

---

## 16. Definition of done

A feature or task is done only when:

* module boundary is still clean
* contract is clear
* code runs
* at least one appropriate verification step exists
* the result is recorded in docs or task log
* known limitation is acknowledged

---

## 17. Current MVP target

The first strong MVP should demonstrate:

* multiple image upload
* sentiment selection
* story generation
* visible intermediate pipeline outputs
* grounded and readable short story
* Python-first coursework submission path
