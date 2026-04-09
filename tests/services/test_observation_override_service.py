from __future__ import annotations

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation
from packages.services.observation_override_service import ObservationOverrideService


def test_override_service_applies_structured_corrections_to_effective_observations() -> None:
    service = ObservationOverrideService()
    observations = [
        SceneObservation(image_id=1, entities=["person"], setting="street", actions=["walking"]),
        SceneObservation(image_id=2, entities=["figure"], setting="alley", actions=["standing"]),
    ]
    overrides = [
        SceneObservationOverride(
            image_id=2,
            main_entity="same woman",
            setting="cafe entrance",
            visible_action="opening the door",
            same_subject_as_previous=True,
            generation_note="Keep the subject consistent across frames.",
        )
    ]

    effective_observations, applied_overrides = service.apply(observations, overrides)

    assert applied_overrides == overrides
    assert effective_observations[1].entities[0] == "same woman"
    assert effective_observations[1].setting == "cafe entrance"
    assert effective_observations[1].actions[0] == "opening the door"
    assert effective_observations[1].same_subject_as_previous is True


def test_override_service_leaves_observations_unchanged_without_active_corrections() -> None:
    service = ObservationOverrideService()
    observations = [
        SceneObservation(image_id=1, entities=["person"], setting="street", actions=["walking"]),
    ]

    effective_observations, applied_overrides = service.apply(
        observations,
        [SceneObservationOverride(image_id=1)],
    )

    assert applied_overrides == []
    assert effective_observations[0] == observations[0]
