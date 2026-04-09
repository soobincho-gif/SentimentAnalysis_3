from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
import logging
from time import monotonic, sleep

import gradio as gr

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation
from packages.core.models.story import (
    DEFAULT_GENERATION_MODE,
    STRICT_GROUNDING_GENERATION_MODE,
    StoryRequest,
)
from packages.infra.bootstrap import build_pipeline
from packages.infra.upload_persistence import (
    cleanup_persisted_images,
    persist_uploaded_images,
)
from packages.services.pipeline import StorytellingPipeline
from packages.services.observation_override_service import ObservationOverrideService
from submission.presentation import (
    SubmissionOutputs,
    present_action_guidance,
    present_correction_status,
    present_error,
    present_initial_outputs,
    present_processing_status,
    present_running_action_guidance,
    present_sequence_preview,
    present_story_result,
)
from submission.session_state import RunSnapshot

KEEP_CONTINUITY = "keep"
SAME_CONTINUITY = "same"
DIFFERENT_CONTINUITY = "different"

GENERATION_ACTION_DEFAULT = "generate"
GENERATION_ACTION_REGENERATE = "regenerate"
GENERATION_ACTION_STRICT = "strict"
GENERATION_ACTION_CORRECTED = "corrected"
GENERATION_ACTION_CORRECTED_STRICT = "corrected_strict"

GENERATION_BUTTON_LABELS = {
    GENERATION_ACTION_DEFAULT: "Generate Story",
    GENERATION_ACTION_REGENERATE: "Regenerate",
    GENERATION_ACTION_STRICT: "Regenerate with stricter grounding",
    GENERATION_ACTION_CORRECTED: "Generate from corrected analysis",
    GENERATION_ACTION_CORRECTED_STRICT: "Corrected analysis + stricter grounding",
}

GENERATION_BUTTON_BUSY_LABELS = {
    GENERATION_ACTION_DEFAULT: "Generating...",
    GENERATION_ACTION_REGENERATE: "Regenerating...",
    GENERATION_ACTION_STRICT: "Regenerating...",
    GENERATION_ACTION_CORRECTED: "Generating...",
    GENERATION_ACTION_CORRECTED_STRICT: "Generating...",
}

logger = logging.getLogger(__name__)


def normalize_images(images: list[str] | str | None) -> list[str]:
    if images is None:
        return []
    if isinstance(images, str):
        return [images]
    return [image for image in images if image]


def deserialize_overrides(payload: Sequence[dict] | None) -> list[SceneObservationOverride]:
    return [SceneObservationOverride.model_validate(item) for item in (payload or [])]


def deserialize_observations(payload: Sequence[dict] | None) -> list[SceneObservation]:
    return [SceneObservation.model_validate(item) for item in (payload or [])]


def serialize_overrides(overrides: Sequence[SceneObservationOverride]) -> list[dict]:
    return [override.model_dump(mode="json", exclude_none=True) for override in overrides]


def serialize_observations(observations: Sequence[SceneObservation]) -> list[dict]:
    return [observation.model_dump(mode="json", exclude_none=True) for observation in observations]


def deserialize_run_snapshot(payload: dict | None) -> RunSnapshot | None:
    if payload is None:
        return None
    return RunSnapshot.model_validate(payload)


def serialize_run_snapshot(snapshot: RunSnapshot | None) -> dict | None:
    if snapshot is None:
        return None
    return snapshot.model_dump(mode="json")


def initial_correction_status() -> str:
    return present_correction_status([])


def reset_workspace_for_images(
    images: list[str] | str | None,
) -> tuple[str, str, str, str, str, list[dict], list[dict], list[dict], str, list[str], dict | None]:
    initial_outputs = present_initial_outputs()
    normalized_images = normalize_images(images)
    return (
        present_sequence_preview(normalized_images),
        initial_outputs.status_html,
        initial_outputs.story_html,
        initial_outputs.analysis_html,
        initial_outputs.diagnostics_html,
        [],
        [],
        [],
        initial_correction_status(),
        normalized_images,
        None,
    )


