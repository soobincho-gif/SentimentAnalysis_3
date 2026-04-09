from __future__ import annotations

from unittest.mock import MagicMock

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.story import StoryDraft, StoryRequest
from packages.services.pipeline import StorytellingPipeline


def test_pipeline_forwards_sentence_alignment_and_grounding_notes() -> None:
    pipeline = StorytellingPipeline(
        image_preprocessing_service=MagicMock(),
        scene_analysis_service=MagicMock(),
        observation_override_service=MagicMock(),
        sequence_linking_service=MagicMock(),
        narrative_planning_service=MagicMock(),
        sentiment_control_service=MagicMock(),
        story_generation_service=MagicMock(),
        evaluation_service=MagicMock(),
    )

    from packages.core.models.sequence import NarrativePlan, SequenceMemory

    pipeline.image_preprocessing_service.prepare.return_value = MagicMock()
    pipeline.scene_analysis_service.analyze.return_value = []
    pipeline.scene_analysis_service.last_provider_status = {
        "stage": "scene_analysis",
        "execution_mode": "provider",
        "reason": None,
        "recovery_hint": None,
    }
    pipeline.observation_override_service.apply.return_value = ([], [])
    pipeline.sequence_linking_service.build.return_value = SequenceMemory()
    pipeline.narrative_planning_service.plan.return_value = NarrativePlan(arc_type="test")
    pipeline.narrative_planning_service.last_provider_status = {
        "stage": "narrative_planning",
        "execution_mode": "provider",
        "reason": None,
        "recovery_hint": None,
    }
    pipeline.sentiment_control_service.resolve.return_value = MagicMock()
    pipeline.story_generation_service.generate.return_value = StoryDraft(
        title="Mapped Draft",
        story_text="Sentence one. Sentence two.",
        sentence_alignment=[[1], [1, 2]],
        grounding_notes=["entity continuity confirmed", "late frame remains ambiguous"],
    )
    pipeline.story_generation_service.last_provider_status = {
        "stage": "story_generation",
        "execution_mode": "local_fallback",
        "reason": "Local fallback was used for story generation because OPENAI_API_KEY is not configured.",
        "recovery_hint": "Set OPENAI_API_KEY in the environment or .env file.",
    }
    pipeline.evaluation_service.evaluate.return_value = EvaluationReport(
        grounding_score=0.92,
        coherence_score=0.88,
        redundancy_score=0.90,
        sentiment_fit_score=0.91,
        readability_score=0.87,
        flags=[],
        summary="Passed",
    )
    pipeline.evaluation_service.last_provider_status = {
        "stage": "evaluation",
        "execution_mode": "provider",
        "reason": None,
        "recovery_hint": None,
    }

    result = pipeline.run(
        StoryRequest(image_paths=["dummy.jpg"], sentiment="happy", max_sentences=3)
    )

    assert result.original_scene_observations == []
    assert result.sentence_alignment == [[1], [1, 2]]
    assert result.grounding_notes == [
        "entity continuity confirmed",
        "late frame remains ambiguous",
    ]
    assert [entry.stage for entry in result.provider_status] == [
        "scene_analysis",
        "narrative_planning",
        "story_generation",
        "evaluation",
    ]
    assert result.provider_status[2].execution_mode == "local_fallback"


def test_pipeline_uses_overridden_observations_for_corrected_generation() -> None:
    pipeline = StorytellingPipeline(
        image_preprocessing_service=MagicMock(),
        scene_analysis_service=MagicMock(),
        observation_override_service=MagicMock(),
        sequence_linking_service=MagicMock(),
        narrative_planning_service=MagicMock(),
        sentiment_control_service=MagicMock(),
        story_generation_service=MagicMock(),
        evaluation_service=MagicMock(),
    )

    from packages.core.models.sequence import NarrativePlan, SequenceMemory

    raw_observations = [
        SceneObservation(image_id=1, entities=["figure"], actions=["standing"]),
    ]
    effective_observations = [
        SceneObservation(
            image_id=1,
            entities=["woman with scarf"],
            actions=["reading a letter"],
        ),
    ]
    overrides = [
        SceneObservationOverride(
            image_id=1,
            main_entity="woman with scarf",
            visible_action="reading a letter",
        )
    ]

    pipeline.image_preprocessing_service.prepare.return_value = MagicMock()
    pipeline.scene_analysis_service.analyze.return_value = raw_observations
    pipeline.observation_override_service.apply.return_value = (effective_observations, overrides)
    pipeline.sequence_linking_service.build.return_value = SequenceMemory()
    pipeline.narrative_planning_service.plan.return_value = NarrativePlan(arc_type="test")
    pipeline.sentiment_control_service.resolve.return_value = MagicMock()
    pipeline.story_generation_service.generate.return_value = StoryDraft(
        title="Corrected Draft",
        story_text="A corrected grounded story.",
        sentence_alignment=[[1]],
        grounding_notes=["user correction applied"],
    )
    pipeline.evaluation_service.evaluate.return_value = EvaluationReport(
        grounding_score=0.92,
        coherence_score=0.90,
        redundancy_score=0.88,
        sentiment_fit_score=0.89,
        readability_score=0.90,
        flags=[],
        summary="Passed",
    )

    pipeline.run(
        StoryRequest(
            image_paths=["dummy.jpg"],
            sentiment="happy",
            max_sentences=3,
            analysis_overrides=overrides,
        )
    )

    assert pipeline.sequence_linking_service.build.call_args.args[0] == effective_observations
    assert pipeline.story_generation_service.generate.call_args.kwargs["observations"] == effective_observations
    assert pipeline.story_generation_service.generate.call_args.kwargs["applied_overrides"] == overrides


def test_pipeline_default_path_keeps_applied_overrides_empty() -> None:
    pipeline = StorytellingPipeline(
        image_preprocessing_service=MagicMock(),
        scene_analysis_service=MagicMock(),
        observation_override_service=MagicMock(),
        sequence_linking_service=MagicMock(),
        narrative_planning_service=MagicMock(),
        sentiment_control_service=MagicMock(),
        story_generation_service=MagicMock(),
        evaluation_service=MagicMock(),
    )

    from packages.core.models.sequence import NarrativePlan, SequenceMemory

    observations = [SceneObservation(image_id=1, entities=["dog"], actions=["walking"])]
    pipeline.image_preprocessing_service.prepare.return_value = MagicMock()
    pipeline.scene_analysis_service.analyze.return_value = observations
    pipeline.observation_override_service.apply.return_value = (observations, [])
    pipeline.sequence_linking_service.build.return_value = SequenceMemory()
    pipeline.narrative_planning_service.plan.return_value = NarrativePlan(arc_type="test")
    pipeline.sentiment_control_service.resolve.return_value = MagicMock()
    pipeline.story_generation_service.generate.return_value = StoryDraft(
        title="Unchanged Draft",
        story_text="The dog keeps walking.",
        sentence_alignment=[[1]],
        grounding_notes=["grounded"],
    )
    pipeline.evaluation_service.evaluate.return_value = EvaluationReport(
        grounding_score=0.92,
        coherence_score=0.90,
        redundancy_score=0.88,
        sentiment_fit_score=0.89,
        readability_score=0.90,
        flags=[],
        summary="Passed",
    )

    result = pipeline.run(
        StoryRequest(image_paths=["dummy.jpg"], sentiment="happy", max_sentences=3)
    )

    assert result.original_scene_observations == observations
    assert result.applied_overrides == []
