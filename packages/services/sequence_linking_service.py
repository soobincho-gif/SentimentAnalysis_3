from __future__ import annotations

from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import SequenceMemory


class SequenceLinkingService:
    """Turn per-image observations into reusable sequence memory via interpretable heuristics."""

    def __init__(self, use_mock: bool = False) -> None:
        pass

    def build(self, observations: list[SceneObservation]) -> SequenceMemory:
        recurring_entities = self._identify_recurring_entities(observations)
        setting_progression = self._propagate_settings(observations)
        event_candidates = self._build_event_chain(observations)
        unresolved_ambiguities = self._detect_ambiguities(observations, recurring_entities)

        return SequenceMemory(
            recurring_entities=recurring_entities,
            setting_progression=setting_progression,
            event_candidates=event_candidates,
            unresolved_ambiguities=unresolved_ambiguities,
        )

    def _identify_recurring_entities(self, observations: list[SceneObservation]) -> list[str]:
        # Word overlap heuristic to catch "brown dog" and "dog" but avoid "man" in "woman"
        matches: set[str] = set()
        blocked_pairs: set[tuple[int, int]] = set()

        for index in range(1, len(observations)):
            current = observations[index]
            previous = observations[index - 1]
            pair = (previous.image_id, current.image_id)

            if current.same_subject_as_previous is False:
                blocked_pairs.add(pair)
                continue

            if (
                current.same_subject_as_previous is True
                and previous.entities
                and current.entities
            ):
                matches.add(previous.entities[0].lower())
                matches.add(current.entities[0].lower())

        for i, obs1 in enumerate(observations):
            for e1 in obs1.entities:
                set1 = set(e1.lower().split())
                for obs2 in observations[i + 1 :]:
                    pair = (obs1.image_id, obs2.image_id)
                    if pair in blocked_pairs:
                        continue
                    for e2 in obs2.entities:
                        set2 = set(e2.lower().split())
                        if set1 & set2:
                            matches.add(e1.lower())
                            matches.add(e2.lower())

        # Reduce to the shortest overlapping terms
        recurring: set[str] = set()
        for m1 in matches:
            set_m1 = set(m1.split())
            # Is m1 a "longer version" of any other match?
            is_subsumed = False
            for m2 in matches:
                if m1 != m2:
                    set_m2 = set(m2.split())
                    if set_m2.issubset(set_m1) and len(m2) < len(m1):
                        is_subsumed = True
                        break
            if not is_subsumed:
                recurring.add(m1)
                
        return sorted(list(recurring))

    def _propagate_settings(self, observations: list[SceneObservation]) -> list[str]:
        # Propagate setting if visually ambiguous/missing
        progression: list[str] = []
        current_setting = "unspecified location"
        for obs in observations:
            if obs.setting:
                current_setting = obs.setting
            progression.append(current_setting)
        return progression

    def _build_event_chain(self, observations: list[SceneObservation]) -> list[str]:
        chain: list[str] = []
        for obs in observations:
            parts = []
            if obs.entities:
                parts.append(f"{', '.join(obs.entities)}")
            if obs.actions:
                parts.append(f"{', '.join(obs.actions)}")
            if obs.objects:
                parts.append(f"with {', '.join(obs.objects)}")
                
            if parts:
                chain.append(f"Image {obs.image_id}: {' '.join(parts)}")
            else:
                chain.append(f"Image {obs.image_id}: visual beat")
        return chain

    def _detect_ambiguities(self, observations: list[SceneObservation], recurring: list[str]) -> list[str]:
        ambiguities: list[str] = []
        continuity_confirmed = any(
            observation.same_subject_as_previous is True for observation in observations[1:]
        )

        if len(observations) > 1 and not recurring and not continuity_confirmed:
            ambiguities.append("No clear recurring subjects detected. Sequence continuity is uncertain.")
            
        settings = [obs.setting for obs in observations if obs.setting]
        if len(set(settings)) > len(observations) / 2 and not recurring:
            ambiguities.append("Frequent setting changes without stable subjects. Risk of disconnected narration.")
            
        for obs in observations:
            if obs.uncertainty_notes:
                ambiguities.append(f"Image {obs.image_id} has limited cues: {obs.uncertainty_notes[0]}")
                
        return ambiguities
