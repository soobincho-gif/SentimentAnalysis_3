# System Architecture

- Purpose: Define the high-level system decomposition and dependency direction for the MVP.
- Owner: Tech lead.
- When to read: Before implementing the backend, services, package boundaries, or cross-layer contracts.
- Decisions that belong here: Component responsibilities, data flow, integration points, and extension paths.

## 1. Why This Architecture Exists

This project is not a simple image captioning system. It is a visual storytelling system that must generate a short story from an ordered sequence of user-uploaded images while reflecting a chosen sentiment. Prior work on visual storytelling shows that the problem is harder than captioning because the system must maintain cross-image coherence, connect events across time, keep characters and settings consistent, and still remain grounded in visible content.

The architecture follows four research-backed lessons:

- distinguish visually observable facts from the narrative ultimately told,
- maintain explicit memory across images for recurring entities and settings,
- inject style or sentiment without overwhelming grounding,
- evaluate grounding, coherence, and redundancy as separate quality dimensions.

This leads to a staged pipeline rather than a one-shot generator:

1. input and preprocessing,
2. observable world extraction,
3. sequence memory and linking,
4. narrative planning,
5. sentiment-controlled generation,
6. evaluation and revision.

## 2. Architecture Principles

### 2.1 Separate Facts From Narration

The system must never jump straight from raw images to final prose without first extracting structured observable facts. Facts and narration are different layers, and collapsing them makes hallucinations harder to detect and debug.

### 2.2 Preserve Cross-Image Memory

The system must track recurring people, animals, objects, and settings across images. Visual storytelling quality depends heavily on continuity, so entity memory is a first-class architectural concern rather than a hidden prompt trick.

### 2.3 Control Sentiment As Style, Not As Truth

Sentiment should shape tone, pacing, word choice, and emotional framing, but should not invent unsupported events. Style and grounding are competing goals and must be balanced explicitly.

### 2.4 Build Evaluation Into The Loop

A fluent story is not necessarily grounded, and a grounded story is not necessarily coherent. Evaluation must therefore live inside the pipeline, not after it.

## 3. High-Level System Flow

```text
User Uploads Images + Sentiment
        ↓
Input Validator / Image Preprocessor
        ↓
Scene Analyzer (per image)
        ↓
Sequence Linker + Entity Memory Builder
        ↓
Narrative Planner
        ↓
Sentiment Controller
        ↓
Story Draft Generator
        ↓
Grounding / Coherence / Redundancy Evaluator
        ↓
Revision Loop
        ↓
Final Story + Traceable Story Metadata
```

## 4. Component Design

### 4.1 Input Validator And Preprocessor

Responsibilities:

- accept multiple uploaded images in user-defined order,
- validate file type and file size,
- normalize image orientation and format,
- preserve user order as the default temporal order,
- generate stable internal image IDs.

Outputs:

- `OrderedImageSet`
- `ImageMetadata`
- `PreprocessingReport`

Why this exists:

Visual storytelling is defined over an ordered image sequence, not an unordered set. If order is lost, the story flow collapses.

### 4.2 Scene Analyzer

Responsibilities:

- extract structured scene descriptions from each image,
- capture characters, settings, objects, actions, visible mood cues, OCR text, and uncertainty notes,
- produce structured facts rather than polished prose.

Output schema:

```text
SceneObservation
- image_id
- entities[]
- setting
- objects[]
- actions[]
- visible_mood
- text_in_image[]
- uncertainty_notes[]
```

Why this exists:

Downstream planning and evaluation need a stable factual layer before they can reason about story shape.

### 4.3 Sequence Linker And Entity Memory Builder

Responsibilities:

- link recurring entities across images,
- infer setting continuity when reasonable,
- build event transitions between adjacent frames,
- identify likely beginning, middle, and ending roles,
- mark ambiguity when continuity is weak.

Output schema:

```text
SequenceMemory
- entities_by_id
- recurring_entities[]
- setting_progression[]
- event_candidates[]
- unresolved_ambiguities[]
```

Why this exists:

Consistency across scenes is a known failure point in visual storytelling. Entity memory makes those failures inspectable.

### 4.4 Narrative Planner

Responsibilities:

- transform scene-level facts into a minimal story plan,
- define story arc and sentence-to-image alignment,
- mark safe details, light bridges, allowed inferences, and forbidden claims.

Core rule:

The planner may introduce light bridging language such as "later" or "after a while," but should avoid inventing major unseen events unless explicitly marked as soft inference.

Output schema:

```text
NarrativePlan
- title_candidates[]
- arc_type
- beat_list[]
- sentence_image_map[]
- allowed_inferences[]
- forbidden_claims[]
```

### 4.5 Sentiment Controller

Responsibilities:

- translate the chosen sentiment into lexical tone, pacing, emotional framing, ending style, and inference strictness,
- shape how the story sounds without changing what is visually true.

Example mapping:

- `happy`: warmer verbs, smoother transitions, affirmative ending
- `sad`: quieter pacing, reflective tone, softer closure
- `suspenseful`: shorter beats, delayed certainty, sharper transitions
- `mysterious`: restrained explanation, lingering ending, controlled ambiguity

### 4.6 Story Draft Generator

Responsibilities:

