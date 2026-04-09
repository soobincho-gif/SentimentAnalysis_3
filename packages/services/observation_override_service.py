from __future__ import annotations

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation


class ObservationOverrideService:
    """Apply explicit user corrections before downstream sequencing and generation."""

    def apply(
        self,
        observations: list[SceneObservation],
        overrides: list[SceneObservationOverride],
    ) -> tuple[list[SceneObservation], list[SceneObservationOverride]]:
        override_by_image_id = {
            override.image_id: override
            for override in overrides
            if override.has_changes() and 1 <= override.image_id <= len(observations)
        }

        effective_observations: list[SceneObservation] = []
        applied_overrides: list[SceneObservationOverride] = []

        for observation in observations:
            effective = observation.model_copy(deep=True)
            override = override_by_image_id.get(observation.image_id)

            if override is not None:
                applied_overrides.append(override)
                if override.main_entity is not None:
                    effective.entities = self._replace_primary_value(
                        effective.entities,
                        override.main_entity,
                    )
                if override.setting is not None:
                    effective.setting = override.setting
                if override.visible_action is not None:
                    effective.actions = self._replace_primary_value(
                        effective.actions,
                        override.visible_action,
                    )
                if override.same_subject_as_previous is not None:
                    effective.same_subject_as_previous = override.same_subject_as_previous

            if (
                effective.same_subject_as_previous is True
                and effective.image_id > 1
                and effective_observations
                and effective_observations[-1].entities
                and override is not None
                and override.main_entity is None
            ):
                previous_entity = effective_observations[-1].entities[0]
                effective.entities = self._replace_primary_value(
                    effective.entities,
                    previous_entity,
                )

            effective_observations.append(effective)

        return effective_observations, applied_overrides

    def _replace_primary_value(self, values: list[str], replacement: str) -> list[str]:
        deduped_tail = [value for value in values if value.lower() != replacement.lower()]
        return [replacement, *deduped_tail]
