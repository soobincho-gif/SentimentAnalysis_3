from __future__ import annotations

from pathlib import Path

from PIL import Image

from packages.core.models.story import StoryRequest
from packages.infra.bootstrap import build_pipeline


def test_storytelling_pipeline_runs_end_to_end(tmp_path: Path) -> None:
    image_paths = [
        tmp_path / "park_dog_walk.png",
        tmp_path / "park_dog_rest.png",
    ]
    colors = [(220, 210, 180), (130, 120, 110)]

    for image_path, color in zip(image_paths, colors, strict=True):
        image = Image.new("RGB", (256, 192), color=color)
        image.save(image_path)

    pipeline = build_pipeline(use_mock=True)
    result = pipeline.run(
        StoryRequest(
            image_paths=[str(path) for path in image_paths],
            sentiment="heartwarming",
            max_sentences=4,
            include_debug=True,
        )
    )

    assert result.title
    assert result.story_text
    assert len(result.original_scene_observations) == 2
    assert len(result.scene_observations) == 2
    assert result.sequence_memory is not None
    assert result.evaluation_report is not None
    assert result.evaluation_report.grounding_score > 0
    assert result.sentence_alignment
    assert result.grounding_notes
