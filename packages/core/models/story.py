from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import NarrativePlan, SequenceMemory

DEFAULT_GENERATION_MODE = "default"
STRICT_GROUNDING_GENERATION_MODE = "strict_grounding"
SUPPORTED_GENERATION_MODES = (
    DEFAULT_GENERATION_MODE,
    STRICT_GROUNDING_GENERATION_MODE,
)
PROVIDER_EXECUTION_MODE_PROVIDER = "provider"
PROVIDER_EXECUTION_MODE_LOCAL_FALLBACK = "local_fallback"
SUPPORTED_PROVIDER_EXECUTION_MODES = (
    PROVIDER_EXECUTION_MODE_PROVIDER,
    PROVIDER_EXECUTION_MODE_LOCAL_FALLBACK,
)


class StoryDraft(BaseModel):
    """Draft story artifact produced before final packaging."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    story_text: str = Field(min_length=1)
    sentence_alignment: list[list[int]] = Field(default_factory=list)
    grounding_notes: list[str] = Field(default_factory=list)


class StoryRequest(BaseModel):
    """Top-level pipeline input."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    image_paths: list[str] = Field(min_length=1)
    sentiment: str = Field(min_length=1)
    max_sentences: int = Field(default=5, ge=1)
    include_debug: bool = True
    analysis_overrides: list[SceneObservationOverride] = Field(default_factory=list)
    generation_mode: str = Field(default=DEFAULT_GENERATION_MODE)

    @field_validator("image_paths")
    @classmethod
    def validate_image_paths(cls, value: list[str]) -> list[str]:
        if any(not path for path in value):
            raise ValueError("image_paths cannot include empty values")
        return value

    @field_validator("sentiment")
    @classmethod
    def normalize_sentiment(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("generation_mode")
    @classmethod
    def normalize_generation_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_GENERATION_MODES:
            supported = ", ".join(SUPPORTED_GENERATION_MODES)
            raise ValueError(
                f"Unsupported generation mode '{value}'. Choose one of: {supported}."
            )
        return normalized


class ProviderStageStatus(BaseModel):
    """Execution trace for one provider-backed stage."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    stage: str = Field(min_length=1)
    execution_mode: str = Field(default=PROVIDER_EXECUTION_MODE_PROVIDER)
    reason: str | None = None
    recovery_hint: str | None = None

    @field_validator("stage")
    @classmethod
    def normalize_stage(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("execution_mode")
    @classmethod
    def normalize_execution_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_PROVIDER_EXECUTION_MODES:
            supported = ", ".join(SUPPORTED_PROVIDER_EXECUTION_MODES)
            raise ValueError(
                f"Unsupported provider execution mode '{value}'. Choose one of: {supported}."
            )
        return normalized


class StoryResult(BaseModel):
    """Submission-facing result payload for UI and future APIs."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    story_text: str = Field(min_length=1)
    original_scene_observations: list[SceneObservation] = Field(default_factory=list)
    scene_observations: list[SceneObservation] = Field(default_factory=list)
    sequence_memory: SequenceMemory | None = None
    narrative_plan: NarrativePlan | None = None
    evaluation_report: EvaluationReport | None = None
    sentence_alignment: list[list[int]] = Field(default_factory=list)
    grounding_notes: list[str] = Field(default_factory=list)
    provider_status: list[ProviderStageStatus] = Field(default_factory=list)
    applied_overrides: list[SceneObservationOverride] = Field(default_factory=list)
    generation_mode: str = Field(default=DEFAULT_GENERATION_MODE)
    revision_attempts: int = Field(default=0)
    is_fallback: bool = Field(default=False)
