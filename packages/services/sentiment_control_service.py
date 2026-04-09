from __future__ import annotations

from packages.core.models.sentiment import SentimentProfile
from packages.core.models.story import STRICT_GROUNDING_GENERATION_MODE
from packages.prompts.sentiment_profiles import (
    SENTIMENT_PROFILE_MAP,
    SUPPORTED_SENTIMENT_LABELS,
)


class SentimentControlService:
    """Resolve a user-facing sentiment label into narrative control settings."""

    def resolve(
        self,
        sentiment_label: str,
        *,
        generation_mode: str = "default",
    ) -> SentimentProfile:
        normalized = sentiment_label.strip().lower()
        if normalized not in SENTIMENT_PROFILE_MAP:
            supported = ", ".join(SUPPORTED_SENTIMENT_LABELS)
            raise ValueError(
                f"Unsupported sentiment '{sentiment_label}'. Choose one of: {supported}."
            )
        profile = SENTIMENT_PROFILE_MAP[normalized]
        if generation_mode != STRICT_GROUNDING_GENERATION_MODE:
            return profile

        return profile.model_copy(
            update={
                "sentence_style": f"{profile.sentence_style}; literal and evidence-led",
                "metaphor_tolerance": "very low",
                "inference_strictness": "very strict",
            }
        )
