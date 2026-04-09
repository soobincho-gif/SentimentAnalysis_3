# Data Contracts

## Purpose
This document defines the structured data contracts passed between pipeline stages.

The goal is to keep the system debuggable, grounded, and modular.
Each stage must consume explicit typed inputs and produce explicit typed outputs.

## Why this document exists
Visual storytelling systems become fragile when raw model outputs are passed loosely between components.
This project therefore uses structured contracts to separate:
- observable facts,
- sequence reasoning,
- sentiment control,
- story generation,
- evaluation.

## Contract design principles

### 1. Facts before narration
Contracts should represent observable image content before story-like interpretation.

### 2. Stable interfaces
Downstream modules should depend on stable schemas, not on prompt-specific text blobs.

### 3. Explicit uncertainty
If the model is unsure, the uncertainty should be represented in the contract rather than silently ignored.

### 4. Debuggable intermediate states
Intermediate outputs should be inspectable in the submission UI and during development.

---

## Pipeline contract map

```text
OrderedImageSet
  -> SceneObservation[]
  -> SequenceMemory
  -> NarrativePlan
  -> SentimentProfile
  -> StoryDraft
  -> EvaluationReport
  -> StoryResult
```

---

## 1. OrderedImageSet

### Purpose

Represents the user-uploaded images in the exact order intended for storytelling.

### Fields

* `image_paths: list[str]`
* `original_filenames: list[str] | None`
* `total_images: int`

### Rules

* order must be preserved
* all downstream stages assume this order is meaningful
* image IDs are assigned based on this order

---

## 2. SceneObservation

### Purpose

Represents grounded observable information extracted from one image.

### Fields

* `image_id: int`
* `entities: list[str]`
* `setting: str | None`
* `objects: list[str]`
* `actions: list[str]`
* `visible_mood: str | None`
* `text_in_image: list[str]`
* `uncertainty_notes: list[str]`
* `same_subject_as_previous: bool | None`

### Example

```json
{
  "image_id": 1,
  "entities": ["small brown dog", "owner"],
  "setting": "park",
  "objects": ["leash", "grass", "tree"],
  "actions": ["walking", "looking around"],
  "visible_mood": "playful",
  "text_in_image": [],
  "uncertainty_notes": [],
  "same_subject_as_previous": null
}
```

### Rules

* should only describe what is visible or weakly inferable
* should not contain full story sentences
* must remain reusable for planning and evaluation
* continuity confirmation may be left unset unless the user explicitly corrects it

---

## 3. SceneObservationOverride

### Purpose

Represents a bounded user correction layered onto the analyzed observation before sequence linking.

### Fields

* `image_id: int`
* `main_entity: str | None`
* `setting: str | None`
* `visible_action: str | None`
* `same_subject_as_previous: bool | None`
* `generation_note: str | None`

### Rules

* overrides must stay explicit and typed
* blank fields mean "keep the current analysis"
* overrides are authoritative over ambiguous scene analysis for the next corrected generation

---

## 4. SequenceMemory

### Purpose

Stores cross-image continuity and sequence-level reasoning.

### Fields

* `recurring_entities: list[str]`
* `setting_progression: list[str]`
* `event_candidates: list[str]`
* `unresolved_ambiguities: list[str]`

### Example

```json
{
  "recurring_entities": ["dog_1", "owner_1"],
  "setting_progression": ["park path", "tree shade", "open lawn", "walk home"],
  "event_candidates": [
    "a walk begins",
    "the dog pauses to rest",
    "the dog plays with a ball",
    "the pair return home"
  ],
  "unresolved_ambiguities": []
}
```

### Rules

* memory should prefer continuity over fragmentation
* unresolved ambiguity must be recorded, not hidden
* event candidates are not final narrative sentences

---

## 5. NarrativePlan

### Purpose

Converts observations and memory into a constrained story blueprint.

### Fields

* `arc_type: str`
* `beat_list: list[str>`
* `sentence_image_map: list[list[int]]`
* `allowed_inferences: list[str>`
* `forbidden_claims: list[str>`
* `title_candidates: list[str>`

### Example

```json
{
  "arc_type": "simple chronological slice-of-life",
  "beat_list": [
    "begin the walk",
    "pause under the tree",
    "find and fetch the ball",
    "end with a warm return home"
  ],
  "sentence_image_map": [[1], [2], [3], [4]],
  "allowed_inferences": [
    "later that day",
    "after a short rest"
  ],
  "forbidden_claims": [
    "the dog speaks",
    "it starts raining",
    "a new unseen character appears"
  ],
  "title_candidates": [
    "A Happy Walk Home",
    "An Afternoon in the Park"
  ]
}
```

