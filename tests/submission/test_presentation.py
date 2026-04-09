from __future__ import annotations

from pathlib import Path

from PIL import Image

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment_audit import SentimentAudit
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import PROVIDER_EXECUTION_MODE_LOCAL_FALLBACK, ProviderStageStatus, STRICT_GROUNDING_GENERATION_MODE, StoryResult
from submission.session_state import RunSnapshot
from submission.presentation import (
    present_action_guidance,
    present_correction_status,
    present_error,
    present_initial_outputs,
    present_processing_status,
    present_sequence_preview,
    present_story_result,
    render_observation_editor_card,
)


def _make_image(path: Path, color: tuple[int, int, int]) -> str:
    image = Image.new("RGB", (180, 120), color=color)
    image.save(path)
    return str(path)


def _make_result(
    *,
    grounding_score: float,
    coherence_score: float,
    flags: list[str],
    revision_attempts: int = 0,
    is_fallback: bool = False,
    unresolved_ambiguities: list[str] | None = None,
    story_text: str = "First sentence. Second sentence.",
    sentence_alignment: list[list[int]] | None = None,
    applied_overrides: list[SceneObservationOverride] | None = None,
    generation_mode: str = "default",
    grounding_notes: list[str] | None = None,
    evaluation_summary: str = "Summary text",
    provider_status: list[ProviderStageStatus] | None = None,
    sentiment_audit: SentimentAudit | None = None,
) -> StoryResult:
    return StoryResult(
        title="Storyboard Draft",
        story_text=story_text,
        original_scene_observations=[
            SceneObservation(image_id=1, entities=["dog"], setting="park", actions=["standing"]),
            SceneObservation(image_id=2, entities=["dog"], setting="path", actions=["waiting"]),
        ],
        scene_observations=[
            SceneObservation(image_id=1, entities=["dog"], setting="park", actions=["standing"]),
            SceneObservation(image_id=2, entities=["dog"], setting="path", actions=["waiting"]),
        ],
        sequence_memory=SequenceMemory(
            recurring_entities=["dog"],
            setting_progression=["park", "path"],
            unresolved_ambiguities=unresolved_ambiguities or [],
        ),
        evaluation_report=EvaluationReport(
            grounding_score=grounding_score,
            coherence_score=coherence_score,
            redundancy_score=0.90,
            sentiment_fit_score=0.88,
            readability_score=0.86,
            flags=flags,
            summary=evaluation_summary,
            sentiment_audit=sentiment_audit,
        ),
        sentence_alignment=sentence_alignment or [[1], [2]],
        grounding_notes=grounding_notes or ["dog remains visible"],
        provider_status=provider_status or [],
        applied_overrides=applied_overrides or [],
        generation_mode=generation_mode,
        revision_attempts=revision_attempts,
        is_fallback=is_fallback,
    )


def test_present_story_result_marks_fallback_as_low_confidence(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.62,
        coherence_score=0.81,
        flags=["grounding_below_threshold"],
        is_fallback=True,
    )

    outputs = present_story_result(result, sentiment="happy", image_paths=image_paths)

    assert "We’re not confident enough to present this as a final story yet" in outputs.status_html
    assert "Draft preview" in outputs.story_html
    assert "Revision limit reached" in outputs.diagnostics_html


def test_present_story_result_marks_revised_result_as_caution(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.91,
        coherence_score=0.89,
        flags=[],
        revision_attempts=1,
    )

    outputs = present_story_result(result, sentiment="heartwarming", image_paths=image_paths)

    assert "Draft story — some details are uncertain" in outputs.status_html
    assert "Revision performed" in outputs.diagnostics_html


def test_present_story_result_marks_clean_result_as_good(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.91,
        coherence_score=0.89,
        flags=[],
    )

    outputs = present_story_result(result, sentiment="playful", image_paths=image_paths)

    assert "Story ready" in outputs.status_html
    assert "Generated from 2 images · playful · Story ready" in outputs.story_html
    assert "status-icon-wrap" in outputs.status_html


