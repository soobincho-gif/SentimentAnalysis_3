from __future__ import annotations

from itertools import chain

from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment import SentimentProfile

STORY_GENERATION_SYSTEM_PROMPT = """
You are a grounded visual storyteller. Generate a short story based on the provided explicit narrative plan, sequence memory, and image observations.
Adhere strictly to the requested tone, max sentences, and constraints. Do not fabricate major unsupported events.
Output must correspond precisely to the StoryDraft JSON schema.
""".strip()

SENTIMENT_GENERATION_GUIDANCE: dict[str, str] = {
    "sad": (
        "For sad stories, keep the tone quiet, reflective, and grounded in visible pauses, fading light, distance, or the sense of time passing. "
        "Use soft, restrained, bittersweet language rather than dramatic tragedy. "
        "Do not invent loss, death, abandonment, conflict, or harm unless the images explicitly support it."
    ),
    "suspenseful": (
        "For suspenseful stories, build tension from pauses, timing, watchfulness, and uncertainty already visible in the images. "
        "Make the tension explicit with grounded cues such as tense, alert, uneasy, hesitant, or unresolved wording, especially near the ending. "
        "Do not invent hidden danger, pursuit, villainy, supernatural threat, unseen agents, or the feeling that something off-screen is watching or following unless the images explicitly support it. "
        "If the scene itself is gentle, keep the suspense mild and human-scale through waiting, hesitation, fading light, silence, or an unresolved next step. "
        "Prefer restrained alertness and unresolved anticipation over dramatic menace, and keep the pacing tight rather than cozy."
    ),
    "mysterious": (
        "For mysterious stories, keep the tone curious, quiet, and slightly strange through partial understanding, subtle ambiguity, or details that remain open-ended. "
        "Prefer hints, questions, and quiet wonder over explicit revelation. "
        "Do not invent hidden identities, supernatural causes, conspiracies, or major secrets unless the images explicitly support them."
    ),
    "playful": (
        "For playful stories, keep the energy light, lively, and concrete through visible motion, quick rhythm, laughter, teasing movement, and cheerful interaction. "
        "Use buoyant wording such as lively, bright, delighted, or energetic where it fits the scene. "
        "Do not let the story drift into generic sentimentality or a calm summary if the images still support motion and fun."
    ),
}

SENTENCE_PREFIXES: dict[str, dict[str, str]] = {
    "happy": {
        "opening": "A warm rhythm begins as",
        "middle": "Soon,",
        "closing": "By the end,",
    },
    "sad": {
        "opening": "A quiet hush settles in as",
        "middle": "A little later,",
        "closing": "By the end,",
    },
    "suspenseful": {
        "opening": "Tension gathers as",
        "middle": "Moments later,",
        "closing": "At last,",
    },
    "mysterious": {
        "opening": "A small question hangs over the scene as",
        "middle": "Soon after,",
        "closing": "In the final moment,",
    },
    "heartwarming": {
        "opening": "A gentle warmth grows as",
        "middle": "Before long,",
        "closing": "By the end,",
    },
    "playful": {
        "opening": "A lively spark appears as",
        "middle": "In the next beat,",
        "closing": "By the finish,",
    },
    "grounded": {
        "opening": "The sequence opens as",
        "middle": "Then,",
        "closing": "Finally,",
    },
}

FALLBACK_SCENE_ENDINGS = {
    "happy": "giving the frame a warm, cheerful lift",
    "sad": "leaving the frame quiet, soft, and subdued",
    "suspenseful": "keeping the frame tense, sharp, and alert",
    "mysterious": "leaving the frame curious, quiet, and slightly uncertain",
    "heartwarming": "giving the frame a tender, comforting warmth",
    "playful": "giving the frame a lively, light, energetic bounce",
    "grounded": "keeping the frame measured and concrete",
}

FALLBACK_TRANSITION_ENDINGS = {
    "happy": "the next visible moment keeps that bright, gentle feeling moving forward",
    "sad": "the next visible moment stays soft and restrained",
    "suspenseful": "the next visible moment lands with a sharper, more uncertain edge",
    "mysterious": "the next visible moment keeps part of its meaning just out of reach",
    "heartwarming": "the next visible moment feels sincerely and gently connected",
    "playful": "the next visible moment keeps a quick, lively rhythm",
    "grounded": "the next visible moment stays closely tied to what the images show",
}

FALLBACK_CLOSING_ENDINGS = {
    "happy": "ending on an affirming, bright note",
    "sad": "ending on a quiet, reflective note",
    "suspenseful": "ending on a tense, unresolved note",
    "mysterious": "ending on a curious, open note",
    "heartwarming": "ending on a tender, satisfying note",
    "playful": "ending on a light, smiling note",
    "grounded": "ending on a measured, grounded note",
}