### Rules

* the plan may guide narrative flow
* the plan must not introduce unsupported major events
* every beat should remain traceable to one or more images

---

## 6. SentimentProfile

### Purpose

Represents the user-selected emotional mode as narrative control settings.

### Fields

* `label: str`
* `tone_keywords: list[str>`
* `pacing_style: str`
* `sentence_style: str`
* `ending_style: str`
* `metaphor_tolerance: str`
* `inference_strictness: str`

### Example

```json
{
  "label": "happy",
  "tone_keywords": ["warm", "bright", "gentle", "cheerful"],
  "pacing_style": "smooth",
  "sentence_style": "clear and warm",
  "ending_style": "affirming",
  "metaphor_tolerance": "low-to-medium",
  "inference_strictness": "strict"
}
```

### Rules

* sentiment affects style, not truth
* sentiment must not override grounding constraints

---

## 7. StoryDraft

### Purpose

Represents the generated story before or after evaluation.

### Fields

* `title: str`
* `story_text: str`
* `sentence_alignment: list[list[int]]`
* `grounding_notes: list[str]`

### Example

```json
{
  "title": "A Happy Walk Home",
  "story_text": "On a bright afternoon, the little dog trotted through the park with eager steps. ...",
  "sentence_alignment": [[1], [2], [3], [4]],
  "grounding_notes": [
    "dog and owner visible across multiple images",
    "ball mentioned only where visually supported"
  ]
}
```

### Rules

* the text should read naturally as one short story
* sentence alignment must preserve traceability to image order
* grounding notes should explain major evidence-backed choices

---

## 8. EvaluationReport

### Purpose

Represents quality checks applied to the generated story.

### Fields

* `grounding_score: float`
* `coherence_score: float`
* `redundancy_score: float`
* `sentiment_fit_score: float`
* `readability_score: float`
* `flags: list[str]`
* `summary: str`
* `sentiment_audit: SentimentAudit | None`

### Example

```json
{
  "grounding_score": 0.91,
  "coherence_score": 0.88,
  "redundancy_score": 0.94,
  "sentiment_fit_score": 0.90,
  "readability_score": 0.87,
  "flags": [],
  "summary": "The story remains grounded, flows chronologically, and matches the selected happy tone.",
  "sentiment_audit": {
    "target_sentiment": "happy",
    "matched_keywords": ["warm", "bright"],
    "missing_keywords": ["gentle", "cheerful"],
    "matched_style_cues": ["warm wording", "affirming close"],
    "missing_style_cues": ["smooth pacing"],
    "score": 0.81,
    "summary": "The draft expresses happy clearly through warm, bright, warm wording."
  }
}
```

### Rules

* scores are guidance, not absolute truth
* flags must be specific enough to support revision
* if a failure is detected, the failure category should be traceable
* `sentiment_audit` should explain which tone cues were actually detected and which ones remain weak

---

## 9. SentimentAudit

### Purpose

Represents a deterministic audit trail for how clearly the generated draft expresses the selected sentiment.

### Fields

* `target_sentiment: str`
* `matched_keywords: list[str]`
* `missing_keywords: list[str]`
* `matched_style_cues: list[str]`
* `missing_style_cues: list[str]`
* `score: float`
* `summary: str`

### Rules

* this audit is support evidence, not a replacement for full evaluation
* it should remain explainable enough to debug local fallback behavior
* it should never justify adding unsupported visual claims just to raise tone scores

---

## 10. StoryRequest

### Purpose

Represents the top-level input to the pipeline.

### Fields

* `image_paths: list[str]`
* `sentiment: str`
* `max_sentences: int`
* `include_debug: bool`
* `analysis_overrides: list[SceneObservationOverride]`
* `generation_mode: str`

### Rules

* `max_sentences` must be a positive integer
* the UI may allow any positive sentence count, but generation may still stop earlier if the image evidence or plan does not support a longer grounded story

---

## 11. StoryResult

### Purpose

Represents the final pipeline output returned to UI or API.

### Fields

