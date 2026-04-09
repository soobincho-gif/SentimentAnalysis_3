from __future__ import annotations

from packages.services.evaluation_service import EvaluationService
from packages.services.image_preprocessing_service import ImagePreprocessingService
from packages.services.narrative_planning_service import NarrativePlanningService
from packages.services.observation_override_service import ObservationOverrideService
from packages.services.pipeline import StorytellingPipeline
from packages.infra.sentiment_run_logger import SentimentRunLogger
from packages.services.scene_analysis_service import SceneAnalysisService
from packages.services.sentiment_control_service import SentimentControlService
from packages.services.sequence_linking_service import SequenceLinkingService
from packages.services.story_generation_service import StoryGenerationService


def build_pipeline(use_mock: bool = False) -> StorytellingPipeline:
    return StorytellingPipeline(
        image_preprocessing_service=ImagePreprocessingService(),
        scene_analysis_service=SceneAnalysisService(use_mock=use_mock),
        observation_override_service=ObservationOverrideService(),
        sequence_linking_service=SequenceLinkingService(use_mock=use_mock),
        narrative_planning_service=NarrativePlanningService(use_mock=use_mock),
        sentiment_control_service=SentimentControlService(),
        story_generation_service=StoryGenerationService(use_mock=use_mock),
        evaluation_service=EvaluationService(use_mock=use_mock),
        sentiment_run_logger=SentimentRunLogger(),
    )
