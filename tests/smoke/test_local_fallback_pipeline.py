from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
import pytest

from packages.core.models.story import StoryRequest
from packages.infra.bootstrap import build_pipeline


def test_storytelling_pipeline_without_api_key_uses_local_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    log_dir = tmp_path / "runtime_logs"
    monkeypatch.setenv("VISUAL_STORY_LOG_DIR", str(log_dir))
    image_paths = [
        tmp_path / "park_dog_walk.png",
        tmp_path / "park_dog_rest.png",
    ]

    for image_path, color in zip(image_paths, [(220, 210, 180), (130, 120, 110)], strict=True):
        image = Image.new("RGB", (256, 192), color=color)
        image.save(image_path)

    pipeline = build_pipeline(use_mock=False)
    result = pipeline.run(
        StoryRequest(
            image_paths=[str(path) for path in image_paths],
            sentiment="heartwarming",
            max_sentences=5,
            include_debug=True,
        )
    )

    assert "mock story" not in result.story_text.lower()
    assert "park" in result.story_text.lower()
    assert "dog" in result.story_text.lower()
    assert result.sentence_alignment
    assert result.grounding_notes
    assert result.evaluation_report is not None
    assert "Local deterministic evaluation" in result.evaluation_report.summary
    assert result.evaluation_report.sentiment_audit is not None

    log_files = list(log_dir.glob("*_sentiment_runs.jsonl"))
    assert len(log_files) == 1
    log_lines = log_files[0].read_text(encoding="utf-8").strip().splitlines()
    assert log_lines
    payload = json.loads(log_lines[-1])
    assert payload["request"]["sentiment"] == "heartwarming"
    assert payload["evaluation"]["sentiment_audit"]["target_sentiment"] == "heartwarming"
    assert payload["story"]["title"] == result.title
