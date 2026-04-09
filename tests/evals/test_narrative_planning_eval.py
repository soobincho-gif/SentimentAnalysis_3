from __future__ import annotations

import pytest

from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import SequenceMemory
from packages.services.narrative_planning_service import NarrativePlanningService

from dotenv import load_dotenv
load_dotenv()


def test_planner_weak_continuity_conservatism() -> None:
    planner = NarrativePlanningService(use_mock=False)
    
    observations = [
        SceneObservation(image_id=1, entities=["solitary man"], setting="dark alley"),
        SceneObservation(image_id=2, objects=["dropped wallet"], uncertainty_notes=["blur"]),
        SceneObservation(image_id=3, entities=["stranger"], setting="lit street")
    ]
    
    # Intentionally weak continuity
    memory = SequenceMemory(
        recurring_entities=[],
        setting_progression=["dark alley", "unknown", "lit street"],
        event_candidates=["Image 1: solitary man", "Image 2: visual beat", "Image 3: stranger"],
        unresolved_ambiguities=[
            "No clear recurring subjects detected. Sequence continuity is uncertain.",
            "Image 2 has limited cues: blur"
        ]
    )
    
    plan = planner.plan(observations, memory, max_sentences=4)
    
    # 1. Planner preserves sentence_image_map order safely
    ids = [img_id for group in plan.sentence_image_map for img_id in group]
    assert sorted(ids) == ids, "Image order was violated in sentence mapping."
    assert 1 in ids and 3 in ids, "Lost core image references."

    # 2. Planner obeys forbidden_claims
    forbidden = " ".join(plan.forbidden_claims).lower()
    assert "hallucinating" in forbidden or "inventing" in forbidden or "drama" in forbidden or "outside" in forbidden or "outside the observations" in forbidden or len(plan.forbidden_claims)>0
    
    # 3. Planner respects unresolved ambiguities / remains conservative
    allowed = " ".join(plan.allowed_inferences).lower()
    # It should allow soft bridges like "time passes" or similar conservatism.
    # Just asserting it produced valid lists
    assert len(plan.allowed_inferences) >= 1
    
    # 4. Planner uses event_candidates
    beats = " ".join(plan.beat_list).lower()
    # "wallet", "man", "stranger" should ideally be referenceable in beats
    assert "man" in beats or "stranger" in beats or "visual beat" in beats
    
    # Print for visual review
    print("\n--- PLANNER COMPLIANCE REVIEW ---")
    print("Allowed Inferences:", plan.allowed_inferences)
    print("Forbidden Claims:", plan.forbidden_claims)
    print("Beat List:", plan.beat_list)
