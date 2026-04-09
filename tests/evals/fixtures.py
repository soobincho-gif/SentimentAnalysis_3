from __future__ import annotations

from dataclasses import dataclass
from packages.core.models.scene import SceneObservation

@dataclass
class EvalCase:
    name: str
    sentiment: str
    observations: list[SceneObservation]
    expected_success_criteria: str
    failure_risks: str
    should_not_happen: str

EVAL_CASES = [
    EvalCase(
        name="simple_chronological_happy_flow",
        sentiment="happy",
        observations=[
            SceneObservation(image_id=1, entities=["dog", "owner"], actions=["walking"], setting="park"),
            SceneObservation(image_id=2, entities=["dog"], objects=["ball"], actions=["playing"], setting="park"),
            SceneObservation(image_id=3, entities=["dog", "owner"], actions=["resting"], setting="home")
        ],
        expected_success_criteria="Story reads smoothly, correctly infers returning home.",
        failure_risks="Missing the transition from park to home.",
        should_not_happen="Story gets stuck at the park or invents a dramatic accident."
    ),
    EvalCase(
        name="visually_ambiguous_sequence",
        sentiment="mysterious",
        observations=[
            SceneObservation(image_id=1, entities=["shadow"], setting="alley", uncertainty_notes=["very dark image"]),
            SceneObservation(image_id=2, objects=["dropped key"], uncertainty_notes=["blurry focus"]),
            SceneObservation(image_id=3, entities=["person"], actions=["looking back"])
        ],
        expected_success_criteria="Explicitly uses uncertainty as part of the mysterious tone without fabricating clear events.",
        failure_risks="Model might hallucinate a full detective plot.",
        should_not_happen="Complete fabrication of a specific crime or chase scene not supported by image cues."
    ),
    EvalCase(
        name="recurring_entity_consistency_case",
        sentiment="heartwarming",
        observations=[
            SceneObservation(image_id=1, entities=["old man", "cat"], setting="living room"),
            SceneObservation(image_id=2, entities=["old man"], actions=["pouring milk"], setting="kitchen"),
            SceneObservation(image_id=3, entities=["cat"], actions=["drinking"], setting="kitchen")
        ],
        expected_success_criteria="Maintains the relationship between 'old man' and 'cat' seamlessly despite scene cuts.",
        failure_risks="Failing to link the milk poured in #2 with the cat drinking in #3.",
        should_not_happen="Treating the cat in #3 as a newly introduced stray animal."
    ),
    EvalCase(
        name="sentiment_sensitive_case",
        sentiment="suspenseful",
        observations=[
            SceneObservation(image_id=1, entities=["woman"], setting="empty hallway"),
            SceneObservation(image_id=2, objects=["half-open door"], actions=["approaching"]),
            SceneObservation(image_id=3, entities=["woman"], visible_mood="surprised", setting="inside room")
        ],
        expected_success_criteria="Tone builds tension up to the surprise without making up the room's contents.",
        failure_risks="Tone falling flat (reads like a real estate listing).",
        should_not_happen="Revealing what is inside the room (not grounded in observations)."
    ),
    EvalCase(
        name="grounding_risk_case",
        sentiment="playful",
        observations=[
            SceneObservation(image_id=1, entities=["two children"], actions=["running"], setting="field")
        ],
        expected_success_criteria="Tells a playful story using ONLY the field and running children. Stays within 1 vignette.",
        failure_risks="Padding the story with made-up toys, events, or parents.",
        should_not_happen="Adding objects like kites or balls that are missing from the observation."
    ),
    EvalCase(
        name="redundancy_risk_case",
        sentiment="happy",
        observations=[
            SceneObservation(image_id=1, actions=["staring out window"], setting="bedroom"),
            SceneObservation(image_id=2, actions=["looking out window"], setting="bedroom"),
            SceneObservation(image_id=3, actions=["watching through window"], setting="bedroom")
        ],
        expected_success_criteria="Aggregates the repeated action naturally without repeating identical sentence structures.",
        failure_risks="Generating three identical sentences in a row ('The person looks. Then the person looks.').",
        should_not_happen="Failing the REDUNDANCY_WARNING_THRESHOLD in the EvaluationService."
    )
]
