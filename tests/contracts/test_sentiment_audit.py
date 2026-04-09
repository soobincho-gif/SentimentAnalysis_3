from __future__ import annotations

from packages.core.sentiment_audit import audit_story_sentiment
from packages.services.sentiment_control_service import SentimentControlService


def test_happy_audit_accepts_positive_provider_style_language() -> None:
    audit = audit_story_sentiment(
        (
            "A child and their dog arrived at the sunny park gate, excitement bubbling in the air. "
            "They tossed an orange ball, and the dog dashed after it, tails wagging in pure joy. "
            "Laughter filled the park as they played, the sun shining brightly above. "
            "Together, they enjoyed the peaceful moment, hearts full of happiness."
        ),
        SentimentControlService().resolve("happy"),
    )

    assert audit.score >= 0.78
    assert "cheerful" in audit.matched_keywords


def test_heartwarming_audit_accepts_bond_and_calm_language() -> None:
    audit = audit_story_sentiment(
        (
            "A child and their dog find a cozy bench to rest together after playing in the park. "
            "They share a moment of calm, the day's joy lingering in their hearts. "
            "In the gentle light of the setting sun, their bond feels stronger than ever."
        ),
        SentimentControlService().resolve("heartwarming"),
    )

    assert audit.score >= 0.78
    assert "tender" in audit.matched_keywords
    assert "comforting" in audit.matched_keywords


def test_suspenseful_audit_accepts_unease_and_threat_language() -> None:
    audit = audit_story_sentiment(
        (
            "A distant, unsettling ring echoed in the air, hinting at something amiss. "
            "Shadows danced around them, and an uneasy silence slowly replaced their laughter. "
            "The outing felt like a prelude to an unseen threat lurking just beyond the trees."
        ),
        SentimentControlService().resolve("suspenseful"),
    )

    assert audit.score >= 0.78
    assert "tense" in audit.matched_keywords
    assert "uncertain" in audit.matched_keywords


def test_sad_audit_accepts_bittersweet_provider_style_language() -> None:
    audit = audit_story_sentiment(
        (
            "A child and a dog rest on a quiet bench as the light begins fading. "
            "The moment feels melancholy and bittersweet, with a poignant stillness around them."
        ),
        SentimentControlService().resolve("sad"),
    )

    assert audit.score >= 0.78
    assert "reflective" in audit.matched_keywords
    assert "subdued" in audit.matched_keywords


def test_playful_audit_accepts_fun_and_laughter_language() -> None:
    audit = audit_story_sentiment(
        (
            "A child and a dog race across the grass in a fun, delightful game. "
            "Their laughter keeps the ending light and cheerful."
        ),
        SentimentControlService().resolve("playful"),
    )

    assert audit.score >= 0.78
    assert "lively" in audit.matched_keywords
    assert "cheerful" in audit.matched_keywords


def test_mysterious_audit_accepts_secret_and_riddle_language() -> None:
    audit = audit_story_sentiment(
        (
            "A quiet path feels strange, as if it is holding a secret just out of view. "
            "The final moment leaves an unanswered riddle in the fading light."
        ),
        SentimentControlService().resolve("mysterious"),
    )

    assert audit.score >= 0.78
    assert "curious" in audit.matched_keywords
    assert "uncertain" in audit.matched_keywords