def save_analysis_correction(
    original_observation_payload: Sequence[dict] | None,
    existing_override_payload: Sequence[dict] | None,
    image_id: int,
    main_entity: str,
    setting: str,
    visible_action: str,
    continuity_choice: str,
    generation_note: str,
) -> tuple[list[dict], list[dict], str]:
    overrides = {
        override.image_id: override for override in deserialize_overrides(existing_override_payload)
    }
    original_observations = deserialize_observations(original_observation_payload)
    same_subject_as_previous = _continuity_choice_to_value(continuity_choice)
    override = SceneObservationOverride(
        image_id=image_id,
        main_entity=main_entity,
        setting=setting,
        visible_action=visible_action,
        same_subject_as_previous=same_subject_as_previous,
        generation_note=generation_note,
    )

    if override.has_changes():
        overrides[image_id] = override
    else:
        overrides.pop(image_id, None)

    active_overrides = sorted(overrides.values(), key=lambda item: item.image_id)
    preview_observations = _preview_effective_observations(original_observations, active_overrides)
    return (
        serialize_overrides(active_overrides),
        serialize_observations(preview_observations),
        present_correction_status(active_overrides),
    )


def clear_analysis_correction(
    original_observation_payload: Sequence[dict] | None,
    existing_override_payload: Sequence[dict] | None,
    image_id: int,
) -> tuple[list[dict], list[dict], str]:
    overrides = {
        override.image_id: override for override in deserialize_overrides(existing_override_payload)
    }
    original_observations = deserialize_observations(original_observation_payload)
    overrides.pop(image_id, None)
    active_overrides = sorted(overrides.values(), key=lambda item: item.image_id)
    preview_observations = _preview_effective_observations(original_observations, active_overrides)
    return (
        serialize_overrides(active_overrides),
        serialize_observations(preview_observations),
        present_correction_status(active_overrides),
    )


def clear_all_corrections(
    original_observation_payload: Sequence[dict] | None,
) -> tuple[list[dict], list[dict], str]:
    original_observations = deserialize_observations(original_observation_payload)
    return (
        [],
        serialize_observations(original_observations),
        present_correction_status([]),
    )


def generate_default_story(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
) -> tuple[str, str, str, str, list[dict], list[dict], str, dict | None]:
    overrides = deserialize_overrides(override_payload)
    return _run_generation(
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        overrides=overrides,
        applied_override_source=[],
        generation_mode=DEFAULT_GENERATION_MODE,
        previous_run_snapshot=deserialize_run_snapshot(previous_run_payload),
    )