def test_present_processing_status_renders_timer_and_spinner() -> None:
    status_html = present_processing_status(3)

    assert "Generating story..." in status_html
    assert "Processing... 3s" in status_html
    assert "status-spinner" in status_html


def test_present_action_guidance_lists_disabled_reasons() -> None:
    guidance_html = present_action_guidance(
        has_images=False,
        has_previous_run=False,
        has_corrections=False,
        sentence_error=None,
    )

    assert "Upload at least one image to enable Generate Story." in guidance_html
    assert "Generate a story first to unlock Regenerate and stricter grounding." in guidance_html
    assert "Save at least one correction in Analysis first" in guidance_html


def test_present_error_banner_does_not_double_escape_quotes() -> None:
    outputs = present_error(RuntimeError("Couldn't generate a story yet."))

    assert "&amp;#x27;" not in outputs.status_html
    assert "Couldn&#x27;t generate a story yet." in outputs.status_html


def test_present_story_result_marks_provider_fallback_as_caution(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.91,
        coherence_score=0.89,
        flags=[],
        grounding_notes=[
            "Local fallback was used for story generation because OPENAI_API_KEY is not configured.",
            "dog remains visible",
        ],
        evaluation_summary=(
            "Local deterministic evaluation was used because OPENAI_API_KEY is not configured. "
            "The draft was scored conservatively against the available observations."
        ),
        provider_status=[
            ProviderStageStatus(
                stage="story_generation",
                execution_mode=PROVIDER_EXECUTION_MODE_LOCAL_FALLBACK,
                reason="Local fallback was used for story generation because OPENAI_API_KEY is not configured.",
                recovery_hint="Set OPENAI_API_KEY in the environment or .env file.",
            ),
            ProviderStageStatus(
                stage="evaluation",
                execution_mode=PROVIDER_EXECUTION_MODE_LOCAL_FALLBACK,
                reason="Local fallback was used for evaluation because OPENAI_API_KEY is not configured.",
                recovery_hint="Set OPENAI_API_KEY in the environment or .env file.",
            ),
        ],
    )

    outputs = present_story_result(result, sentiment="playful", image_paths=image_paths)

    assert "Draft story — some details are uncertain" in outputs.status_html
    assert "Local fallback active" in outputs.diagnostics_html
    assert "Provider status" in outputs.diagnostics_html
    assert "OPENAI_API_KEY is not configured" in outputs.diagnostics_html


def test_story_map_only_uses_shared_prefix_for_alignment(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.91,
        coherence_score=0.89,
        flags=[],
        story_text="First sentence. Second sentence. Third sentence.",
        sentence_alignment=[[1], [2]],
    )

    outputs = present_story_result(result, sentiment="playful", image_paths=image_paths)

    assert "Sentence 1 · Images 1" in outputs.story_html
    assert "Sentence 2 · Images 2" in outputs.story_html
    assert "Sentence 3 · No mapped image" in outputs.story_html


def test_present_story_result_shows_manual_corrections_and_strict_mode(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.84,
        coherence_score=0.89,
        flags=[],
        applied_overrides=[
            SceneObservationOverride(image_id=1, main_entity="dog in red collar"),
        ],
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
    )

    outputs = present_story_result(result, sentiment="playful", image_paths=image_paths)

    assert "Strict grounding enabled" in outputs.story_html
    assert "Generated from corrected analysis" in outputs.story_html
    assert "1 manual correction applied" in outputs.story_html
    assert "Strict grounding mode" in outputs.diagnostics_html
    assert "Applied corrections" in outputs.diagnostics_html


