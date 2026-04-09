from __future__ import annotations

import gradio as gr
from pathlib import Path

from PIL import Image
import pytest

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import StoryResult
from submission.session_state import RunSnapshot
from submission.controller import (
    clear_analysis_correction,
    clear_all_corrections,
    generate_default_story,
    generate_from_corrected_analysis_strict,
    reset_workspace_for_images,
    save_analysis_correction,
    stream_generate_default_story,
    update_generation_controls,
)


def test_reset_workspace_for_images_reflects_image_order(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    Image.new("RGB", (64, 64), color=(180, 140, 100)).save(first)
    Image.new("RGB", (64, 64), color=(120, 90, 70)).save(second)

    preview_html, *_, uploaded_images, run_snapshot = reset_workspace_for_images([str(first), str(second)])

    assert "Image 1" in preview_html
    assert "Image 2" in preview_html
    assert "first.png" in preview_html
    assert "second.png" in preview_html
    assert uploaded_images == [str(first), str(second)]
    assert run_snapshot is None


def test_save_analysis_correction_updates_active_correction_status() -> None:
    payload, preview_payload, status_html = save_analysis_correction(
        [
            SceneObservation(
                image_id=1,
                entities=["figure"],
                setting="street",
                actions=["standing"],
            ).model_dump(mode="json", exclude_none=True)
        ],
        [],
        1,
        "woman with scarf",
        "cafe entrance",
        "opening the door",
        "same",
        "Keep the same person grounded across both images.",
    )

    overrides = [SceneObservationOverride.model_validate(item) for item in payload]
    preview = [SceneObservation.model_validate(item) for item in preview_payload]

    assert len(overrides) == 1
    assert overrides[0].main_entity == "woman with scarf"
    assert preview[0].entities[0] == "woman with scarf"
    assert "1 correction saved" in status_html
    assert "Image 1" in status_html


def test_clear_analysis_correction_removes_saved_override() -> None:
    payload, _, _ = save_analysis_correction(
        [
            SceneObservation(
                image_id=1,
                entities=["dog"],
                setting="park",
                actions=["walking"],
            ).model_dump(mode="json", exclude_none=True)
        ],
        [],
        1,
        "dog",
        "",
        "",
        "keep",
        "",
    )

    cleared_payload, preview_payload, status_html = clear_analysis_correction(
        [
            SceneObservation(
                image_id=1,
                entities=["dog"],
                setting="park",
                actions=["walking"],
            ).model_dump(mode="json", exclude_none=True)
        ],
        payload,
        1,
    )

    assert cleared_payload == []
    assert SceneObservation.model_validate(preview_payload[0]).entities[0] == "dog"
    assert "No saved corrections" in status_html


def test_clear_all_corrections_resets_preview_to_original() -> None:
    observations = [
        SceneObservation(
            image_id=1,
            entities=["dog"],
            setting="park",
            actions=["walking"],
        ).model_dump(mode="json", exclude_none=True)
    ]

    cleared_payload, preview_payload, status_html = clear_all_corrections(observations)

    assert cleared_payload == []
    assert SceneObservation.model_validate(preview_payload[0]).entities[0] == "dog"
    assert "No saved corrections" in status_html


def test_combined_action_passes_corrections_and_strict_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    Image.new("RGB", (64, 64), color=(180, 140, 100)).save(first)
    captured_request = None

    class DummyPipeline:
        def run(self, request):  # type: ignore[no-untyped-def]
            nonlocal captured_request
            captured_request = request
            return StoryResult(
                title="Corrected strict story",
                story_text="A careful grounded story.",
                original_scene_observations=[
                    SceneObservation(image_id=1, entities=["figure"], setting="street", actions=["standing"])
                ],
                scene_observations=[
                    SceneObservation(image_id=1, entities=["woman"], setting="cafe", actions=["opening the door"])
                ],
                sequence_memory=SequenceMemory(),
                evaluation_report=EvaluationReport(
                    grounding_score=0.90,
                    coherence_score=0.88,
                    redundancy_score=0.90,
                    sentiment_fit_score=0.86,
                    readability_score=0.87,
                    flags=[],
                    summary="Passed",
                ),
                applied_overrides=[
                    SceneObservationOverride(image_id=1, main_entity="woman", setting="cafe")
                ],
                generation_mode="strict_grounding",
                sentence_alignment=[[1]],
                grounding_notes=["user correction applied"],
            )

    monkeypatch.setattr("submission.controller.build_pipeline", lambda: DummyPipeline())

    outputs = generate_from_corrected_analysis_strict(
        [str(first)],
        "happy",
        3,
        [
            SceneObservationOverride(
                image_id=1,
                main_entity="woman",
                setting="cafe",
            ).model_dump(mode="json", exclude_none=True)
        ],
        None,
    )

    assert captured_request is not None
    assert captured_request.generation_mode == "strict_grounding"
    assert len(captured_request.analysis_overrides) == 1
    assert "Strict grounding enabled" in outputs[1]
    assert outputs[-1]["generation_mode"] == "strict_grounding"


def test_corrected_action_without_corrections_fails_safely(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    Image.new("RGB", (64, 64), color=(180, 140, 100)).save(first)

    with pytest.raises(gr.Error):
        generate_from_corrected_analysis_strict([str(first)], "happy", 3, [], None)


def test_generate_default_story_keeps_previous_snapshot_when_run_fails(tmp_path: Path) -> None:
    previous_snapshot = RunSnapshot(
        image_signature=[str(tmp_path / "previous.png")],
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.9,
        coherence_score=0.9,
        redundancy_score=0.9,
        sentiment_fit_score=0.9,
        readability_score=0.9,
    )

    outputs = generate_default_story([], "happy", 3, [], previous_snapshot.model_dump(mode="json"))

    assert outputs[-1] == previous_snapshot.model_dump(mode="json")


def test_generate_default_story_normalizes_large_sentence_count(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    Image.new("RGB", (64, 64), color=(180, 140, 100)).save(first)
    captured_request = None

    class DummyPipeline:
        def run(self, request):  # type: ignore[no-untyped-def]
            nonlocal captured_request
            captured_request = request
            return StoryResult(
                title="Longer story",
                story_text="A grounded longer story.",
                original_scene_observations=[
                    SceneObservation(image_id=1, entities=["figure"], setting="street", actions=["standing"])
                ],
                scene_observations=[
                    SceneObservation(image_id=1, entities=["figure"], setting="street", actions=["standing"])
                ],
                sequence_memory=SequenceMemory(),
                evaluation_report=EvaluationReport(
                    grounding_score=0.88,
                    coherence_score=0.87,
                    redundancy_score=0.88,
                    sentiment_fit_score=0.86,
                    readability_score=0.87,
                    flags=[],
                    summary="Passed",
                ),
                sentence_alignment=[[1]],
                grounding_notes=["grounded"],
            )

    monkeypatch.setattr("submission.controller.build_pipeline", lambda: DummyPipeline())

    generate_default_story([str(first)], "happy", 12.0, [], None)

    assert captured_request is not None
    assert captured_request.max_sentences == 12


def test_generate_default_story_rejects_non_positive_sentence_count(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    Image.new("RGB", (64, 64), color=(180, 140, 100)).save(first)

    outputs = generate_default_story([str(first)], "happy", 0, [], None)

    assert "We hit a problem before the story could be generated" in outputs[0]
    assert "Sentence count must be at least 1." in outputs[1]


def test_stream_generate_default_story_emits_processing_then_restores_buttons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_outputs = (
        "<section>done</section>",
        "<section>story</section>",
        "<section>analysis</section>",
        "<section>diagnostics</section>",
        [{"image_id": 1}],
        [{"image_id": 1}],
        "<section>corrections</section>",
        {"sentiment": "happy"},
    )

    def fake_generate(*args, **kwargs):  # type: ignore[no-untyped-def]
        return expected_outputs

    monkeypatch.setattr("submission.controller.generate_default_story", fake_generate)

    stream = stream_generate_default_story(
        ["image.png"],
        "happy",
        3,
        [],
        {"sentiment": "previous"},
        "<section>current story</section>",
        "<section>current analysis</section>",
        "<section>current diagnostics</section>",
        [{"image_id": 99}],
        [{"image_id": 99}],
        "<section>current corrections</section>",
    )

    first = next(stream)
    final = next(stream)

    assert "Generating story..." in first[0]
    assert "Processing... 0s" in first[0]
    assert first[1] == "<section>current story</section>"
    assert first[8]["interactive"] is False
    assert first[8]["value"] == "Generating..."
    assert first[9]["interactive"] is False
    assert "Generation in progress" in first[13]

    assert final[:8] == expected_outputs
    assert final[8]["interactive"] is True
    assert final[8]["value"] == "Generate Story"
    assert final[9]["value"] == "Regenerate"
    assert "Save at least one correction in Analysis first" in final[13]


def test_update_generation_controls_disables_follow_up_actions_without_run_or_corrections() -> None:
    controls = update_generation_controls(["image.png"], [], None, 5)

    assert controls[0]["interactive"] is True
    assert controls[1]["interactive"] is False
    assert controls[2]["interactive"] is False
    assert controls[3]["interactive"] is False
    assert controls[4]["interactive"] is False
    assert "Generate a story first" in controls[5]
    assert "Save at least one correction in Analysis first" in controls[5]
