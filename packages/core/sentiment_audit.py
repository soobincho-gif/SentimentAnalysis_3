from __future__ import annotations

import re
from dataclasses import dataclass

from packages.core.models.sentiment import SentimentProfile
from packages.core.models.sentiment_audit import SentimentAudit

WORD_PATTERN = re.compile(r"[a-z']+")
SENTENCE_PATTERN = re.compile(r"[^.!?]+")

STYLE_CUE_TERMS: dict[str, dict[str, tuple[str, ...]]] = {
    "happy": {
        "warm wording": (
            "warm",
            "bright",
            "cheerful",
            "gentle",
            "affirming",
            "joy",
            "joyful",
            "laughter",
            "happiness",
            "sunny",
            "excitement",
        ),
        "affirming close": (
            "affirming",
            "bright",
            "warm",
            "gentle",
            "settled",
            "peaceful",
            "happiness",
            "joy",
        ),
    },
    "sad": {
        "quiet wording": (
            "quiet",
            "reflective",
            "soft",
            "subdued",
            "hush",
            "restrained",
            "melancholy",
            "bittersweet",
            "poignant",
            "fading",
            "stillness",
        ),
        "restrained close": (
            "quiet",
            "reflective",
            "soft",
            "restrained",
            "subdued",
            "bittersweet",
            "lingering",
            "fading",
            "poignant",
        ),
    },
    "suspenseful": {
        "tense wording": (
            "tense",
            "alert",
            "sharp",
            "uncertain",
            "edge",
            "unresolved",
            "tension",
            "unease",
            "unsettling",
            "eerie",
            "threat",
            "lurking",
            "silence",
            "shadows",
        ),
        "unresolved close": (
            "unresolved",
            "tense",
            "uncertain",
            "edge",
            "alert",
            "threat",
            "lurking",
            "unease",
        ),
    },
    "mysterious": {
        "curious wording": (
            "curious",
            "shadowed",
            "uncertain",
            "question",
            "questions",
            "hidden",
            "quiet",
            "secret",
            "secrets",
            "strange",
            "riddle",
            "whisper",
            "whispers",
            "elusive",
        ),
        "open close": (
            "open",
            "question",
            "questions",
            "remains",
            "uncertain",
            "hidden",
            "unknown",
            "unanswered",
            "strange",
            "riddle",
            "secret",
            "secrets",
            "elusive",
        ),
    },
    "heartwarming": {
        "tender wording": (
            "tender",
            "gentle",
            "comforting",
            "sincere",
            "warm",
            "together",
            "bond",
            "cozy",
            "calm",
            "hearts",
            "kindness",
        ),
        "comforting close": (
            "tender",
            "comforting",
            "satisfying",
            "gentle",
            "warm",
            "bond",
            "calm",
            "together",
        ),
    },
    "playful": {
        "lively wording": (
            "lively",
            "light",
            "energetic",
            "cheerful",
            "playful",
            "spark",
            "bounce",
            "fun",
            "delight",
            "delightful",
            "laughter",
            "joyful",
        ),
        "light close": (
            "light",
            "smiling",
            "lively",
            "playful",
            "bright",
            "joyful",
            "delight",
            "laughter",
            "cheerful",
        ),
    },
}

KEYWORD_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "happy": {
        "warm": ("warmth",),
        "bright": ("sunny", "sun", "shining", "brightly"),
        "gentle": ("peaceful", "calm"),
        "cheerful": ("joy", "joyful", "laughter", "happiness", "excitement"),
    },
    "sad": {
        "quiet": ("silence",),
        "reflective": ("lingering", "bittersweet", "fleeting", "passage", "fading"),
        "soft": ("dim", "gentle"),
        "subdued": ("heavy", "melancholy", "poignant", "fragile"),
    },
    "suspenseful": {
        "tense": ("unsettling", "eerie", "threat", "lurking"),
        "alert": ("shadows", "amiss"),
        "uncertain": ("uneasy", "unclear"),
        "sharp": ("suddenly",),
    },
    "mysterious": {
        "quiet": ("still", "whisper", "whispers", "silence", "softly"),
        "curious": ("question", "questions", "secret", "secrets", "wonder", "elusive"),
        "shadowed": ("shadows", "shimmer", "veiled"),
        "uncertain": ("unclear", "unanswered", "unknown", "strange", "elusive"),
    },
    "heartwarming": {
        "tender": ("bond", "cozy"),
        "gentle": ("calm", "peaceful"),
        "comforting": ("together", "rest", "safe"),
        "sincere": ("hearts", "shared", "bond"),
    },
    "playful": {
        "lively": ("bounce", "darted", "delightful", "laughter"),
        "light": ("smiling", "carefree", "bright"),
        "energetic": ("quick", "raced", "dashed", "sprinted", "eager"),
        "cheerful": ("joy", "laughed", "joyful"),
        "playful": ("fun", "game", "teasing", "delight"),
    },
}


@dataclass(frozen=True)
class _AuditContext:
    normalized_text: str
    sentences: list[str]
    words_by_sentence: list[list[str]]

    @property
    def final_sentence(self) -> str:
        if not self.sentences:
            return ""
        return self.sentences[-1]

    @property
    def average_sentence_length(self) -> float:
        if not self.words_by_sentence:
            return 0.0
        total_words = sum(len(words) for words in self.words_by_sentence)
        return total_words / len(self.words_by_sentence)

    @property
    def shortest_sentence_length(self) -> int:
        if not self.words_by_sentence:
            return 0
        return min(len(words) for words in self.words_by_sentence)