def stream_generate_default_story(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    yield from _stream_generation(
        action_key=GENERATION_ACTION_DEFAULT,
        handler=generate_default_story,
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        current_story_html=current_story_html,
        current_analysis_html=current_analysis_html,
        current_diagnostics_html=current_diagnostics_html,
        current_observation_payload=current_observation_payload,
        current_original_observation_payload=current_original_observation_payload,
        current_correction_status_html=current_correction_status_html,
    )


def generate_strict_story(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
) -> tuple[str, str, str, str, list[dict], list[dict], str, dict | None]:
    overrides = deserialize_overrides(override_payload)
    return _run_generation(
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        overrides=overrides,
        applied_override_source=[],
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
        previous_run_snapshot=deserialize_run_snapshot(previous_run_payload),
    )


def stream_generate_strict_story(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    yield from _stream_generation(
        action_key=GENERATION_ACTION_STRICT,
        handler=generate_strict_story,
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        current_story_html=current_story_html,
        current_analysis_html=current_analysis_html,
        current_diagnostics_html=current_diagnostics_html,
        current_observation_payload=current_observation_payload,
        current_original_observation_payload=current_original_observation_payload,
        current_correction_status_html=current_correction_status_html,
    )


def generate_from_corrected_analysis(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
) -> tuple[str, str, str, str, list[dict], list[dict], str, dict | None]:
    overrides = deserialize_overrides(override_payload)
    if not overrides:
        raise gr.Error("No saved corrections yet. Update the analysis cards first.")

    return _run_generation(
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        overrides=overrides,
        applied_override_source=overrides,
        generation_mode=DEFAULT_GENERATION_MODE,
        previous_run_snapshot=deserialize_run_snapshot(previous_run_payload),
    )


def stream_generate_from_corrected_analysis(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    yield from _stream_generation(
        action_key=GENERATION_ACTION_CORRECTED,
        handler=generate_from_corrected_analysis,
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        current_story_html=current_story_html,
        current_analysis_html=current_analysis_html,
        current_diagnostics_html=current_diagnostics_html,
        current_observation_payload=current_observation_payload,
        current_original_observation_payload=current_original_observation_payload,
        current_correction_status_html=current_correction_status_html,
    )


def generate_from_corrected_analysis_strict(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
) -> tuple[str, str, str, str, list[dict], list[dict], str, dict | None]:
    overrides = deserialize_overrides(override_payload)
    if not overrides:
        raise gr.Error("No saved corrections yet. Update the analysis cards first.")

    return _run_generation(
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        overrides=overrides,
        applied_override_source=overrides,
        generation_mode=STRICT_GROUNDING_GENERATION_MODE,
        previous_run_snapshot=deserialize_run_snapshot(previous_run_payload),
    )


def stream_generate_from_corrected_analysis_strict(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    yield from _stream_generation(
        action_key=GENERATION_ACTION_CORRECTED_STRICT,
        handler=generate_from_corrected_analysis_strict,
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        current_story_html=current_story_html,
        current_analysis_html=current_analysis_html,
        current_diagnostics_html=current_diagnostics_html,
        current_observation_payload=current_observation_payload,
        current_original_observation_payload=current_original_observation_payload,
        current_correction_status_html=current_correction_status_html,
    )


def stream_regenerate_story(
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    yield from _stream_generation(
        action_key=GENERATION_ACTION_REGENERATE,
        handler=generate_default_story,
        images=images,
        sentiment=sentiment,
        max_sentences=max_sentences,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        current_story_html=current_story_html,
        current_analysis_html=current_analysis_html,
        current_diagnostics_html=current_diagnostics_html,
        current_observation_payload=current_observation_payload,
        current_original_observation_payload=current_original_observation_payload,
        current_correction_status_html=current_correction_status_html,
    )


def continuity_choice_value(value: bool | None) -> str:
    if value is True:
        return SAME_CONTINUITY
    if value is False:
        return DIFFERENT_CONTINUITY
    return KEEP_CONTINUITY


def update_generation_controls(
    images: list[str] | str | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    max_sentences: int | float | None,
) -> tuple[dict, dict, dict, dict, dict, str]:
    return _build_generation_controls(
        images=images,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        max_sentences=max_sentences,
    )


def _stream_generation(
    *,
    action_key: str,
    handler: Callable[
        [list[str] | str | None, str, int | float | None, Sequence[dict] | None, dict | None],
        tuple[str, str, str, str, list[dict], list[dict], str, dict | None],
    ],
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    current_story_html: str,
    current_analysis_html: str,
    current_diagnostics_html: str,
    current_observation_payload: Sequence[dict] | None,
    current_original_observation_payload: Sequence[dict] | None,
    current_correction_status_html: str,
) -> Iterator[tuple]:
    preserved_observations = list(current_observation_payload or [])
    preserved_original_observations = list(current_original_observation_payload or [])
    button_updates = _generation_button_updates(active_action=action_key, in_progress=True)
    start_time = monotonic()
    immediate_error = _prevalidate_generation_request(
        action_key=action_key,
        images=images,
        override_payload=override_payload,
        previous_run_payload=previous_run_payload,
        max_sentences=max_sentences,
    )

    if immediate_error is not None:
        error_outputs = present_error(gr.Error(immediate_error))
        yield (
            error_outputs.status_html,
            error_outputs.story_html,
            error_outputs.analysis_html,
            error_outputs.diagnostics_html,
            preserved_observations,
            preserved_original_observations,
            current_correction_status_html,
            previous_run_payload,
            *_build_generation_controls(
                images=images,
                override_payload=override_payload,
                previous_run_payload=previous_run_payload,
                max_sentences=max_sentences,
            ),
        )
        return

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            handler,
            images,
            sentiment,
            max_sentences,
            override_payload,
            previous_run_payload,
        )

        yield (
            present_processing_status(0),
            current_story_html,
            current_analysis_html,
            current_diagnostics_html,
            preserved_observations,
            preserved_original_observations,
            current_correction_status_html,
            previous_run_payload,
            *button_updates,
            present_running_action_guidance(),
        )

        last_elapsed = 0
        while not future.done():
            elapsed_seconds = int(monotonic() - start_time)
            if elapsed_seconds > last_elapsed:
                last_elapsed = elapsed_seconds
                yield (
                    present_processing_status(elapsed_seconds),
                    current_story_html,
                    current_analysis_html,
                    current_diagnostics_html,
                    preserved_observations,
                    preserved_original_observations,
                    current_correction_status_html,
                    previous_run_payload,
                    *button_updates,
                    present_running_action_guidance(),
                )
            sleep(0.1)

        try:
            final_outputs = future.result()
        except Exception as exc:  # pragma: no cover - integration path
            logger.exception("submission.generate.stream_failure action=%s", action_key)
            error_outputs = present_error(exc)
            yield (
                error_outputs.status_html,
                error_outputs.story_html,
                error_outputs.analysis_html,
                error_outputs.diagnostics_html,
                preserved_observations,
                preserved_original_observations,
                current_correction_status_html,
                previous_run_payload,
                *_build_generation_controls(
                    images=images,
                    override_payload=override_payload,
                    previous_run_payload=previous_run_payload,
                    max_sentences=max_sentences,
                ),
            )
            return

    yield (
        *final_outputs,
        *_build_generation_controls(
            images=images,
            override_payload=override_payload,
            previous_run_payload=final_outputs[7],
            max_sentences=max_sentences,
        ),
    )


def _generation_button_updates(
    active_action: str | None = None,
    *,
    in_progress: bool = False,
) -> tuple[dict, dict, dict, dict, dict]:
    updates = []
    for action_key in (
        GENERATION_ACTION_DEFAULT,
        GENERATION_ACTION_REGENERATE,
        GENERATION_ACTION_STRICT,
        GENERATION_ACTION_CORRECTED,
        GENERATION_ACTION_CORRECTED_STRICT,
    ):
        label = (
            GENERATION_BUTTON_BUSY_LABELS[action_key]
            if in_progress and action_key == active_action
            else GENERATION_BUTTON_LABELS[action_key]
        )
        updates.append(gr.update(value=label, interactive=not in_progress))
    return tuple(updates)


def _build_generation_controls(
    *,
    images: list[str] | str | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    max_sentences: int | float | None,
) -> tuple[dict, dict, dict, dict, dict, str]:
    normalized_images = normalize_images(images)
    has_images = bool(normalized_images)
    has_previous_run = previous_run_payload is not None
    has_corrections = bool(deserialize_overrides(override_payload))
    sentence_error = _sentence_count_error(max_sentences)

    generate_enabled = has_images and sentence_error is None
    regenerate_enabled = has_previous_run and sentence_error is None
    strict_enabled = has_previous_run and sentence_error is None
    corrected_enabled = has_corrections and sentence_error is None
    corrected_strict_enabled = has_corrections and sentence_error is None

    helper_html = present_action_guidance(
        has_images=has_images,
        has_previous_run=has_previous_run,
        has_corrections=has_corrections,
        sentence_error=sentence_error,
    )

    return (
        gr.update(value=GENERATION_BUTTON_LABELS[GENERATION_ACTION_DEFAULT], interactive=generate_enabled),
        gr.update(value=GENERATION_BUTTON_LABELS[GENERATION_ACTION_REGENERATE], interactive=regenerate_enabled),
        gr.update(value=GENERATION_BUTTON_LABELS[GENERATION_ACTION_STRICT], interactive=strict_enabled),
        gr.update(value=GENERATION_BUTTON_LABELS[GENERATION_ACTION_CORRECTED], interactive=corrected_enabled),
        gr.update(value=GENERATION_BUTTON_LABELS[GENERATION_ACTION_CORRECTED_STRICT], interactive=corrected_strict_enabled),
        helper_html,
    )


def _prevalidate_generation_request(
    *,
    action_key: str,
    images: list[str] | str | None,
    override_payload: Sequence[dict] | None,
    previous_run_payload: dict | None,
    max_sentences: int | float | None,
) -> str | None:
    if not normalize_images(images):
        return "Upload at least one image before generating a story."

    sentence_error = _sentence_count_error(max_sentences)
    if sentence_error is not None:
        return sentence_error

    if action_key in {GENERATION_ACTION_REGENERATE, GENERATION_ACTION_STRICT} and previous_run_payload is None:
        return "Generate a story first."

    if action_key in {GENERATION_ACTION_CORRECTED, GENERATION_ACTION_CORRECTED_STRICT} and not deserialize_overrides(override_payload):
        return "Save at least one correction in Analysis first."

    return None


def _run_generation(
    *,
    images: list[str] | str | None,
    sentiment: str,
    max_sentences: int | float | None,
    overrides: Sequence[SceneObservationOverride],
    applied_override_source: Sequence[SceneObservationOverride],
    generation_mode: str,
    previous_run_snapshot: RunSnapshot | None,
) -> tuple[str, str, str, str, list[dict], list[dict], str, dict | None]:
    image_paths = normalize_images(images)
    saved_paths: list[str] = []
    logger.info(
        "submission.generate.start sentiment=%s mode=%s image_count=%s max_sentences=%s override_count=%s",
        sentiment,
        generation_mode,
        len(image_paths),
        max_sentences,
        len(applied_override_source),
    )
    try:
        if not image_paths:
            raise ValueError("Please upload at least one image.")
        normalized_max_sentences = _normalize_max_sentences(max_sentences)

        saved_paths = persist_uploaded_images(image_paths)
        if not saved_paths:
            raise ValueError("Uploaded image files could not be prepared for processing.")

        pipeline: StorytellingPipeline = build_pipeline()
        request = StoryRequest(
            image_paths=saved_paths,
            sentiment=sentiment,
            max_sentences=normalized_max_sentences,
            include_debug=True,
            analysis_overrides=list(applied_override_source),
            generation_mode=generation_mode,
        )
        result = pipeline.run(request)
        current_run_snapshot = _build_run_snapshot(
            result,
            image_paths=image_paths,
            sentiment=sentiment,
        )
        outputs = present_story_result(
            result,
            sentiment=sentiment,
            image_paths=image_paths,
            previous_run_snapshot=previous_run_snapshot,
            current_run_snapshot=current_run_snapshot,
        )
        correction_status = present_correction_status(
            overrides,
            generation_mode=generation_mode,
            generated_with_corrections=bool(result.applied_overrides),
        )
        logger.info(
            "submission.generate.success sentiment=%s mode=%s title=%s revisions=%s flags=%s",
            sentiment,
            generation_mode,
            result.title,
            result.revision_attempts,
            len(result.evaluation_report.flags) if result.evaluation_report is not None else 0,
        )
        return (
            outputs.status_html,
            outputs.story_html,
            outputs.analysis_html,
            outputs.diagnostics_html,
            serialize_observations(result.scene_observations),
            serialize_observations(result.original_scene_observations),
            correction_status,
            serialize_run_snapshot(current_run_snapshot),
        )
    except gr.Error as exc:
        logger.warning(
            "submission.generate.validation_error sentiment=%s mode=%s message=%s",
            sentiment,
            generation_mode,
            exc,
        )
        error_outputs = present_error(exc)
        correction_status = present_correction_status(
            overrides,
            generation_mode=generation_mode,
            generated_with_corrections=False,
        )
        return (
            error_outputs.status_html,
            error_outputs.story_html,
            error_outputs.analysis_html,
            error_outputs.diagnostics_html,
            [],
            [],
            correction_status,
            serialize_run_snapshot(previous_run_snapshot),
        )
    except Exception as exc:  # pragma: no cover - UI error path
        logger.exception(
            "submission.generate.failure sentiment=%s mode=%s",
            sentiment,
            generation_mode,
        )
        error_outputs: SubmissionOutputs = present_error(exc)
        correction_status = present_correction_status(
            overrides,
            generation_mode=generation_mode,
            generated_with_corrections=False,
        )
        return (
            error_outputs.status_html,
            error_outputs.story_html,
            error_outputs.analysis_html,
            error_outputs.diagnostics_html,
            [],
            [],
            correction_status,
            serialize_run_snapshot(previous_run_snapshot),
        )
    finally:
        cleanup_persisted_images(saved_paths)


def _continuity_choice_to_value(choice: str) -> bool | None:
    if choice == SAME_CONTINUITY:
        return True
    if choice == DIFFERENT_CONTINUITY:
        return False
    return None


def _preview_effective_observations(
    original_observations: Sequence[SceneObservation],
    overrides: Sequence[SceneObservationOverride],
) -> list[SceneObservation]:
    if not original_observations:
        return []
    service = ObservationOverrideService()
    effective_observations, _ = service.apply(list(original_observations), list(overrides))
    return effective_observations


def _build_run_snapshot(
    result,
    *,
    image_paths: Sequence[str],
    sentiment: str,
) -> RunSnapshot:
    report = result.evaluation_report
    return RunSnapshot(
        image_signature=list(image_paths),
        image_count=len(image_paths),
        sentiment=sentiment,
        correction_count=len(result.applied_overrides),
        generation_mode=result.generation_mode,
        strict_grounding=(result.generation_mode == STRICT_GROUNDING_GENERATION_MODE),
        fallback_used=result.is_fallback,
        flag_count=len(report.flags) if report is not None else 0,
        grounding_score=report.grounding_score if report is not None else 0.0,
        coherence_score=report.coherence_score if report is not None else 0.0,
        redundancy_score=report.redundancy_score if report is not None else 0.0,
        sentiment_fit_score=report.sentiment_fit_score if report is not None else 0.0,
        readability_score=report.readability_score if report is not None else 0.0,
    )


def _normalize_max_sentences(value: int | float | None) -> int:
    error = _sentence_count_error(value)
    if error is not None:
        raise gr.Error(error)
    return int(value)


def _sentence_count_error(value: int | float | None) -> str | None:
    if value is None:
        return "Please enter a sentence count of at least 1."
    if isinstance(value, bool) or not isinstance(value, int | float):
        return "Sentence count must be a whole number."
    if value != int(value):
        return "Sentence count must be a whole number."

    normalized = int(value)
    if normalized < 1:
        return "Sentence count must be at least 1."
    return None
