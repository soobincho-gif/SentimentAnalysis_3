from __future__ import annotations

from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment import SentimentProfile
from packages.core.models.sequence import NarrativePlan, SequenceMemory
from packages.core.models.story import (
    STRICT_GROUNDING_GENERATION_MODE,
    StoryDraft,
)
from packages.services.evaluation_service import EvaluationService
from packages.services.narrative_planning_service import NarrativePlanningService
from packages.services.sentiment_control_service import SentimentControlService
from packages.services.story_generation_service import StoryGenerationService
from packages.prompts.story_generation_prompts import sentiment_generation_guidance


def test_strict_grounding_mode_tightens_evaluation_thresholds() -> None:
    service = EvaluationService(use_mock=True)
    base_report = EvaluationReport(
        grounding_score=0.78,
        coherence_score=0.80,
        redundancy_score=0.90,
        sentiment_fit_score=0.88,
        readability_score=0.89,
        flags=[],
        summary="Close but not strict enough.",
    )

    default_report = service._apply_threshold_policy(base_report, generation_mode="default")
    strict_report = service._apply_threshold_policy(
        base_report,
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
    )

    assert "grounding_score below threshold" not in default_report.flags
    assert "grounding_score below strict threshold" in strict_report.flags


def test_strict_grounding_mode_tightens_sentiment_profile() -> None:
    profile = SentimentControlService().resolve(
        "happy",
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
    )

    assert isinstance(profile, SentimentProfile)
    assert profile.inference_strictness == "very strict"
    assert profile.metaphor_tolerance == "very low"


def test_story_generation_uses_lower_temperature_in_strict_mode() -> None:
    service = StoryGenerationService(use_mock=True)
    captured_temperatures: list[float] = []

    class DummyProvider:
        is_configured = True

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            captured_temperatures.append(kwargs["temperature"])
            return StoryDraft(title="Draft", story_text="One sentence.", sentence_alignment=[[1]], grounding_notes=[])

    service.provider = DummyProvider()  # type: ignore[assignment]
    observation = SceneObservation(image_id=1, entities=["cat"], setting="room", actions=["resting"])
    sentiment_profile = SentimentProfile(
        label="playful",
        tone_keywords=["light"],
        pacing_style="medium",
        sentence_style="compact",
        ending_style="grounded",
        metaphor_tolerance="low",
        inference_strictness="strict",
    )
    plan = NarrativePlan(
        arc_type="grounded",
        beat_list=["Image 1: keep cat grounded while it is resting in room."],
        sentence_image_map=[[1]],
        allowed_inferences=[],
        forbidden_claims=[],
        title_candidates=["Playful Cat"],
    )

    service.generate(
        observations=[observation],
        sequence_memory=SequenceMemory(),
        narrative_plan=plan,
        sentiment_profile=sentiment_profile,
        max_sentences=3,
        generation_mode="default",
    )
    service.generate(
        observations=[observation],
        sequence_memory=SequenceMemory(),
        narrative_plan=plan,
        sentiment_profile=sentiment_profile,
        max_sentences=3,
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
    )

    assert captured_temperatures == [0.35, 0.18]


def test_suspenseful_generation_prompt_uses_restrained_tension_guidance() -> None:
    service = StoryGenerationService(use_mock=True)
    captured_prompts: list[str] = []

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = False

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            captured_prompts.append(kwargs["prompt"])
            return StoryDraft(
                title="Draft",
                story_text="One sentence.",
                sentence_alignment=[[1]],
                grounding_notes=[],
            )

    service.provider = DummyProvider()  # type: ignore[assignment]
    observation = SceneObservation(
        image_id=1,
        entities=["child", "dog"],
        setting="park",
        actions=["waiting"],
    )
    plan = NarrativePlan(
        arc_type="grounded",
        beat_list=["Image 1: child and dog wait at the park gate."],
        sentence_image_map=[[1]],
        allowed_inferences=[],
        forbidden_claims=[],
        title_candidates=["Park Gate"],
    )

    service.generate(
        observations=[observation],
        sequence_memory=SequenceMemory(),
        narrative_plan=plan,
        sentiment_profile=SentimentControlService().resolve("suspenseful"),
        max_sentences=3,
        generation_mode="default",
    )

    prompt = captured_prompts[0]
    assert "Sentiment guidance:" in prompt
    assert "restrained alertness and unresolved anticipation" in prompt
    assert "Make the tension explicit with grounded cues" in prompt
    assert "Do not invent hidden danger" in prompt
    assert "unseen agents" in prompt