def audit_story_sentiment(
    story_text: str,
    sentiment_profile: SentimentProfile,
) -> SentimentAudit:
    normalized_text = story_text.lower()
    sentences = [
        segment.strip().lower()
        for segment in SENTENCE_PATTERN.findall(story_text)
        if segment.strip()
    ]
    words_by_sentence = [WORD_PATTERN.findall(sentence) for sentence in sentences]
    context = _AuditContext(
        normalized_text=normalized_text,
        sentences=sentences,
        words_by_sentence=words_by_sentence,
    )

    expected_keywords = list(dict.fromkeys(keyword.lower() for keyword in sentiment_profile.tone_keywords))
    matched_keywords = [
        keyword
        for keyword in expected_keywords
        if _matches_keyword(sentiment_profile.label, keyword, normalized_text)
    ]
    missing_keywords = [
        keyword for keyword in expected_keywords if keyword not in matched_keywords
    ]

    matched_style_cues: list[str] = []
    missing_style_cues: list[str] = []
    for cue_name in _expected_style_cue_names(sentiment_profile.label):
        if _matches_style_cue(sentiment_profile.label, cue_name, context):
            matched_style_cues.append(cue_name)
        else:
            missing_style_cues.append(cue_name)

    keyword_ratio = _ratio(len(matched_keywords), len(expected_keywords))
    style_ratio = _ratio(len(matched_style_cues), len(_expected_style_cue_names(sentiment_profile.label)))
    score = round(min(0.99, 0.28 + 0.45 * keyword_ratio + 0.27 * style_ratio), 2)
    summary = _build_summary(
        sentiment_label=sentiment_profile.label,
        score=score,
        matched_keywords=matched_keywords,
        matched_style_cues=matched_style_cues,
        missing_keywords=missing_keywords,
        missing_style_cues=missing_style_cues,
    )

    return SentimentAudit(
        target_sentiment=sentiment_profile.label,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        matched_style_cues=matched_style_cues,
        missing_style_cues=missing_style_cues,
        score=score,
        summary=summary,
    )


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase)
    return re.search(rf"\b{escaped}\b", text) is not None


def _matches_keyword(sentiment_label: str, keyword: str, text: str) -> bool:
    if _contains_phrase(text, keyword):
        return True
    aliases = KEYWORD_ALIASES.get(sentiment_label, {}).get(keyword, ())
    return any(_contains_phrase(text, alias) for alias in aliases)


def _expected_style_cue_names(sentiment_label: str) -> list[str]:
    base_names = list(STYLE_CUE_TERMS.get(sentiment_label, {}).keys())
    pacing_label = _pacing_cue_name(sentiment_label)
    if pacing_label is not None:
        base_names.append(pacing_label)
    return base_names


def _matches_style_cue(sentiment_label: str, cue_name: str, context: _AuditContext) -> bool:
    for label, terms in STYLE_CUE_TERMS.get(sentiment_label, {}).items():
        if label == cue_name:
            haystack = context.final_sentence if "close" in cue_name else context.normalized_text
            return any(_contains_phrase(haystack, term) for term in terms)

    if cue_name == "smooth pacing":
        return 9.0 <= context.average_sentence_length <= 24.0
    if cue_name == "slower pacing":
        return context.average_sentence_length >= 12.0
    if cue_name == "tight pacing":
        return context.average_sentence_length <= 13.5 or context.shortest_sentence_length <= 8
    if cue_name == "controlled ambiguity":
        return any(
            _contains_phrase(context.normalized_text, term)
            for term in (
                "question",
                "questions",
                "uncertain",
                "hidden",
                "unclear",
                "remains",
                "secret",
                "secrets",
                "elusive",
            )
        )
    if cue_name == "connected framing":
        return any(
            _contains_phrase(context.normalized_text, term)
            for term in ("together", "connected", "gentle warmth", "comforting")
        )
    if cue_name == "quick pacing":
        return context.average_sentence_length <= 16.0 or _contains_phrase(
            context.normalized_text,
            "quick",
        )
    return False


def _pacing_cue_name(sentiment_label: str) -> str | None:
    mapping = {
        "happy": "smooth pacing",
        "sad": "slower pacing",
        "suspenseful": "tight pacing",
        "mysterious": "controlled ambiguity",
        "heartwarming": "connected framing",
        "playful": "quick pacing",
    }
    return mapping.get(sentiment_label)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _build_summary(
    *,
    sentiment_label: str,
    score: float,
    matched_keywords: list[str],
    matched_style_cues: list[str],
    missing_keywords: list[str],
    missing_style_cues: list[str],
) -> str:
    matched_bits = ", ".join(matched_keywords[:2] + matched_style_cues[:1])
    missing_bits = ", ".join(missing_keywords[:2] + missing_style_cues[:1])

    if score >= 0.78:
        if matched_bits:
            return (
                f"The draft expresses {sentiment_label} clearly through {matched_bits}."
            )
        return f"The draft expresses {sentiment_label} clearly."

    if score >= 0.62:
        if missing_bits:
            return (
                f"The draft shows some {sentiment_label} cues, but it could strengthen {missing_bits}."
            )
        return f"The draft shows some {sentiment_label} cues, but the tone could be stronger."

    if missing_bits:
        return (
            f"The draft only lightly expresses {sentiment_label}; it is still missing {missing_bits}."
        )
    return f"The draft only lightly expresses {sentiment_label}."
