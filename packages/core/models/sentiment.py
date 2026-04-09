from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SentimentProfile(BaseModel):
    """Narrative style controls derived from the selected sentiment."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    label: str = Field(min_length=1)
    tone_keywords: list[str] = Field(default_factory=list)
    pacing_style: str = Field(min_length=1)
    sentence_style: str = Field(min_length=1)
    ending_style: str = Field(min_length=1)
    metaphor_tolerance: str = Field(min_length=1)
    inference_strictness: str = Field(min_length=1)