def test_present_story_result_renders_sentiment_audit_details(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.9,
        coherence_score=0.88,
        flags=[],
        sentiment_audit=SentimentAudit(
            target_sentiment="heartwarming",
            matched_keywords=["tender", "comforting"],
            missing_keywords=["sincere"],
            matched_style_cues=["tender wording", "comforting close"],
            missing_style_cues=["connected framing"],
            score=0.79,
            summary="The draft expresses heartwarming clearly through tender, comforting, tender wording.",
        ),
    )

    outputs = present_story_result(result, sentiment="heartwarming", image_paths=image_paths)

    assert "Sentiment audit" in outputs.diagnostics_html
    assert "Audit score: 0.79" in outputs.diagnostics_html
    assert "Sentiment cues clear" in outputs.diagnostics_html
    assert "Matched keywords: tender, comforting" in outputs.diagnostics_html


def test_present_correction_status_reflects_active_corrections() -> None:
    html = present_correction_status(
        [SceneObservationOverride(image_id=2, main_entity="woman", same_subject_as_previous=True)],
        generated_with_corrections=True,
    )

    assert "1 correction saved" in html
    assert "Latest story used corrected analysis" in html


def test_comparison_view_marks_changed_and_unchanged_fields() -> None:
    html = render_observation_editor_card(
        SceneObservation(
            image_id=1,
            entities=["figure"],
            setting="street",
            actions=["standing"],
            same_subject_as_previous=None,
        ),
        SceneObservation(
            image_id=1,
            entities=["woman"],
            setting="street",
            actions=["opening the door"],
            same_subject_as_previous=True,
        ),
        image_path=None,
        active_override=SceneObservationOverride(
            image_id=1,
            main_entity="woman",
            visible_action="opening the door",
            same_subject_as_previous=True,
            generation_note="Keep the same subject grounded.",
        ),
    )

    assert "Original vs corrected" in html
    assert "Changed" in html
    assert "Unchanged" in html
    assert "User note" in html


def test_run_comparison_renders_score_delta_and_trust_improved(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]
    result = _make_result(
        grounding_score=0.90,
        coherence_score=0.88,
        flags=[],
    )
    previous_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=2,
        sentiment="playful",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=True,
        flag_count=2,
        grounding_score=0.74,
        coherence_score=0.80,
        redundancy_score=0.88,
        sentiment_fit_score=0.84,
        readability_score=0.82,
    )
    current_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=2,
        sentiment="playful",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.90,
        coherence_score=0.88,
        redundancy_score=0.90,
        sentiment_fit_score=0.88,
        readability_score=0.86,
    )

    outputs = present_story_result(
        result,
        sentiment="playful",
        image_paths=image_paths,
        previous_run_snapshot=previous_snapshot,
        current_run_snapshot=current_snapshot,
    )

    assert "Direct comparison" in outputs.story_html
    assert "Trust improved" in outputs.story_html
    assert "+0.16" in outputs.diagnostics_html


def test_run_comparison_renders_limited_label_for_changed_inputs(tmp_path: Path) -> None:
    image_paths = [_make_image(tmp_path / "one.png", (220, 180, 150))]
    result = _make_result(
        grounding_score=0.82,
        coherence_score=0.84,
        flags=[],
    )
    previous_snapshot = RunSnapshot(
        image_signature=["/tmp/other.png"],
        image_count=1,
        sentiment="sad",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.80,
        coherence_score=0.83,
        redundancy_score=0.88,
        sentiment_fit_score=0.85,
        readability_score=0.81,
    )
    current_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="playful",
        correction_count=1,
        generation_mode="strict_grounding",
        strict_grounding=True,
        fallback_used=False,
        flag_count=1,
        grounding_score=0.82,
        coherence_score=0.84,
        redundancy_score=0.88,
        sentiment_fit_score=0.87,
        readability_score=0.82,
    )

    outputs = present_story_result(
        result,
        sentiment="playful",
        image_paths=image_paths,
        previous_run_snapshot=previous_snapshot,
        current_run_snapshot=current_snapshot,
    )

    assert "Limited comparison" in outputs.story_html
    assert outputs.story_html.count("Limited comparison") == 1
    assert "run-highlight-label" not in outputs.story_html
    assert "Different images" in outputs.diagnostics_html
    assert "Different sentiment" in outputs.diagnostics_html


