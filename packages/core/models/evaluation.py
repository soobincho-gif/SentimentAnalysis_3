from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from packages.core.models.sentiment_audit import SentimentAudit


class EvaluationReport(BaseModel):
    """Structured quality report for a generated story."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    grounding_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    redundancy_score: float = Field(ge=0.0, le=1.0)
    sentiment_fit_score: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
    flags: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1)
    sentiment_audit: SentimentAudit | None = None
