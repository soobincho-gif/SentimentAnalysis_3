from __future__ import annotations

from pathlib import Path

from packages.core.models.scene import OrderedImageSet

SUPPORTED_IMAGE_SUFFIXES = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}


class ImagePreprocessingService:
    """Validate ordered image inputs before scene analysis begins."""

    def prepare(self, image_paths: list[str]) -> OrderedImageSet:
        validated_paths = [self._validate_image_path(image_path) for image_path in image_paths]
        return OrderedImageSet(
            image_paths=validated_paths,
            original_filenames=[Path(path).name for path in validated_paths],
            total_images=len(validated_paths),
        )

    def _validate_image_path(self, image_path: str) -> str:
        normalized = image_path.strip()
        if not normalized:
            raise ValueError("Image paths cannot be empty.")

        path = Path(normalized)
        if not path.exists():
            raise FileNotFoundError(f"Uploaded image could not be found: {normalized}")
        if not path.is_file():
            raise ValueError(f"Uploaded image path is not a file: {normalized}")
        if path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            raise ValueError(
                f"Unsupported image file type '{path.suffix or '[none]'}' for {path.name}."
            )

        return str(path)
