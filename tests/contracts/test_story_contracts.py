from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import OrderedImageSet, SceneObservation
from packages.core.models.sentiment_audit import SentimentAudit
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import ProviderStageStatus, StoryRequest, StoryResult
from packages.services.image_preprocessing_service import ImagePreprocessingService
from packages.services.sentiment_control_service import SentimentControlService


def test_story_contracts_round_trip_nested_structures() -> None:
    ordered_images = OrderedImageSet.from_image_paths(["/tmp/one.png", "/tmp/two.png"])
    scene_observation = SceneObservation(
        image_id=1,
        entities=["dog"],
        setting="park",
        objects=["leash"],
        actions=["walking"],
        visible_mood="playful",
        uncertainty_notes=[],
        same_subject_as_previous=True,
    )
    result = StoryResult(
        title="A Grounded Walk",
        story_text="A grounded moment unfolds in order.",
        original_scene_observations=[scene_observation],
        scene_observations=[scene_observation],
        sequence_memory=SequenceMemory(setting_progression=["park", "path"]),
        evaluation_report=EvaluationReport(
            grounding_score=0.9,
            coherence_score=0.88,
            redundancy_score=0.91,
            sentiment_fit_score=0.82,
            readability_score=0.87,
            flags=[],
            summary="Grounded and chronologically clear.",
            sentiment_audit=SentimentAudit(
                target_sentiment="happy",
                matched_keywords=["warm", "bright"],
                missing_keywords=["gentle"],
                matched_style_cues=["warm wording"],
                missing_style_cues=["smooth pacing"],
                score=0.82,
                summary="The draft expresses happy clearly through warm, bright, warm wording.",
            ),
        ),
        sentence_alignment=[[1], [2]],
        grounding_notes=["dog remains visible across both images"],
        provider_status=[
            ProviderStageStatus(
                stage="story_generation",
                execution_mode="local_fallback",
                reason="Local fallback was used for story generation because OPENAI_API_KEY is not configured.",
                recovery_hint="Set OPENAI_API_KEY in the environment or .env file.",
            )
        ],
        applied_overrides=[
            SceneObservationOverride(image_id=2, same_subject_as_previous=True)
        ],
        generation_mode="strict_grounding",
    )

    payload = result.model_dump()

    assert ordered_images.total_images == 2
    assert payload["original_scene_observations"][0]["setting"] == "park"
    assert payload["scene_observations"][0]["setting"] == "park"
    assert payload["scene_observations"][0]["same_subject_as_previous"] is True
    assert payload["sequence_memory"]["setting_progression"] == ["park", "path"]
    assert payload["evaluation_report"]["sentiment_audit"]["target_sentiment"] == "happy"
    assert payload["sentence_alignment"] == [[1], [2]]
    assert payload["grounding_notes"] == ["dog remains visible across both images"]
    assert payload["provider_status"][0]["stage"] == "story_generation"
    assert payload["provider_status"][0]["execution_mode"] == "local_fallback"
    assert payload["applied_overrides"][0]["same_subject_as_previous"] is True
    assert payload["generation_mode"] == "strict_grounding"


def test_story_request_rejects_empty_image_paths() -> None:
    with pytest.raises(ValueError):
        StoryRequest(image_paths=[""], sentiment="happy")


def test_story_request_accepts_large_max_sentences() -> None:
    request = StoryRequest(
        image_paths=["/tmp/one.png"],
        sentiment="happy",
        max_sentences=24,
    )

    assert request.max_sentences == 24


def test_story_request_rejects_unsupported_generation_mode() -> None:
    with pytest.raises(ValueError):
        StoryRequest(
            image_paths=["/tmp/one.png"],
            sentiment="happy",
            generation_mode="cinematic",
        )


def test_image_preprocessing_preserves_order_and_filenames(tmp_path: Path) -> None:
    first = tmp_path / "park_dog_walk.png"
    second = tmp_path / "park_dog_rest.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    ordered_images = ImagePreprocessingService().prepare([str(first), str(second)])

    assert ordered_images.image_paths == [str(first), str(second)]
    assert ordered_images.original_filenames == ["park_dog_walk.png", "park_dog_rest.png"]
    assert ordered_images.total_images == 2


def test_sentiment_control_rejects_unsupported_label() -> None:
    with pytest.raises(ValueError, match="Unsupported sentiment"):
        SentimentControlService().resolve("angry")


def test_provider_sdk_dependencies_are_declared_for_installation() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    assert any(dependency.startswith("openai") for dependency in dependencies)
    assert any(dependency.startswith("instructor") for dependency in dependencies)
    assert any(requirement.startswith("openai") for requirement in requirements)
    assert any(requirement.startswith("instructor") for requirement in requirements)
