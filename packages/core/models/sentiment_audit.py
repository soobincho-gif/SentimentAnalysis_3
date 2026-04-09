from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SentimentAudit(BaseModel):
    """Deterministic trace of how clearly a story expresses the selected sentiment."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    target_sentiment: str = Field(min_length=1)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_style_cues: list[str] = Field(default_factory=list)
    missing_style_cues: list[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=1)
