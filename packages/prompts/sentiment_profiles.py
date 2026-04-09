from __future__ import annotations

from packages.core.models.sentiment import SentimentProfile

SENTIMENT_PROFILE_MAP: dict[str, SentimentProfile] = {
    "happy": SentimentProfile(
        label="happy",
        tone_keywords=["warm", "bright", "gentle", "cheerful"],
        pacing_style="smooth",
        sentence_style="clear and warm",
        ending_style="affirming",
        metaphor_tolerance="low-to-medium",
        inference_strictness="strict",
    ),
    "sad": SentimentProfile(
        label="sad",
        tone_keywords=["quiet", "reflective", "soft", "subdued"],
        pacing_style="slower",
        sentence_style="simple and reflective",
        ending_style="restrained",
        metaphor_tolerance="medium",
        inference_strictness="strict",
    ),
    "suspenseful": SentimentProfile(
        label="suspenseful",
        tone_keywords=["tense", "alert", "uncertain", "sharp"],
        pacing_style="brisk",
        sentence_style="shorter and tighter",
        ending_style="unresolved or lightly tense",
        metaphor_tolerance="low",
        inference_strictness="strict",
    ),
    "mysterious": SentimentProfile(
        label="mysterious",
        tone_keywords=["quiet", "curious", "shadowed", "uncertain"],
        pacing_style="controlled",
        sentence_style="slightly suggestive but clear",
        ending_style="open-ended",
        metaphor_tolerance="medium",
        inference_strictness="strict",
    ),
    "heartwarming": SentimentProfile(
        label="heartwarming",
        tone_keywords=["tender", "gentle", "comforting", "sincere"],
        pacing_style="smooth",
        sentence_style="warm and soft",
        ending_style="emotionally satisfying",
        metaphor_tolerance="low-to-medium",
        inference_strictness="strict",
    ),
    "playful": SentimentProfile(
        label="playful",
        tone_keywords=["lively", "light", "energetic", "cheerful"],
        pacing_style="quick",
        sentence_style="crisp and upbeat",
        ending_style="smiling and light",
        metaphor_tolerance="low",
        inference_strictness="strict",
    ),
}

SUPPORTED_SENTIMENT_LABELS = tuple(SENTIMENT_PROFILE_MAP.keys())
