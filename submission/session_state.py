from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RunSnapshot(BaseModel):
    """Session-scoped metadata for comparing the latest run with the previous run."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    image_signature: list[str] = Field(default_factory=list)
    image_count: int = Field(ge=0)
    sentiment: str = Field(min_length=1)
    correction_count: int = Field(default=0, ge=0)
    generation_mode: str = Field(min_length=1)
    strict_grounding: bool = False
    fallback_used: bool = False
    flag_count: int = Field(default=0, ge=0)
    grounding_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    redundancy_score: float = Field(ge=0.0, le=1.0)
    sentiment_fit_score: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