TITLE_ADJECTIVES = {
    "happy": "Bright",
    "sad": "Quiet",
    "suspenseful": "Tense",
    "mysterious": "Hidden",
    "heartwarming": "Gentle",
    "playful": "Playful",
    "hopeful": "Hopeful",
    "wistful": "Soft",
    "grounded": "Grounded",
}


def humanize_list(values: list[str]) -> str:
    unique_values = list(dict.fromkeys(value for value in values if value))
    if not unique_values:
        return ""
    if len(unique_values) == 1:
        return unique_values[0]
    if len(unique_values) == 2:
        return f"{unique_values[0]} and {unique_values[1]}"
    return f"{', '.join(unique_values[:-1])}, and {unique_values[-1]}"


def sentence_prefix(profile: SentimentProfile, index: int, total: int) -> str:
    variants = SENTENCE_PREFIXES.get(profile.label, SENTENCE_PREFIXES["grounded"])
    if index == 0:
        return variants["opening"]
    if index == total - 1:
        return variants["closing"]
    return variants["middle"]


def sentence_prefix_for_role(profile: SentimentProfile, role: str) -> str:
    variants = SENTENCE_PREFIXES.get(profile.label, SENTENCE_PREFIXES["grounded"])
    if role == "opening":
        return variants["opening"]
    if role == "closing":
        return variants["closing"]
    return variants["middle"]


def build_observation_phrase(observations: list[SceneObservation]) -> str:
    entities = humanize_list(
        list(chain.from_iterable(observation.entities for observation in observations))
    )
    actions = humanize_list(
        list(chain.from_iterable(observation.actions for observation in observations))
    )
    objects = humanize_list(
        list(chain.from_iterable(observation.objects for observation in observations))
    )
    settings = [observation.setting for observation in observations if observation.setting]
    setting = humanize_list(settings)

    if entities and actions and setting:
        phrase = f"{entities} move through {actions} in the {setting}"
    elif entities and actions:
        phrase = f"{entities} hold focus while {actions}"
    elif setting and objects:
        phrase = f"the {setting} comes into focus around {objects}"
    elif setting:
        phrase = f"the {setting} holds the moment together"
    elif objects:
        phrase = f"{objects} anchor the scene"
    else:
        phrase = "the uploaded images hold a grounded moment"

    if objects and objects not in phrase:
        phrase = f"{phrase}, with {objects} close at hand"

    return phrase


def build_title_candidates(
    observations: list[SceneObservation],
    sentiment_label: str | None = None,
) -> list[str]:
    entities = list(
        dict.fromkeys(
            value for observation in observations for value in observation.entities if value
        )
    )
    settings = list(
        dict.fromkeys(
            value
            for observation in observations
            if observation.setting
            for value in [observation.setting]
        )
    )
    adjective = TITLE_ADJECTIVES.get(sentiment_label or "grounded", "Grounded")

    candidates: list[str] = []
    if settings:
        candidates.append(f"{adjective} Scenes from the {settings[0].title()}")
    if entities:
        candidates.append(f"{adjective} Moments with {entities[0].title()}")
    candidates.append(f"{adjective} Scenes In Order")
    return candidates


def build_grounding_note(observation: SceneObservation) -> str:
    evidence_parts: list[str] = []
    if observation.setting:
        evidence_parts.append(f"setting={observation.setting}")
    if observation.actions:
        evidence_parts.append(f"actions={humanize_list(observation.actions)}")
    if observation.objects:
        evidence_parts.append(f"objects={humanize_list(observation.objects)}")
    if not evidence_parts:
        evidence_parts.append("metadata-only cues")
    return f"Image {observation.image_id} supported the story through {', '.join(evidence_parts)}."


def fallback_scene_ending(sentiment_label: str) -> str:
    return FALLBACK_SCENE_ENDINGS.get(sentiment_label, FALLBACK_SCENE_ENDINGS["grounded"])


def fallback_transition_ending(sentiment_label: str) -> str:
    return FALLBACK_TRANSITION_ENDINGS.get(
        sentiment_label,
        FALLBACK_TRANSITION_ENDINGS["grounded"],
    )


def fallback_closing_ending(sentiment_label: str) -> str:
    return FALLBACK_CLOSING_ENDINGS.get(sentiment_label, FALLBACK_CLOSING_ENDINGS["grounded"])


def sentiment_generation_guidance(profile: SentimentProfile) -> str:
    return SENTIMENT_GENERATION_GUIDANCE.get(profile.label, "")
