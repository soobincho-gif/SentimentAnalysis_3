from __future__ import annotations

SCENE_ANALYSIS_SYSTEM_PROMPT = """
Analyze one uploaded image and return only grounded scene facts.
Separate observable facts from uncertainty notes.
Do not write final story prose and do not infer sequence-level meaning.
""".strip()

FALLBACK_ANALYSIS_NOTE = (
    "MVP fallback analysis uses filename cues and basic image metadata. Richer grounding "
    "can be added later through a provider-backed analyzer."
)
LIMITED_CUE_NOTE = "The image filename and metadata did not expose many grounded scene cues."
UNCLEAR_SETTING_NOTE = "The setting remained unclear in the metadata-only analysis pass."

FILENAME_STOPWORDS = {
    "image",
    "img",
    "photo",
    "picture",
    "scan",
    "snapshot",
    "upload",
    "final",
    "copy",
    "edited",
    "small",
    "large",
    "jpeg",
    "jpg",
    "png",
    "heic",
}

ENTITY_HINTS = {
    "boy": "boy",
    "girl": "girl",
    "child": "child",
    "children": "children",
    "person": "person",
    "people": "people",
    "family": "family",
    "mother": "mother",
    "father": "father",
    "woman": "woman",
    "man": "man",
    "friend": "friend",
    "dog": "dog",
    "cat": "cat",
    "bird": "bird",
    "couple": "couple",
}

OBJECT_HINTS = {
    "ball": "ball",
    "book": "book",
    "bike": "bicycle",
    "bicycle": "bicycle",
    "cake": "cake",
    "car": "car",
    "coffee": "coffee cup",
    "flower": "flowers",
    "gift": "gift",
    "hat": "hat",
    "lamp": "lamp",
    "leash": "leash",
    "phone": "phone",
    "sign": "sign",
    "table": "table",
    "tree": "tree",
    "umbrella": "umbrella",
    "window": "window",
}

ACTION_HINTS = {
    "arrive": "arriving",
    "carry": "carrying",
    "dance": "dancing",
    "eat": "eating",
    "fetch": "fetching",
    "look": "looking",
    "play": "playing",
    "pose": "posing",
    "rest": "resting",
    "ride": "riding",
    "run": "running",
    "sit": "sitting",
    "smile": "smiling",
    "stand": "standing",
    "talk": "talking",
    "walk": "walking",
    "watch": "watching",
}

SETTING_HINTS = {
    "beach": "beach",
    "cafe": "cafe",
    "city": "city street",
    "classroom": "classroom",
    "forest": "forest",
    "garden": "garden",
    "home": "home",
    "house": "home",
    "kitchen": "kitchen",
    "office": "office",
    "park": "park",
    "road": "roadside",
    "room": "room interior",
    "school": "school",
    "street": "street",
}