def test_story_revision_prompt_reincludes_observations() -> None:
    service = StoryGenerationService(use_mock=True)
    captured_prompts: list[str] = []

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = False

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            captured_prompts.append(kwargs["prompt"])
            return StoryDraft(
                title="Draft",
                story_text="Revised sentence.",
                sentence_alignment=[[1]],
                grounding_notes=[],
            )

    service.provider = DummyProvider()  # type: ignore[assignment]
    observation = SceneObservation(image_id=1, entities=["child"], setting="park", actions=["waiting"])
    plan = NarrativePlan(
        arc_type="grounded",
        beat_list=["Image 1: child waits in the park."],
        sentence_image_map=[[1]],
        allowed_inferences=[],
        forbidden_claims=[],
        title_candidates=["Park Wait"],
    )

    service.revise(
        previous_draft=StoryDraft(
            title="Draft",
            story_text="The park felt threatening.",
            sentence_alignment=[[1]],
            grounding_notes=[],
        ),
        feedback_flags=["sentiment_fit_score below threshold"],
        observations=[observation],
        sequence_memory=SequenceMemory(),
        narrative_plan=plan,
        sentiment_profile=SentimentControlService().resolve("suspenseful"),
        max_sentences=3,
        generation_mode="default",
    )

    prompt = captured_prompts[0]
    assert "Observations:" in prompt
    assert "\"setting\":\"park\"" in prompt


def test_sad_playful_and_mysterious_profiles_have_generation_guidance() -> None:
    assert "bittersweet" in sentiment_generation_guidance(SentimentControlService().resolve("sad"))
    assert "lively" in sentiment_generation_guidance(SentimentControlService().resolve("playful"))
    assert "quiet wonder" in sentiment_generation_guidance(SentimentControlService().resolve("mysterious"))


def test_evaluation_uses_deterministic_temperature() -> None:
    service = EvaluationService(use_mock=True)
    captured_temperatures: list[float] = []

    class DummyProvider:
        is_configured = True

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            captured_temperatures.append(kwargs["temperature"])
            return EvaluationReport(
                grounding_score=0.9,
                coherence_score=0.9,
                redundancy_score=0.9,
                sentiment_fit_score=0.9,
                readability_score=0.9,
                flags=[],
                summary="ok",
            )

    service.provider = DummyProvider()  # type: ignore[assignment]
    service.evaluate(
        story_draft=StoryDraft(title="Draft", story_text="One sentence.", sentence_alignment=[[1]], grounding_notes=[]),
        observations=[SceneObservation(image_id=1, entities=["cat"], setting="room", actions=["resting"])],
        sequence_memory=SequenceMemory(),
        sentiment_profile=SentimentProfile(
            label="playful",
            tone_keywords=["light"],
            pacing_style="medium",
            sentence_style="compact",
            ending_style="grounded",
            metaphor_tolerance="low",
            inference_strictness="strict",
        ),
    )

    assert captured_temperatures == [0.0]


def test_threshold_policy_removes_inconsistent_provider_score_flags() -> None:
    service = EvaluationService(use_mock=True)
    report = EvaluationReport(
        grounding_score=0.84,
        coherence_score=0.82,
        redundancy_score=0.88,
        sentiment_fit_score=0.76,
        readability_score=0.9,
        flags=["grounding_score", "sentiment_fit_score", "manual note"],
        summary="ok",
    )

    cleaned = service._apply_threshold_policy(report, generation_mode="default")

    assert "grounding_score" not in cleaned.flags
    assert "sentiment_fit_score" not in cleaned.flags
    assert "manual note" in cleaned.flags


