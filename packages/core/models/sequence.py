from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SequenceMemory(BaseModel):
    """Cross-image continuity and sequence-level reasoning."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    recurring_entities: list[str] = Field(default_factory=list)
    setting_progression: list[str] = Field(default_factory=list)
    event_candidates: list[str] = Field(default_factory=list)
    unresolved_ambiguities: list[str] = Field(default_factory=list)


class NarrativePlan(BaseModel):
    """Constrained story scaffold derived from observations and sequence memory."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    arc_type: str = Field(min_length=1)
    beat_list: list[str] = Field(default_factory=list)
    sentence_image_map: list[list[int]] = Field(default_factory=list)
    allowed_inferences: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    title_candidates: list[str] = Field(default_factory=list)
