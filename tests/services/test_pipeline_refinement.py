from __future__ import annotations

from unittest.mock import MagicMock
from packages.core.models.story import StoryRequest, StoryDraft
from packages.core.models.evaluation import EvaluationReport
from packages.services.pipeline import StorytellingPipeline

def test_revision_loop_triggers_and_stops_when_compliant() -> None:
    # 1. Setup mock services
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
    
    from packages.core.models.sequence import SequenceMemory, NarrativePlan
    
    # Normally scene analysis returns observations. We use our fixture directly.
    pipeline.scene_analysis_service.analyze.return_value = []
    pipeline.observation_override_service.apply.return_value = ([], [])
    pipeline.sequence_linking_service.build.return_value = SequenceMemory()
    pipeline.narrative_planning_service.plan.return_value = NarrativePlan(arc_type="test")
    pipeline.sentiment_control_service.resolve.return_value = MagicMock()
    
    # Generate returns a poor draft
    pipeline.story_generation_service.generate.return_value = StoryDraft(
        title="Bad Draft", story_text="Failed", sentence_alignment=[], grounding_notes=[]
    )
    
    # Revise returns an improved draft
    pipeline.story_generation_service.revise.return_value = StoryDraft(
        title="Good Draft", story_text="Passed", sentence_alignment=[], grounding_notes=[]
    )
    
    # Evaluate naturally returns flags first, then passes
    pipeline.evaluation_service.evaluate.side_effect = [
        EvaluationReport(
            grounding_score=0.5, coherence_score=0.5, redundancy_score=0.5, 
            sentiment_fit_score=0.5, readability_score=0.5, flags=["grounding_issue"], summary="Failed"
        ),
        EvaluationReport(
            grounding_score=0.9, coherence_score=0.9, redundancy_score=0.9, 
            sentiment_fit_score=0.9, readability_score=0.9, flags=[], summary="Passed"
        )
    ]
    
    # 2. Run
    req = StoryRequest(image_paths=["dummy.jpg"], sentiment="happy", max_sentences=3)
    result = pipeline.run(req)
    
    # 3. Assert loops triggered once
    assert pipeline.story_generation_service.generate.call_count == 1
    assert pipeline.story_generation_service.revise.call_count == 1
    assert pipeline.evaluation_service.evaluate.call_count == 2
    
    # It stops correctly when compliant
    assert result.story_text == "Passed"


def test_revision_loop_respects_max_attempts_and_does_safe_fallback() -> None:
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
    
    from packages.core.models.sequence import SequenceMemory, NarrativePlan

    pipeline.scene_analysis_service.analyze.return_value = []
    pipeline.observation_override_service.apply.return_value = ([], [])
    pipeline.sequence_linking_service.build.return_value = SequenceMemory()
    pipeline.narrative_planning_service.plan.return_value = NarrativePlan(arc_type="test")
    pipeline.sentiment_control_service.resolve.return_value = MagicMock()
    
    # Continually returns a bad draft
    pipeline.story_generation_service.generate.return_value = StoryDraft(
        title="Bad Draft", story_text="Failed Generation", sentence_alignment=[], grounding_notes=[]
    )
    pipeline.story_generation_service.revise.return_value = StoryDraft(
        title="Still Bad", story_text="Failed Revision", sentence_alignment=[], grounding_notes=[]
    )
    
    # Evaluate constantly flags
    pipeline.evaluation_service.evaluate.return_value = EvaluationReport(
        grounding_score=0.5, coherence_score=0.5, redundancy_score=0.5, 
        sentiment_fit_score=0.5, readability_score=0.5, flags=["stubborn constraint violation"], summary="Failed"
    )
    
    req = StoryRequest(image_paths=["dummy.jpg"], sentiment="happy", max_sentences=3)
    result = pipeline.run(req)
    
    # loop hits max_attempts=2 (generating 1 + revise 2 = 3 evaluates)
    assert pipeline.story_generation_service.revise.call_count == 2
    assert pipeline.evaluation_service.evaluate.call_count == 3
    
    # Safe fallback returns the latest draft but with explicit failure flags attached
    assert result.story_text == "Failed Revision"
    assert "stubborn constraint violation" in result.evaluation_report.flags
