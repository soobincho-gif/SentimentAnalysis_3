from __future__ import annotations

from packages.core.models.scene import SceneObservation
from packages.services.sequence_linking_service import SequenceLinkingService


def test_linking_identifies_same_main_entity_across_frames() -> None:
    service = SequenceLinkingService()
    observations = [
        SceneObservation(image_id=1, entities=["brown dog"], actions=["walking"]),
        SceneObservation(image_id=2, entities=["dog"], actions=["running"]),
        SceneObservation(image_id=3, entities=["small dog"], actions=["resting"])
    ]
    memory = service.build(observations)
    assert "dog" in memory.recurring_entities
    assert len(memory.recurring_entities) == 1


def test_linking_preserves_setting_progression() -> None:
    service = SequenceLinkingService()
    observations = [
        SceneObservation(image_id=1, entities=["cat"], setting="living room"),
        SceneObservation(image_id=2, entities=["cat"], setting=""),
        SceneObservation(image_id=3, entities=["cat"], setting="kitchen"),
        SceneObservation(image_id=4, entities=["cat"], setting="")
    ]
    memory = service.build(observations)
    assert memory.setting_progression == ["living room", "living room", "kitchen", "kitchen"]


def test_linking_prevents_over_merging_distinct_entities() -> None:
    service = SequenceLinkingService()
    observations = [
        SceneObservation(image_id=1, entities=["cat"], actions=["sleeping"]),
        SceneObservation(image_id=2, entities=["dog"], actions=["barking"]),
        SceneObservation(image_id=3, entities=["bird"], actions=["flying"])
    ]
    memory = service.build(observations)
    # Distinct entities should NOT be merged
    assert memory.recurring_entities == []
    # Ambiguity should be flagged since characters keep changing
    assert "No clear recurring subjects detected. Sequence continuity is uncertain." in memory.unresolved_ambiguities


def test_linking_flags_uncertain_continuity_with_rapid_setting_changes() -> None:
    service = SequenceLinkingService()
    observations = [
        SceneObservation(image_id=1, entities=["man"], setting="park"),
        SceneObservation(image_id=2, entities=["woman"], setting="cafe"),
        SceneObservation(image_id=3, entities=["child"], setting="school")
    ]
    memory = service.build(observations)
    assert any("Frequent setting changes without stable subjects" in note for note in memory.unresolved_ambiguities)
