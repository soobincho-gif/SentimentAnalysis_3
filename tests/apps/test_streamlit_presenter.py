from __future__ import annotations

from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import ProviderStageStatus, StoryResult
from apps.web.streamlit_presenter import classify_story_result, observation_payload, story_map_rows


def _base_result() -> StoryResult:
    return StoryResult(
        title="Walk Home",
        story_text="A dog waits in the park. Later it rests at home.",
        scene_observations=[
            SceneObservation(image_id=1, entities=["dog"], setting="park", actions=["waiting"]),
            SceneObservation(image_id=2, entities=["dog"], setting="home", actions=["resting"]),
        ],
        sequence_memory=SequenceMemory(
            recurring_entities=["dog"],
            setting_progression=["park", "home"],
            event_candidates=["Image 1: dog waiting", "Image 2: dog resting"],
            unresolved_ambiguities=[],
        ),
        evaluation_report=EvaluationReport(
            grounding_score=0.92,
            coherence_score=0.91,
            redundancy_score=0.88,
            sentiment_fit_score=0.9,
            readability_score=0.89,
            flags=[],
            summary="Passed",
        ),
        sentence_alignment=[[1], [2]],
    )


def test_classify_story_result_marks_provider_backed_pass_as_good() -> None:
    result = _base_result()

    status = classify_story_result(result)

    assert status.state == "good"
    assert status.title == "Story ready"


def test_classify_story_result_keeps_provider_uncertainty_in_caution_band() -> None:
    result = _base_result().model_copy(
        update={
            "sequence_memory": SequenceMemory(
                recurring_entities=["dog"],
                setting_progression=["park", "home"],
                event_candidates=["Image 1: dog waiting", "Image 2: dog resting"],
                unresolved_ambiguities=[
                    "Image 1 has limited cues.",
                    "Image 2 has limited cues.",
                ],
            )
        }
    )

    status = classify_story_result(result)

    assert status.state == "caution"


def test_classify_story_result_marks_multiple_fallback_ambiguities_as_low_confidence() -> None:
    result = _base_result().model_copy(
        update={
            "sequence_memory": SequenceMemory(
                recurring_entities=["dog"],
                setting_progression=["park", "home"],
                event_candidates=["Image 1: dog waiting", "Image 2: dog resting"],
                unresolved_ambiguities=[
                    "Image 1 has limited cues.",
                    "Image 2 has limited cues.",
                ],
            ),
            "provider_status": [
                ProviderStageStatus(
                    stage="scene_analysis",
                    execution_mode="local_fallback",
                    reason="Local fallback was used for scene analysis because OPENAI_API_KEY is not configured.",
                )
            ]
        }
    )

    status = classify_story_result(result)

    assert status.state == "low-confidence"
    assert "OPENAI_API_KEY" in status.reason


def test_story_map_rows_preserves_sentence_alignment() -> None:
    rows = story_map_rows(_base_result())

    assert rows == [
        ("A dog waits in the park.", [1]),
        ("Later it rests at home.", [2]),
    ]


def test_observation_payload_formats_optional_fields() -> None:
    payload = observation_payload(
        SceneObservation(
            image_id=1,
            entities=["dog"],
            setting="park",
            actions=["waiting"],
            uncertainty_notes=["Mild blur in the background"],
        )
    )

    assert payload["Entities"] == "dog"
    assert payload["Uncertainty"] == "Mild blur in the background"