def test_run_comparison_renders_fallback_and_warning_count_changes(tmp_path: Path) -> None:
    image_paths = [_make_image(tmp_path / "one.png", (220, 180, 150))]
    result = _make_result(
        grounding_score=0.86,
        coherence_score=0.85,
        flags=["grounding_warning"],
        is_fallback=False,
    )
    previous_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=True,
        flag_count=3,
        grounding_score=0.70,
        coherence_score=0.72,
        redundancy_score=0.80,
        sentiment_fit_score=0.75,
        readability_score=0.77,
    )
    current_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=1,
        grounding_score=0.86,
        coherence_score=0.85,
        redundancy_score=0.89,
        sentiment_fit_score=0.88,
        readability_score=0.85,
    )

    outputs = present_story_result(
        result,
        sentiment="happy",
        image_paths=image_paths,
        previous_run_snapshot=previous_snapshot,
        current_run_snapshot=current_snapshot,
    )

    assert "Revision limit reached" in outputs.diagnostics_html
    assert "Improved" in outputs.diagnostics_html
    assert "-2" in outputs.diagnostics_html


def test_run_comparison_handles_no_previous_run_state(tmp_path: Path) -> None:
    image_paths = [_make_image(tmp_path / "one.png", (220, 180, 150))]
    result = _make_result(
        grounding_score=0.86,
        coherence_score=0.85,
        flags=[],
    )
    current_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.86,
        coherence_score=0.85,
        redundancy_score=0.89,
        sentiment_fit_score=0.88,
        readability_score=0.85,
    )

    outputs = present_story_result(
        result,
        sentiment="happy",
        image_paths=image_paths,
        previous_run_snapshot=None,
        current_run_snapshot=current_snapshot,
    )

    assert "No previous run in this session yet" in outputs.story_html
    assert "No previous run in this session yet" in outputs.diagnostics_html
    assert "story-mascot comparison" in outputs.story_html


def test_run_comparison_generates_no_meaningful_change_verdict(tmp_path: Path) -> None:
    image_paths = [_make_image(tmp_path / "one.png", (220, 180, 150))]
    result = _make_result(
        grounding_score=0.86,
        coherence_score=0.85,
        flags=[],
    )
    previous_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.85,
        coherence_score=0.85,
        redundancy_score=0.89,
        sentiment_fit_score=0.88,
        readability_score=0.85,
    )
    current_snapshot = RunSnapshot(
        image_signature=image_paths,
        image_count=1,
        sentiment="happy",
        correction_count=0,
        generation_mode="default",
        strict_grounding=False,
        fallback_used=False,
        flag_count=0,
        grounding_score=0.86,
        coherence_score=0.85,
        redundancy_score=0.89,
        sentiment_fit_score=0.88,
        readability_score=0.85,
    )

    outputs = present_story_result(
        result,
        sentiment="happy",
        image_paths=image_paths,
        previous_run_snapshot=previous_snapshot,
        current_run_snapshot=current_snapshot,
    )

    assert "No meaningful change" in outputs.story_html


def test_initial_outputs_include_story_empty_state_mascot() -> None:
    outputs = present_initial_outputs()

    assert "story-mascot story" in outputs.story_html
    assert "Story workspace" in outputs.story_html


def test_sequence_preview_uses_compact_thumb_strip(tmp_path: Path) -> None:
    image_paths = [
        _make_image(tmp_path / "one.png", (220, 180, 150)),
        _make_image(tmp_path / "two.png", (160, 120, 90)),
    ]

    html = present_sequence_preview(image_paths)

    assert "thumb-strip" in html
