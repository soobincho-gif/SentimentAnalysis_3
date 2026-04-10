from __future__ import annotations

from pathlib import Path

from packages.infra.upload_persistence import cleanup_persisted_images, persist_uploaded_images


class UploadedBuffer:
    def __init__(self, name: str, payload: bytes) -> None:
        self.name = name
        self._payload = payload

    def getbuffer(self) -> memoryview:
        return memoryview(self._payload)


def test_persist_uploaded_images_accepts_existing_paths(tmp_path: Path) -> None:
    source_path = tmp_path / "example.png"
    source_path.write_bytes(b"image-bytes")

    persisted_paths = persist_uploaded_images([str(source_path)])

    assert len(persisted_paths) == 1
    assert Path(persisted_paths[0]).read_bytes() == b"image-bytes"
    cleanup_persisted_images(persisted_paths)


def test_persist_uploaded_images_accepts_uploaded_file_buffers() -> None:
    uploaded = UploadedBuffer("story_frame.png", b"buffered-image")

    persisted_paths = persist_uploaded_images([uploaded])

    assert len(persisted_paths) == 1
    assert Path(persisted_paths[0]).suffix == ".png"
    assert Path(persisted_paths[0]).read_bytes() == b"buffered-image"
    cleanup_persisted_images(persisted_paths)
