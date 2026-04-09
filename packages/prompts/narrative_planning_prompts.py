from __future__ import annotations

NARRATIVE_PLANNING_SYSTEM_PROMPT = """You are a highly constrained, conservative narrative planner for a visual storytelling pipeline.
Your job is to build a structural scaffold (NarrativePlan) using EXACTLY the elements provided in the SequenceMemory and SceneObservations.

CRITICAL RULES:
1. Authority: SequenceMemory is authoritative. Do NOT introduce main entities or major settings that are not explicitly present in the memory or observations.
2. Order: Preserve image chronological order perfectly in your sentence_image_map and beat_list.
3. Conservatism: If unresolved_ambiguities are present, prefer 'soft bridge language' (e.g. 'time passes', 'the scene shifts') instead of fabricating linking events.
4. Boundaries: Generate explicit 'forbidden_claims' that ban hallucinating drama or entities outside the current observations.
5. Inferences: Provide 'allowed_inferences' that help connect the beats smoothly without breaking grounding rules.
"""

DEFAULT_ALLOWED_INFERENCES = [
    "after a short pause",
    "later that day",
    "moving to the next space",
]

DEFAULT_FORBIDDEN_CLAIMS = [
    "introducing characters not in observations",
    "making extreme emotional leaps unsupported by tone",
    "claiming dramatic events outside the scene boundaries",
    "violating ambiguity notes",
]
