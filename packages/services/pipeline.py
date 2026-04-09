from __future__ import annotations

from packages.core.models.story import (
    ProviderStageStatus,
    StoryRequest,
    StoryResult,
    STRICT_GROUNDING_GENERATION_MODE,
)
from packages.core.models.sentiment import SentimentProfile
from packages.infra.sentiment_run_logger import SentimentRunLogger
from packages.services.evaluation_service import EvaluationService
from packages.services.image_preprocessing_service import ImagePreprocessingService
from packages.services.narrative_planning_service import NarrativePlanningService
from packages.services.observation_override_service import ObservationOverrideService
from packages.services.scene_analysis_service import SceneAnalysisService
from packages.services.sentiment_control_service import SentimentControlService
from packages.services.sequence_linking_service import SequenceLinkingService
from packages.services.story_generation_service import StoryGenerationService


class StorytellingPipeline:
    """Thin orchestration layer for the MVP storytelling flow."""

    def __init__(
        self,
        image_preprocessing_service: ImagePreprocessingService,
        scene_analysis_service: SceneAnalysisService,
        observation_override_service: ObservationOverrideService,
        sequence_linking_service: SequenceLinkingService,
        narrative_planning_service: NarrativePlanningService,
        sentiment_control_service: SentimentControlService,
        story_generation_service: StoryGenerationService,
        evaluation_service: EvaluationService,
        sentiment_run_logger: SentimentRunLogger | None = None,
    ) -> None:
        self.image_preprocessing_service = image_preprocessing_service
        self.scene_analysis_service = scene_analysis_service
        self.observation_override_service = observation_override_service
        self.sequence_linking_service = sequence_linking_service
        self.narrative_planning_service = narrative_planning_service
        self.sentiment_control_service = sentiment_control_service
        self.story_generation_service = story_generation_service
        self.evaluation_service = evaluation_service
        self.sentiment_run_logger = sentiment_run_logger

    def run(self, request: StoryRequest) -> StoryResult:
        provider_status: list[ProviderStageStatus] = []
        ordered_images = self.image_preprocessing_service.prepare(request.image_paths)
        scene_observations = self.scene_analysis_service.analyze(ordered_images)
        self._append_provider_status(provider_status, self.scene_analysis_service)
        effective_observations, applied_overrides = self.observation_override_service.apply(
            scene_observations,
            request.analysis_overrides,
        )
        sequence_memory = self.sequence_linking_service.build(effective_observations)
        narrative_plan = self.narrative_planning_service.plan(
            observations=effective_observations,
            sequence_memory=sequence_memory,
            max_sentences=request.max_sentences,
            applied_overrides=applied_overrides,
            generation_mode=request.generation_mode,
        )
        self._append_provider_status(provider_status, self.narrative_planning_service)
        sentiment_profile = self.sentiment_control_service.resolve(
            request.sentiment,
            generation_mode=request.generation_mode,
        )
        story_draft = self.story_generation_service.generate(
            observations=effective_observations,
            sequence_memory=sequence_memory,
            narrative_plan=narrative_plan,
            sentiment_profile=sentiment_profile,
            max_sentences=request.max_sentences,
            applied_overrides=applied_overrides,
            generation_mode=request.generation_mode,
        )
        self._append_provider_status(provider_status, self.story_generation_service)
        evaluation_report = self.evaluation_service.evaluate(
            story_draft=story_draft,
            observations=effective_observations,
            sequence_memory=sequence_memory,
            sentiment_profile=sentiment_profile,
            generation_mode=request.generation_mode,
        )
        self._append_provider_status(provider_status, self.evaluation_service)

        max_attempts = 2 if request.generation_mode != STRICT_GROUNDING_GENERATION_MODE else 3
        attempts = 0
        while evaluation_report.flags and attempts < max_attempts:
            # Rejection trigger hit! Ask generation to safely refine it.
            story_draft = self.story_generation_service.revise(
                previous_draft=story_draft,
                feedback_flags=evaluation_report.flags,
                observations=effective_observations,
                sequence_memory=sequence_memory,
                narrative_plan=narrative_plan,
                sentiment_profile=sentiment_profile,
                max_sentences=request.max_sentences,
                applied_overrides=applied_overrides,
                generation_mode=request.generation_mode,
            )
            # Re-evaluate it
            evaluation_report = self.evaluation_service.evaluate(
                story_draft=story_draft,
                observations=effective_observations,
                sequence_memory=sequence_memory,
                sentiment_profile=sentiment_profile,
                generation_mode=request.generation_mode,
            )
            self._append_provider_status(provider_status, self.story_generation_service)
            self._append_provider_status(provider_status, self.evaluation_service)
            attempts += 1

        result = StoryResult(
            title=story_draft.title,
            story_text=story_draft.story_text,
            original_scene_observations=scene_observations,
            scene_observations=effective_observations,
            sequence_memory=sequence_memory,
            narrative_plan=narrative_plan if request.include_debug else None,
            evaluation_report=evaluation_report,
            sentence_alignment=story_draft.sentence_alignment,
            grounding_notes=story_draft.grounding_notes,
            provider_status=provider_status,
            applied_overrides=applied_overrides,
            generation_mode=request.generation_mode,
            revision_attempts=attempts,
            is_fallback=(attempts >= max_attempts and bool(evaluation_report.flags)),
        )
        self._record_sentiment_run(
            request=request,
            sentiment_profile=sentiment_profile,
            result=result,
        )
        return result

    def _append_provider_status(
        self,
        provider_status: list[ProviderStageStatus],
        service: object,
    ) -> None:
        payload = getattr(service, "last_provider_status", None)
        if payload is None or not isinstance(payload, dict):
            return
        provider_status.append(ProviderStageStatus.model_validate(payload))

    def _record_sentiment_run(
        self,
        *,
        request: StoryRequest,
        sentiment_profile: SentimentProfile,
        result: StoryResult,
    ) -> None:
        if self.sentiment_run_logger is None:
            return
        try:
            self.sentiment_run_logger.record(
                request=request,
                sentiment_profile=sentiment_profile,
                result=result,
            )
        except Exception:
            # Logging should never block story generation.
            return
