from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
import re
from typing import Any, Iterable


def persist_uploaded_images(images: list[Any]) -> list[str]:
    """Copy uploaded image payloads into stable temp files for pipeline use."""

    saved_paths: list[str] = []
    for image in images:
        source_path = _coerce_uploaded_path(image)
        if not source_path.exists():
            continue

        suffix = source_path.suffix or ".png"
        prefix = _safe_temp_prefix(source_path.stem)
        with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
            with source_path.open("rb") as source_stream:
                shutil.copyfileobj(source_stream, temp_file)
            saved_paths.append(temp_file.name)

    return saved_paths


def cleanup_persisted_images(image_paths: Iterable[str]) -> None:
    for image_path in image_paths:
        Path(image_path).unlink(missing_ok=True)


def _coerce_uploaded_path(image: Any) -> Path:
    if isinstance(image, Path):
        return image
    if isinstance(image, str):
        return Path(image)
    if hasattr(image, "name"):
        return Path(str(image.name))
    if isinstance(image, dict) and "name" in image:
        return Path(str(image["name"]))
    raise ValueError(f"Unsupported upload payload: {type(image)!r}")


def _safe_temp_prefix(stem: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_").lower()
    if not normalized:
        normalized = "upload"
    return f"{normalized[:32]}__"
