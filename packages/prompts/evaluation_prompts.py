from __future__ import annotations

GROUNDING_WARNING_THRESHOLD = 0.7
COHERENCE_WARNING_THRESHOLD = 0.72
REDUNDANCY_WARNING_THRESHOLD = 0.7
SENTIMENT_WARNING_THRESHOLD = 0.68
READABILITY_WARNING_THRESHOLD = 0.68

DEFAULT_SCORE_THRESHOLDS = {
    "grounding": GROUNDING_WARNING_THRESHOLD,
    "coherence": COHERENCE_WARNING_THRESHOLD,
    "redundancy": REDUNDANCY_WARNING_THRESHOLD,
    "sentiment_fit": SENTIMENT_WARNING_THRESHOLD,
    "readability": READABILITY_WARNING_THRESHOLD,
}

STRICT_GROUNDING_SCORE_THRESHOLDS = {
    "grounding": 0.82,
    "coherence": 0.72,
    "redundancy": REDUNDANCY_WARNING_THRESHOLD,
    "sentiment_fit": SENTIMENT_WARNING_THRESHOLD,
    "readability": READABILITY_WARNING_THRESHOLD,
}

QUALITY_FLAG_MESSAGES = {
    "grounding": "Grounding confidence is limited; the story should stay closer to explicit image cues.",
    "coherence": "Sequence coherence is light; the image-to-image progression could be clarified.",
    "redundancy": "Sentence variety is limited; the draft repeats similar structure too often.",
    "sentiment": "The selected sentiment is only lightly expressed in the draft.",
    "readability": "Sentence length or cadence could be smoothed for easier reading.",
}