def test_provider_evaluation_reconciles_sentiment_fit_with_strong_audit() -> None:
    service = EvaluationService(use_mock=True)

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = False

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            return EvaluationReport(
                grounding_score=0.8,
                coherence_score=0.8,
                redundancy_score=0.9,
                sentiment_fit_score=0.6,
                readability_score=0.9,
                flags=["sentiment_fit_score", "grounding_score"],
                summary="Provider scored the tone conservatively.",
            )

    service.provider = DummyProvider()  # type: ignore[assignment]
    report = service.evaluate(
        story_draft=StoryDraft(
            title="Mysterious Park",
            story_text=(
                "A child and a dog pause at the park gate in the fading light. "
                "Their play feels touched by quiet secrets and unanswered questions. "
                "The final moment leaves a strange, open riddle in the air."
            ),
            sentence_alignment=[[1], [2], [3]],
            grounding_notes=[],
        ),
        observations=[
            SceneObservation(image_id=1, entities=["child", "dog"], setting="park", actions=["pausing"]),
            SceneObservation(image_id=2, entities=["child", "dog"], setting="park", actions=["playing"]),
            SceneObservation(image_id=3, entities=["child", "dog"], setting="park", actions=["resting"]),
        ],
        sequence_memory=SequenceMemory(setting_progression=["park", "park", "park"]),
        sentiment_profile=SentimentControlService().resolve("mysterious"),
    )

    assert report.sentiment_fit_score >= 0.68
    assert "sentiment_fit_score" not in report.flags
    assert "grounding_score" not in report.flags
    assert "reconciled upward" in report.summary


def test_local_fallback_generation_uses_distinct_sentiment_cues() -> None:
    service = StoryGenerationService(use_mock=True)
    observations = [
        SceneObservation(image_id=1, entities=["dog"], setting="park", actions=["waiting"]),
        SceneObservation(image_id=2, entities=["dog"], setting="path", actions=["walking"]),
    ]
    plan = NarrativePlan(
        arc_type="grounded",
        beat_list=["Image 1: dog waits in park.", "Image 2: dog walks on path."],
        sentence_image_map=[[1], [2]],
        allowed_inferences=[],
        forbidden_claims=[],
        title_candidates=["Grounded Dog"],
    )
    sequence_memory = SequenceMemory(setting_progression=["park", "path"])

    happy_story = service._fallback_generate(
        observations=observations,
        sequence_memory=sequence_memory,
        narrative_plan=plan,
        sentiment_profile=SentimentControlService().resolve("happy"),
        max_sentences=4,
        generation_mode="default",
        fallback_note="fallback",
    )
    sad_story = service._fallback_generate(
        observations=observations,
        sequence_memory=sequence_memory,
        narrative_plan=plan,
        sentiment_profile=SentimentControlService().resolve("sad"),
        max_sentences=4,
        generation_mode="default",
        fallback_note="fallback",
    )

    assert happy_story.story_text != sad_story.story_text
    assert "warm" in happy_story.story_text.lower()
    assert "cheerful" in happy_story.story_text.lower()
    assert "quiet" in sad_story.story_text.lower()
    assert "subdued" in sad_story.story_text.lower()


def test_fallback_evaluation_records_sentiment_audit_details() -> None:
    service = EvaluationService(use_mock=True)
    report = service.evaluate(
        story_draft=StoryDraft(
            title="Bright Walk",
            story_text=(
                "A warm rhythm begins as image 1 shows the dog waiting in the park, "
                "giving the frame a warm, cheerful lift. "
                "Taken together, the images move from park to path, ending on an affirming, bright note."
            ),
            sentence_alignment=[[1], [1, 2]],
            grounding_notes=[],
        ),
        observations=[
            SceneObservation(image_id=1, entities=["dog"], setting="park", actions=["waiting"]),
            SceneObservation(image_id=2, entities=["dog"], setting="path", actions=["walking"]),
        ],
        sequence_memory=SequenceMemory(setting_progression=["park", "path"]),
        sentiment_profile=SentimentControlService().resolve("happy"),
    )

    assert report.sentiment_audit is not None
    assert report.sentiment_fit_score == report.sentiment_audit.score
    assert report.sentiment_audit.target_sentiment == "happy"
    assert "warm" in report.sentiment_audit.matched_keywords
    assert "Sentiment audit:" in report.summary
