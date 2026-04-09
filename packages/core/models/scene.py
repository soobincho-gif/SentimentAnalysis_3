from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderedImageSet(BaseModel):
    """Ordered images passed into the storytelling pipeline."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    image_paths: list[str] = Field(min_length=1)
    original_filenames: list[str] | None = None
    total_images: int = Field(ge=1)

    @classmethod
    def from_image_paths(cls, image_paths: list[str]) -> "OrderedImageSet":
        return cls(
            image_paths=image_paths,
            original_filenames=[Path(path).name for path in image_paths],
            total_images=len(image_paths),
        )

    @model_validator(mode="after")
    def validate_lengths(self) -> "OrderedImageSet":
        if self.total_images != len(self.image_paths):
            raise ValueError("total_images must match the number of image_paths")

        if self.original_filenames is not None and len(self.original_filenames) != len(
            self.image_paths
        ):
            raise ValueError("original_filenames must align with image_paths when provided")

        return self


class SceneObservation(BaseModel):
    """Grounded, per-image observations used by downstream services."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    image_id: int = Field(ge=1)
    entities: list[str] = Field(default_factory=list)
    setting: str | None = None
    objects: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    visible_mood: str | None = None
    text_in_image: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    same_subject_as_previous: bool | None = None