- generate the actual short story from `SceneObservation[]`, `SequenceMemory`, `NarrativePlan`, and `SentimentProfile`,
- preserve image order,
- prioritize grounded details,
- avoid unsupported nouns, events, and repetitive mentions.

Output schema:

```text
StoryDraft
- title
- story_text
- sentence_alignment[]
- grounding_notes[]
```

Why this exists:

The generator should be the realization layer, not the reasoning layer. If all reasoning lives inside one prompt, debugging and revision become unreliable.

### 4.7 Evaluator And Revision Loop

Responsibilities:

- evaluate grounding, coherence, and redundancy,
- also check sentiment fit and readability,
- trigger targeted revision when unsupported details, entity drift, temporal breaks, repetition, or tone mismatch appear.

Revision triggers:

- unsupported object or event,
- entity inconsistency,
- broken temporal flow,
- excessive repetition,
- sentiment too weak or too dominant.

Why this exists:

Visual storytelling quality is multi-dimensional. Evaluation should guide revision, but should not be treated as a perfect oracle.

## 5. Data Contracts

Required domain models:

- `OrderedImageSet`
- `SceneObservation`
- `SequenceMemory`
- `NarrativePlan`
- `SentimentProfile`
- `StoryDraft`
- `EvaluationReport`
- `RevisionDecision`

Rule:

No downstream component should read raw uploaded images directly if an upstream structured representation already exists for the same purpose.

## 6. Recommended Python Package Boundaries

```text
apps/
  api/
    main.py
    routes/
    schemas/
packages/
  core/
    models/
    rules/
  services/
    image_preprocessing/
    scene_analysis/
    sequence_linking/
    narrative_planning/
    sentiment_control/
    story_generation/
    evaluation/
    revision/
  prompts/
    scene_analysis/
    planning/
    generation/
    evaluation/
  infra/
    openai_client/
    file_storage/
    logging/
    config/
submission/
  app.py
```

Boundary rule:

- `core` contains domain models and pure rules,
- `services` orchestrates business flow,
- `prompts` stores prompt assets and prompt contracts,
- `infra` handles provider clients, storage, config, and logging,
- `apps/api` exposes transport,
- `submission/app.py` stays as a thin coursework-facing entrypoint.

## 7. Dependency Direction

```text
apps/api -> services -> core
services -> prompts
services -> infra
infra never imports apps/api
core never imports services or infra
submission -> services
submission -> infra
```

Why this matters:

If prompt logic, routing, domain policy, and revision behavior blend together, the system becomes impossible to evaluate component by component.

## 8. Iterative Build Loop For AI Coding Agents

Each implementation cycle must follow this order:

1. design,
2. attempt,
3. evaluate,
4. revise,
5. record decision.

### Design

State:

- what component is changing,
- its expected input and output contract,
- likely failure modes,
- how success will be checked.

### Attempt

Implement only one component or one integration boundary at a time.

### Evaluate

Run:

- unit tests,
- contract tests,
- at least one end-to-end smoke test with 3 to 5 images when available,
- qualitative checks for grounding, coherence, and sentiment fit.

### Revise

Fix the detected failure category before broadening scope.

### Record Decision

Write a short note in `docs/05_decisions/` or `projects/visual-storytelling/TASKS.md` if boundaries or expectations changed.

## 9. MVP Scope

The MVP should support:

- multiple image upload,
- user-controlled image order,
- one sentiment selection,
- grounded short story output,
- one-pass evaluation,
- one regeneration flow.

The MVP should not yet include:

- long storybooks,
- multi-user collaboration,
- voice narration,
- advanced character editing,
- automatic album sorting without user confirmation.

## 10. Primary Risks

- Hallucinated story details
  Mitigation: factual observation layer, forbidden claims list, evaluator
- Same character treated as different entities
  Mitigation: explicit entity memory
- Sentiment overwhelms grounding
  Mitigation: style controller separated from fact extraction
- Beautiful but repetitive text
  Mitigation: redundancy checks in evaluator
- Hard-to-debug generation failures
  Mitigation: structured intermediates and isolated package boundaries

## 11. Success Criteria

A generated story is acceptable when:

- it follows image order,
- it preserves major recurring entities,
- it does not invent major unsupported events,
- it clearly reflects the selected sentiment,
- it reads like one coherent short story instead of separate captions.

## Sources

- [Visual Storytelling (Huang et al., NAACL 2016)](https://aclanthology.org/N16-1147.pdf)
- [SEE&TELL: Controllable Narrative Generation from Images](https://openreview.net/pdf?id=_8Ity3P03Z1)
- [Make-a-Story: Visual Memory Conditioned Consistent Story Generation (CVPR 2023)](https://openaccess.thecvf.com/content/CVPR2023/papers/Rahman_Make-a-Story_Visual_Memory_Conditioned_Consistent_Story_Generation_CVPR_2023_paper.pdf)
- [Image-grounded controllable stylistic story generation](https://aclanthology.org/2022.latechclfl-1.6.pdf)
- [RoViST: Learning Robust Metrics for Visual Storytelling](https://aclanthology.org/2022.findings-naacl.206/)
- [Imagine, Reason and Write: Visual Storytelling with Graph Knowledge](https://cdn.aaai.org/ojs/16410/16410-13-19904-1-2-20210518.pdf)
