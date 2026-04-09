from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageStat

from packages.core.models.scene import OrderedImageSet, SceneObservation
from packages.infra.provider_client import ProviderClient
from packages.prompts.scene_analysis_prompts import SCENE_ANALYSIS_SYSTEM_PROMPT

COMMON_FILENAME_TOKENS = {
    "img",
    "image",
    "images",
    "photo",
    "picture",
    "upload",
    "frame",
    "story",
    "visual",
    "copy",
    "scan",
}
SETTING_KEYWORDS = {
    "park",
    "street",
    "road",
    "beach",
    "sea",
    "ocean",
    "cafe",
    "room",
    "home",
    "house",
    "forest",
    "field",
    "kitchen",
    "office",
    "school",
    "store",
    "station",
    "bridge",
    "garden",
    "sky",
}
ACTION_KEYWORDS = {
    "walk",
    "walking",
    "run",
    "running",
    "sit",
    "sitting",
    "stand",
    "standing",
    "look",
    "looking",
    "wait",
    "waiting",
    "smile",
    "smiling",
    "hold",
    "holding",
    "play",
    "playing",
    "open",
    "opening",
    "rest",
    "resting",
}


class SceneAnalysisService:
    """Produce grounded per-image observations using real provider analysis."""

    def __init__(self, use_mock: bool = False) -> None:
        self.provider = ProviderClient(use_mock=use_mock)
        self.last_provider_status: dict[str, str | None] | None = None

    def analyze(self, ordered_images: OrderedImageSet) -> list[SceneObservation]:
        observations: list[SceneObservation] = []
        fallback_status: dict[str, str | None] | None = None
        for image_id, image_path in enumerate(ordered_images.image_paths, start=1):
            filename_hint = (
                ordered_images.original_filenames[image_id - 1]
                if ordered_images.original_filenames is not None
                and image_id - 1 < len(ordered_images.original_filenames)
                else None
            )
            observations.append(
                self._analyze_single_image(
                    image_id=image_id,
                    image_path=image_path,
                    filename_hint=filename_hint,
                )
            )
            if getattr(self.provider, "last_request_used_fallback", False):
                fallback_status = self._provider_status_payload(stage="scene_analysis")
        self._apply_local_continuity(observations)
        if fallback_status is not None:
            self.last_provider_status = fallback_status
        else:
            self.last_provider_status = self._provider_status_payload(stage="scene_analysis")
        return observations

    def _analyze_single_image(
        self,
        image_id: int,
        image_path: str,
        filename_hint: str | None = None,
    ) -> SceneObservation:
        if not self.provider.is_configured:
            return self._fallback_observation(
                image_id=image_id,
                image_path=image_path,
                filename_hint=filename_hint,
                provider_note=self.provider.describe_fallback(stage="scene analysis"),
            )

        prompt = f"{SCENE_ANALYSIS_SYSTEM_PROMPT}\nThis is image #{image_id} in the sequence."
        observation = self.provider.analyze_image(
            image_path=image_path,
            prompt=prompt,
            response_model=SceneObservation,
        )
        if getattr(self.provider, "last_request_used_fallback", False):
            return self._fallback_observation(
                image_id=image_id,
                image_path=image_path,
                filename_hint=filename_hint,
                provider_note=self.provider.describe_fallback(stage="scene analysis"),
            )
        observation.image_id = image_id
        return observation

    def _fallback_observation(
        self,
        *,
        image_id: int,
        image_path: str,
        filename_hint: str | None,
        provider_note: str | None = None,
    ) -> SceneObservation:
        tokens = self._filename_tokens(filename_hint or Path(image_path).stem)
        entities = self._derive_entities(tokens)
        setting = self._derive_setting(tokens)
        actions = self._derive_actions(tokens)
        objects = self._derive_objects(tokens, entities, actions, setting)
        visible_mood = self._derive_visible_mood(image_path)
        uncertainty_notes: list[str] = []
        if provider_note is not None:
            uncertainty_notes.append(provider_note)
        if entities == ["main subject"] or setting == "unresolved setting":
            uncertainty_notes.append(
                "Local visual fallback was used because no multimodal provider is configured."
            )
        return SceneObservation(
            image_id=image_id,
            entities=entities,
            setting=setting,
            objects=objects,
            actions=actions,
            visible_mood=visible_mood,
            uncertainty_notes=uncertainty_notes,
        )

    def _apply_local_continuity(self, observations: list[SceneObservation]) -> None:
        for index in range(1, len(observations)):
            previous = observations[index - 1]
            current = observations[index]
            if current.same_subject_as_previous is not None:
                continue
            if previous.entities and current.entities and previous.entities[0] == current.entities[0]:
                current.same_subject_as_previous = True
            elif previous.setting and current.setting and previous.setting != current.setting:
                current.same_subject_as_previous = False

    def _filename_tokens(self, value: str) -> list[str]:
        normalized = Path(value).stem.split("__", 1)[0].lower()
        tokens = [
            token
            for token in re.split(r"[^a-z0-9]+", normalized)
            if token and not token.isdigit() and token not in COMMON_FILENAME_TOKENS
        ]
        return tokens

    def _derive_entities(self, tokens: list[str]) -> list[str]:
        entity_tokens = [token for token in tokens if token not in SETTING_KEYWORDS and token not in ACTION_KEYWORDS]
        if not entity_tokens:
            return ["main subject"]
        return [" ".join(entity_tokens[:2])]

    def _derive_setting(self, tokens: list[str]) -> str:
        for token in tokens:
            if token in SETTING_KEYWORDS:
                return token
        return "unresolved setting"

    def _derive_actions(self, tokens: list[str]) -> list[str]:
        matches = [token for token in tokens if token in ACTION_KEYWORDS]
        if matches:
            return [matches[0]]
        return ["remaining visible"]

    def _derive_objects(
        self,
        tokens: list[str],
        entities: list[str],
        actions: list[str],
        setting: str,
    ) -> list[str]:
        blocked = set(entities[0].split()) | set(actions) | {setting}
        objects = [token for token in tokens if token not in blocked and token not in SETTING_KEYWORDS]
        return objects[:3]

    def _derive_visible_mood(self, image_path: str) -> str:
        try:
            with Image.open(image_path) as image:
                rgb = image.convert("RGB").resize((24, 24))
                mean = ImageStat.Stat(rgb).mean
        except OSError:
            return "neutral"

        brightness = sum(mean) / 3
        if brightness >= 190:
            return "bright"
        if brightness <= 85:
            return "dim"
        if mean[0] > mean[2] + 18:
            return "warm"
        if mean[2] > mean[0] + 18:
            return "cool"
        return "neutral"

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