* `title: str`
* `story_text: str`
* `original_scene_observations: list[SceneObservation]`
* `scene_observations: list[SceneObservation]`
* `sequence_memory: SequenceMemory | None`
* `narrative_plan: NarrativePlan | None`
* `evaluation_report: EvaluationReport | None`
* `sentence_alignment: list[list[int]]`
* `grounding_notes: list[str]`
* `provider_status: list[ProviderStageStatus]`
* `applied_overrides: list[SceneObservationOverride]`
* `generation_mode: str`

### Rules

* this object is the submission-facing result
* it should contain enough detail for debugging and demonstration
* it should not expose raw provider-specific payloads
* sentence alignment and grounding notes should remain available for trust-focused UI presentation
* provider status should expose stage, execution mode, fallback cause, and recovery hint without exposing raw SDK payloads
* applied overrides and generation mode should remain visible for trust and regeneration transparency
* original and effective observations should both remain available when the UI needs a comparison view

---

## 11. Recommended Pydantic model layout

```text
packages/core/models/
  scene.py
  correction.py
  sequence.py
  sentiment.py
  sentiment_audit.py
  story.py
  evaluation.py
```

---

## 12. Suggested Python model skeleton

```python
from pydantic import BaseModel, Field
from typing import List, Optional


class SceneObservation(BaseModel):
    image_id: int
    entities: List[str] = Field(default_factory=list)
    setting: Optional[str] = None
    objects: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    visible_mood: Optional[str] = None
    text_in_image: List[str] = Field(default_factory=list)
    uncertainty_notes: List[str] = Field(default_factory=list)
    same_subject_as_previous: Optional[bool] = None


class SceneObservationOverride(BaseModel):
    image_id: int
    main_entity: Optional[str] = None
    setting: Optional[str] = None
    visible_action: Optional[str] = None
    same_subject_as_previous: Optional[bool] = None
    generation_note: Optional[str] = None


class SequenceMemory(BaseModel):
    recurring_entities: List[str] = Field(default_factory=list)
    setting_progression: List[str] = Field(default_factory=list)
    event_candidates: List[str] = Field(default_factory=list)
    unresolved_ambiguities: List[str] = Field(default_factory=list)


class NarrativePlan(BaseModel):
    arc_type: str
    beat_list: List[str] = Field(default_factory=list)
    sentence_image_map: List[List[int]] = Field(default_factory=list)
    allowed_inferences: List[str] = Field(default_factory=list)
    forbidden_claims: List[str] = Field(default_factory=list)
    title_candidates: List[str] = Field(default_factory=list)


class SentimentProfile(BaseModel):
    label: str
    tone_keywords: List[str] = Field(default_factory=list)
    pacing_style: str
    sentence_style: str
    ending_style: str
    metaphor_tolerance: str
    inference_strictness: str


class SentimentAudit(BaseModel):
    target_sentiment: str
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    matched_style_cues: List[str] = Field(default_factory=list)
    missing_style_cues: List[str] = Field(default_factory=list)
    score: float
    summary: str


class EvaluationReport(BaseModel):
    grounding_score: float
    coherence_score: float
    redundancy_score: float
    sentiment_fit_score: float
    readability_score: float
    flags: List[str] = Field(default_factory=list)
    summary: str
    sentiment_audit: Optional[SentimentAudit] = None


class ProviderStageStatus(BaseModel):
    stage: str
    execution_mode: str = "provider"
    reason: Optional[str] = None
    recovery_hint: Optional[str] = None


class StoryRequest(BaseModel):
    image_paths: List[str]
    sentiment: str
    max_sentences: int = 5
    include_debug: bool = True
    analysis_overrides: List[SceneObservationOverride] = Field(default_factory=list)
    generation_mode: str = "default"


class StoryResult(BaseModel):
    title: str
    story_text: str
    original_scene_observations: List[SceneObservation] = Field(default_factory=list)
    scene_observations: List[SceneObservation] = Field(default_factory=list)
    sequence_memory: Optional[SequenceMemory] = None
    narrative_plan: Optional[NarrativePlan] = None
    evaluation_report: Optional[EvaluationReport] = None
    sentence_alignment: List[List[int]] = Field(default_factory=list)
    grounding_notes: List[str] = Field(default_factory=list)
    provider_status: List[ProviderStageStatus] = Field(default_factory=list)
    applied_overrides: List[SceneObservationOverride] = Field(default_factory=list)
    generation_mode: str = "default"
```

---

## 13. Boundary rule

No module may silently change the meaning of a contract field.
If a contract changes:

1. update this document,
2. update the model definition,
3. update the dependent services,
4. update contract tests.

This rule exists to prevent drift between planning, implementation, and evaluation.
