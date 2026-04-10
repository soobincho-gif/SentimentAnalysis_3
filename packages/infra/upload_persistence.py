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
        if source_path is not None:
            if not source_path.exists():
                continue

            suffix = source_path.suffix or ".png"
            prefix = _safe_temp_prefix(source_path.stem)
            with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
                with source_path.open("rb") as source_stream:
                    shutil.copyfileobj(source_stream, temp_file)
                saved_paths.append(temp_file.name)
            continue

        filename, payload_bytes = _coerce_uploaded_bytes(image)
        suffix = Path(filename).suffix or ".png"
        prefix = _safe_temp_prefix(Path(filename).stem)
        with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
            temp_file.write(payload_bytes)
            saved_paths.append(temp_file.name)

    return saved_paths


def cleanup_persisted_images(image_paths: Iterable[str]) -> None:
    for image_path in image_paths:
        Path(image_path).unlink(missing_ok=True)


def _coerce_uploaded_path(image: Any) -> Path | None:
    if isinstance(image, Path):
        return image
    if isinstance(image, str):
        return Path(image)
    if hasattr(image, "name"):
        candidate_path = Path(str(image.name))
        if candidate_path.exists():
            return candidate_path
    if isinstance(image, dict) and "name" in image:
        candidate_path = Path(str(image["name"]))
        if candidate_path.exists():
            return candidate_path
    return None


def _coerce_uploaded_bytes(image: Any) -> tuple[str, bytes]:
    if hasattr(image, "getbuffer") and hasattr(image, "name"):
        return str(image.name), bytes(image.getbuffer())
    if hasattr(image, "read") and hasattr(image, "name"):
        payload = image.read()
        if hasattr(image, "seek"):
            image.seek(0)
        if isinstance(payload, bytes):
            return str(image.name), payload
    if isinstance(image, dict) and "name" in image and "data" in image:
        data = image["data"]
        if isinstance(data, bytes):
            return str(image["name"]), data
    raise ValueError(f"Unsupported upload payload: {type(image)!r}")


def _safe_temp_prefix(stem: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_").lower()
    if not normalized:
        normalized = "upload"
    return f"{normalized[:32]}__"
