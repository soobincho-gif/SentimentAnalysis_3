from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SceneObservationOverride(BaseModel):
    """User-supplied corrections layered onto scene observations before sequencing."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    image_id: int = Field(ge=1)
    main_entity: str | None = None
    setting: str | None = None
    visible_action: str | None = None
    same_subject_as_previous: bool | None = None
    generation_note: str | None = Field(default=None, max_length=240)

    @field_validator("main_entity", "setting", "visible_action", "generation_note", mode="before")
    @classmethod
    def blank_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def has_changes(self) -> bool:
        return any(
            value is not None
            for value in [
                self.main_entity,
                self.setting,
                self.visible_action,
                self.same_subject_as_previous,
                self.generation_note,
            ]
        )
