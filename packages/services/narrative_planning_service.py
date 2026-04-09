from __future__ import annotations

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation
from packages.core.models.story import STRICT_GROUNDING_GENERATION_MODE
from packages.core.models.sequence import NarrativePlan, SequenceMemory
from packages.infra.provider_client import ProviderClient
from packages.prompts.narrative_planning_prompts import NARRATIVE_PLANNING_SYSTEM_PROMPT


class NarrativePlanningService:
    """Build a constrained narrative plan via Provider without generating final prose."""

    def __init__(self, use_mock: bool = False) -> None:
        self.provider = ProviderClient(use_mock=use_mock)
        self.last_provider_status: dict[str, str | None] | None = None

    def plan(
        self,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        max_sentences: int,
        applied_overrides: list[SceneObservationOverride] | None = None,
        generation_mode: str = "default",
    ) -> NarrativePlan:
        if not self.provider.is_configured:
            self.last_provider_status = self._provider_status_payload(stage="narrative_planning")
            return self._fallback_plan(
                observations=observations,
                sequence_memory=sequence_memory,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
            )

        override_json = [
            override.model_dump_json(exclude_none=True)
            for override in (applied_overrides or [])
        ]
        prompt_text = (
            f"Generate a robust narrative plan for a story spanning {len(observations)} images.\n"
            f"Maximum sentences allowed: {max_sentences}\n\n"
            
            f"--- AUTHORITATIVE STRUCTURAL CONSTRAINTS ---\n"
            f"Sequence Memory: {sequence_memory.model_dump_json()}\n"
            f"Observations: {[obs.model_dump_json() for obs in observations]}\n\n"
            
            f"Ensure sentence_image_map arrays map EXACTLY to the chronological image_id flow. "
            f"For title_candidates, keep them rooted in the visible facts.\n"
            f"For beat_list, use Sequence Memory's event_candidates if present.\n"
            f"If unresolved_ambiguities exist in Sequence Memory, your allowed_inferences MUST reflect safe, conservative transitions."
        )

        if override_json:
            prompt_text += (
                "\n\nTreat the following user corrections as authoritative over any ambiguous image reading:\n"
                f"{override_json}\n"
            )
        if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            prompt_text += (
                "\nSTRICT GROUNDING MODE: Minimize allowed_inferences, prefer omission over speculation, "
                "and expand forbidden_claims to block soft but unsupported story bridges."
            )
        
        plan = self.provider.generate_text(
            prompt=prompt_text,
            response_model=NarrativePlan,
            system_prompt=NARRATIVE_PLANNING_SYSTEM_PROMPT,
            temperature=0.2,
        )
        if getattr(self.provider, "last_request_used_fallback", False):
            self.last_provider_status = self._provider_status_payload(stage="narrative_planning")
            return self._fallback_plan(
                observations=observations,
                sequence_memory=sequence_memory,
                max_sentences=max_sentences,
                generation_mode=generation_mode,
            )
        self.last_provider_status = self._provider_status_payload(stage="narrative_planning")
        return plan

    def _fallback_plan(
        self,
        *,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        max_sentences: int,
        generation_mode: str,
    ) -> NarrativePlan:
        beat_list = [
            self._observation_beat(observation)
            for observation in observations
        ]
        sentence_image_map = [[observation.image_id] for observation in observations]

        if len(observations) > 1 and len(sentence_image_map) < max_sentences:
            for index in range(1, len(observations)):
                if len(sentence_image_map) >= max_sentences:
                    break
                sentence_image_map.append([observations[index - 1].image_id, observations[index].image_id])
                beat_list.append(
                    f"Link image {observations[index - 1].image_id} to image {observations[index].image_id} conservatively."
                )

        if len(observations) > 1 and len(sentence_image_map) < max_sentences:
            sentence_image_map.append([observation.image_id for observation in observations])
            beat_list.append("Close the sequence with a grounded summary.")

        allowed_inferences = [] if generation_mode == STRICT_GROUNDING_GENERATION_MODE else [
            "time passes between adjacent images",
            "the sequence can be described in chronological order",
        ]
        forbidden_claims = [
            "Do not introduce unseen characters or events.",
            "Do not claim emotions or causes that are not visually supported.",
        ]
        if sequence_memory.unresolved_ambiguities:
            forbidden_claims.append("Do not claim a stable identity when continuity remains uncertain.")

        title_subject = observations[0].entities[0] if observations and observations[0].entities else "Scene"
        title_setting = observations[0].setting if observations and observations[0].setting else "Sequence"

        return NarrativePlan(
            arc_type="grounded chronological sequence",
            beat_list=beat_list[:max_sentences],
            sentence_image_map=sentence_image_map[:max_sentences],
            allowed_inferences=allowed_inferences,
            forbidden_claims=forbidden_claims,
            title_candidates=[
                f"{title_subject.title()} in {title_setting.title()}",
                f"A Grounded View of {title_setting.title()}",
            ],
        )

    def _observation_beat(self, observation: SceneObservation) -> str:
        entity = observation.entities[0] if observation.entities else "a subject"
        action = observation.actions[0] if observation.actions else "remains visible"
        setting = observation.setting or "an unresolved setting"
        return f"Image {observation.image_id}: keep {entity} grounded while it is {action} in {setting}."

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
