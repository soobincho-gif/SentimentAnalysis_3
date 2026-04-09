from __future__ import annotations

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment import SentimentProfile
from packages.core.models.sequence import NarrativePlan, SequenceMemory
from packages.core.models.story import STRICT_GROUNDING_GENERATION_MODE
from packages.core.models.story import StoryDraft
from packages.infra.provider_client import ProviderClient
from packages.prompts.story_generation_prompts import (
    STORY_GENERATION_SYSTEM_PROMPT,
    build_grounding_note,
    fallback_closing_ending,
    fallback_scene_ending,
    fallback_transition_ending,
    sentiment_generation_guidance,
    sentence_prefix_for_role,
)


class StoryGenerationService:
    """Generate a short grounded story from explicit intermediate contracts using a real provider."""

    def __init__(self, use_mock: bool = False) -> None:
        self.provider = ProviderClient(use_mock=use_mock)
        self.last_provider_status: dict[str, str | None] | None = None

    def generate(
        self,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        narrative_plan: NarrativePlan,
        sentiment_profile: SentimentProfile,
        max_sentences: int,
        applied_overrides: list[SceneObservationOverride] | None = None,
        generation_mode: str = "default",
    ) -> StoryDraft:
        if not self.provider.is_configured:
            self.last_provider_status = self._provider_status_payload(stage="story_generation")
            return self._fallback_generate(
                observations=observations,
                sequence_memory=sequence_memory,
                narrative_plan=narrative_plan,
                sentiment_profile=sentiment_profile,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="story generation"),
            )

        override_json = [
            override.model_dump_json(exclude_none=True)
            for override in (applied_overrides or [])
        ]
        prompt_text = (
            f"Generate a story of at most {max_sentences} sentences.\n"
            f"Tone/Sentiment: {sentiment_profile.label} ({', '.join(sentiment_profile.tone_keywords)})\n"
            f"Narrative Plan: {narrative_plan.model_dump_json()}\n"
            f"Sequence Memory: {sequence_memory.model_dump_json()}\n"
            f"Observations: {[obs.model_dump_json() for obs in observations]}\n"
        )
        if override_json:
            prompt_text += f"User Corrections: {override_json}\n"
        if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            prompt_text += (
                "STRICT GROUNDING MODE: prefer literal wording, stay close to explicit image evidence, "
                "and omit speculative transitions rather than smoothing them with invented detail.\n"
            )
        sentiment_guidance = sentiment_generation_guidance(sentiment_profile)
        if sentiment_guidance:
            prompt_text += f"Sentiment guidance: {sentiment_guidance}\n"
        
        draft = self.provider.generate_text(
            prompt=prompt_text,
            response_model=StoryDraft,
            system_prompt=STORY_GENERATION_SYSTEM_PROMPT,
            temperature=0.18 if generation_mode == STRICT_GROUNDING_GENERATION_MODE else 0.35,
        )
        if getattr(self.provider, "last_request_used_fallback", False):
            self.last_provider_status = self._provider_status_payload(stage="story_generation")
            return self._fallback_generate(
                observations=observations,
                sequence_memory=sequence_memory,
                narrative_plan=narrative_plan,
                sentiment_profile=sentiment_profile,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="story generation"),
            )
        
        # Enforce/enrich fallback alignment and grounding traces if the model missed them
        if not draft.sentence_alignment:
            draft.sentence_alignment = narrative_plan.sentence_image_map[:max_sentences]
            
        grounding_notes = [
            build_grounding_note(observation) for observation in observations
        ]
        if sequence_memory.unresolved_ambiguities:
            grounding_notes.append(sequence_memory.unresolved_ambiguities[0])
            
        draft.grounding_notes.extend(grounding_notes)
        self.last_provider_status = self._provider_status_payload(stage="story_generation")

        return draft

    def revise(
        self,
        previous_draft: StoryDraft,
        feedback_flags: list[str],
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        narrative_plan: NarrativePlan,
        sentiment_profile: SentimentProfile,
        max_sentences: int,
        applied_overrides: list[SceneObservationOverride] | None = None,
        generation_mode: str = "default",
    ) -> StoryDraft:
        if not self.provider.is_configured:
            self.last_provider_status = self._provider_status_payload(stage="story_revision")
            return self._fallback_generate(
                observations=observations,
                sequence_memory=sequence_memory,
                narrative_plan=narrative_plan,
                sentiment_profile=sentiment_profile,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="story revision"),
            )

        override_json = [
            override.model_dump_json(exclude_none=True)
            for override in (applied_overrides or [])
        ]
        prompt_text = (
            f"Please REVISE the following story draft.\n"
            f"The previous draft violated these critical evaluation constraints:\n"
            f"{', '.join(feedback_flags)}\n\n"
            f"Previous Draft Text: {previous_draft.story_text}\n\n"
            f"YOU MUST PRESERVE the following constraints exactly:\n"
            f"Tone/Sentiment: {sentiment_profile.label}\n"
            f"Narrative Plan: {narrative_plan.model_dump_json()}\n"
            f"Sequence Memory: {sequence_memory.model_dump_json()}\n"
            f"Observations: {[obs.model_dump_json() for obs in observations]}\n"
        )
        if override_json:
            prompt_text += f"User Corrections: {override_json}\n"
        if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            prompt_text += (
                "STRICT GROUNDING MODE remains active. Keep the revision literal, conservative, "
                "and tightly bound to the corrected observations.\n"
            )
        sentiment_guidance = sentiment_generation_guidance(sentiment_profile)
        if sentiment_guidance:
            prompt_text += f"Sentiment guidance: {sentiment_guidance}\n"
        
        system_prompt = (
            STORY_GENERATION_SYSTEM_PROMPT + 
            "\n\nCRITICAL FIX: Focus exclusively on repairing the evaluated failures while maintaining the authoritative plan."
        )
        
        draft = self.provider.generate_text(
            prompt=prompt_text,
            response_model=StoryDraft,
            system_prompt=system_prompt,
            temperature=0.12 if generation_mode == STRICT_GROUNDING_GENERATION_MODE else 0.22,
        )
        if getattr(self.provider, "last_request_used_fallback", False):
            self.last_provider_status = self._provider_status_payload(stage="story_revision")
            return self._fallback_generate(
                observations=observations,
                sequence_memory=sequence_memory,
                narrative_plan=narrative_plan,
                sentiment_profile=sentiment_profile,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="story revision"),
            )
        
        if not draft.sentence_alignment:
            draft.sentence_alignment = narrative_plan.sentence_image_map[:max_sentences]
            
        grounding_notes = [
            build_grounding_note(observation) for observation in observations
        ]
        if sequence_memory.unresolved_ambiguities:
            grounding_notes.append(sequence_memory.unresolved_ambiguities[0])
            
        draft.grounding_notes.extend(grounding_notes)
        self.last_provider_status = self._provider_status_payload(stage="story_revision")

        return draft

    def _fallback_generate(
        self,
        *,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        narrative_plan: NarrativePlan,
        sentiment_profile: SentimentProfile,
        max_sentences: int,
        generation_mode: str,
        fallback_note: str | None = None,
    ) -> StoryDraft:
        title = self._fallback_title(observations, sentiment_profile.label, narrative_plan)
        sentences: list[str] = []
        alignment: list[list[int]] = []

        if observations and len(sentences) < max_sentences:
            first_observation = observations[0]
            sentences.append(
                self._observation_sentence(
                    first_observation,
                    sentiment_profile=sentiment_profile,
                    prefix_role="opening",
                )
            )
            alignment.append([first_observation.image_id])

        if len(observations) > 1:
            for index in range(1, len(observations)):
                if len(sentences) >= max_sentences:
                    break
                previous = observations[index - 1]
                current = observations[index]
                remaining_slots = max_sentences - len(sentences)
                remaining_observations_including_current = len(observations) - index
                reserve_closing_slot = 1

                if remaining_slots > (remaining_observations_including_current + reserve_closing_slot - 1):
                    sentences.append(
                        self._transition_sentence(
                            previous,
                            current,
                            sentiment_profile=sentiment_profile,
                            generation_mode=generation_mode,
                        )
                    )
                    alignment.append([previous.image_id, current.image_id])

                if len(sentences) >= max_sentences:
                    break
                sentences.append(
                    self._observation_sentence(
                        current,
                        sentiment_profile=sentiment_profile,
                        prefix_role="middle",
                    )
                )
                alignment.append([current.image_id])

        if len(observations) > 1 and len(sentences) < max_sentences:
            sentences.append(
                self._closing_sentence(
                    observations,
                    sequence_memory,
                    sentiment_profile=sentiment_profile,
                )
            )
            alignment.append([observation.image_id for observation in observations])

        grounding_notes = [
            fallback_note
            or "Local deterministic fallback was used because no OpenAI API key is configured."
        ]
        grounding_notes.extend(build_grounding_note(observation) for observation in observations)
        if sequence_memory.unresolved_ambiguities:
            grounding_notes.append(sequence_memory.unresolved_ambiguities[0])

        return StoryDraft(
            title=title,
            story_text=" ".join(sentences),
            sentence_alignment=alignment,
            grounding_notes=grounding_notes,
        )

    def _fallback_title(
        self,
        observations: list[SceneObservation],
        sentiment_label: str,
        narrative_plan: NarrativePlan,
    ) -> str:
        if narrative_plan.title_candidates:
            return narrative_plan.title_candidates[0]
        subject = observations[0].entities[0] if observations and observations[0].entities else "Scene"
        return f"{sentiment_label.title()} View of {subject.title()}"

    def _observation_sentence(
        self,
        observation: SceneObservation,
        *,
        sentiment_profile: SentimentProfile,
        prefix_role: str,
    ) -> str:
        entity = observation.entities[0] if observation.entities else "a subject"
        setting = observation.setting or "an unresolved setting"
        action = observation.actions[0] if observation.actions else "remaining visible"
        prefix = sentence_prefix_for_role(sentiment_profile, prefix_role)
        ending = fallback_scene_ending(sentiment_profile.label)
        return f"{prefix} image {observation.image_id} shows {entity} {action} in {setting}, {ending}."

    def _transition_sentence(
        self,
        previous: SceneObservation,
        current: SceneObservation,
        *,
        sentiment_profile: SentimentProfile,
        generation_mode: str,
    ) -> str:
        continuity = (
            "The same subject appears to continue into the next moment"
            if current.same_subject_as_previous is True
            else "The sequence then shifts to the next visible moment"
        )
        if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            return f"{continuity}, without adding details beyond what the images clearly support."
        transition = fallback_transition_ending(sentiment_profile.label)
        return f"{continuity}, and {transition}."

    def _provider_status_payload(self, *, stage: str) -> dict[str, str | None]:
        if hasattr(self.provider, "status_payload"):
            return self.provider.status_payload(stage=stage)
        if getattr(self.provider, "last_request_used_fallback", False):
            reason = (
                self.provider.describe_fallback(stage=stage)
                if hasattr(self.provider, "describe_fallback")
                else f"Local fallback was used for {stage}."
            )
            return {
                "stage": stage,
                "execution_mode": "local_fallback",
                "reason": reason,
                "recovery_hint": None,
            }
        return {
            "stage": stage,
            "execution_mode": "provider",
            "reason": None,
            "recovery_hint": None,
        }

    def _closing_sentence(
        self,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        *,
        sentiment_profile: SentimentProfile,
    ) -> str:
        closing = fallback_closing_ending(sentiment_profile.label)
        if sequence_memory.setting_progression:
            path = " to ".join(sequence_memory.setting_progression[:2])
            return f"Taken together, the images move from {path}, {closing}."
        final_setting = observations[-1].setting or "the final frame"
        return f"Taken together, the sequence settles in {final_setting}, {closing}."
