from __future__ import annotations

from pathlib import Path

from PIL import Image

from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import OrderedImageSet, SceneObservation
from packages.core.models.sentiment import SentimentProfile
from packages.core.models.sequence import NarrativePlan, SequenceMemory
from packages.core.models.story import StoryDraft
from packages.services.evaluation_service import EvaluationService
from packages.services.scene_analysis_service import SceneAnalysisService
from packages.services.story_generation_service import StoryGenerationService


def _sentiment_profile() -> SentimentProfile:
    return SentimentProfile(
        label="playful",
        tone_keywords=["light"],
        pacing_style="medium",
        sentence_style="compact",
        ending_style="grounded",
        metaphor_tolerance="low",
        inference_strictness="strict",
    )


def _narrative_plan() -> NarrativePlan:
    return NarrativePlan(
        arc_type="grounded",
        beat_list=["Image 1: keep cat grounded while it is resting in room."],
        sentence_image_map=[[1]],
        allowed_inferences=[],
        forbidden_claims=[],
        title_candidates=["Playful Cat"],
    )


def test_scene_analysis_uses_local_fallback_when_provider_request_fails(tmp_path: Path) -> None:
    image_path = tmp_path / "park_cat_rest.png"
    Image.new("RGB", (64, 64), color=(180, 170, 150)).save(image_path)
    service = SceneAnalysisService(use_mock=True)

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = True

        def analyze_image(self, **kwargs):  # type: ignore[no-untyped-def]
            return SceneObservation(
                image_id=1,
                entities=["shadowy figure"],
                setting="unknown location",
                objects=["small item"],
                actions=["moving"],
                visible_mood="neutral",
                uncertainty_notes=["MOCK DATA: Actual provider bypassed or failed."],
            )

        def describe_fallback(self, *, stage: str) -> str:
            return f"Local fallback was used for {stage} because the OpenAI provider request failed."

    service.provider = DummyProvider()  # type: ignore[assignment]
    observations = service.analyze(OrderedImageSet.from_image_paths([str(image_path)]))

    assert observations[0].entities == ["cat"]
    assert any("provider request failed" in note.lower() for note in observations[0].uncertainty_notes)


def test_story_generation_uses_local_fallback_when_provider_request_fails() -> None:
    service = StoryGenerationService(use_mock=True)

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = True

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            return StoryDraft(
                title="Mock Supported Story",
                story_text="This is a gracefully degraded mock story due to missing API keys or test mode.",
                sentence_alignment=[[1]],
                grounding_notes=["MOCK DATA: Provider fallback"],
            )

        def describe_fallback(self, *, stage: str) -> str:
            return f"Local fallback was used for {stage} because the OpenAI provider request failed."

    service.provider = DummyProvider()  # type: ignore[assignment]
    observation = SceneObservation(image_id=1, entities=["cat"], setting="room", actions=["resting"])

    draft = service.generate(
        observations=[observation],
        sequence_memory=SequenceMemory(),
        narrative_plan=_narrative_plan(),
        sentiment_profile=_sentiment_profile(),
        max_sentences=3,
    )

    assert "gracefully degraded mock story" not in draft.story_text.lower()
    assert "cat" in draft.story_text.lower()
    assert any("provider request failed" in note.lower() for note in draft.grounding_notes)


def test_evaluation_uses_local_fallback_when_provider_request_fails() -> None:
    service = EvaluationService(use_mock=True)

    class DummyProvider:
        is_configured = True
        last_request_used_fallback = True

        def generate_text(self, **kwargs):  # type: ignore[no-untyped-def]
            return EvaluationReport(
                grounding_score=0.9,
                coherence_score=0.9,
                redundancy_score=0.9,
                sentiment_fit_score=0.9,
                readability_score=0.9,
                flags=[],
                summary="MOCK DATA: Draft passes evaluation.",
            )

        def describe_fallback(self, *, stage: str) -> str:
            return f"Local fallback was used for {stage} because the OpenAI provider request failed."

    service.provider = DummyProvider()  # type: ignore[assignment]
    report = service.evaluate(
        story_draft=StoryDraft(
            title="Draft",
            story_text="One sentence.",
            sentence_alignment=[[1]],
            grounding_notes=[],
        ),
        observations=[SceneObservation(image_id=1, entities=["cat"], setting="room", actions=["resting"])],
        sequence_memory=SequenceMemory(),
        sentiment_profile=_sentiment_profile(),
    )

    assert "mock data" not in report.summary.lower()
    assert "provider request failed" in report.summary.lower()
