from __future__ import annotations

import base64
import html
import io
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from packages.core.models.correction import SceneObservationOverride
from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment_audit import SentimentAudit
from packages.core.models.story import (
    STRICT_GROUNDING_GENERATION_MODE,
    StoryResult,
)
from submission.session_state import RunSnapshot

DEFAULT_MAX_REVISION_ATTEMPTS = 2
STRICT_MAX_REVISION_ATTEMPTS = 3


@dataclass(frozen=True)
class SubmissionOutputs:
    status_html: str
    story_html: str
    analysis_html: str
    diagnostics_html: str

    def as_tuple(self) -> tuple[str, str, str, str]:
        return (
            self.status_html,
            self.story_html,
            self.analysis_html,
            self.diagnostics_html,
        )


@dataclass(frozen=True)
class ConfidencePresentation:
    state: str
    banner_title: str
    meta_label: str
    reason: str


@dataclass(frozen=True)
class MetricDeltaPresentation:
    label: str
    previous_value: str
    current_value: str
    delta_value: str
    trend: str


@dataclass(frozen=True)
class RunComparisonPresentation:
    available: bool
    comparable: bool
    scope_label: str
    verdict: str
    summary: str
    metric_rows: list[MetricDeltaPresentation]
    same_images: bool
    same_sentiment: bool
    previous_snapshot: RunSnapshot | None
    current_snapshot: RunSnapshot


def present_initial_outputs() -> SubmissionOutputs:
    return SubmissionOutputs(
        status_html=_render_status_banner(
            "neutral",
            "Ready to analyze a sequence",
            "Upload images, confirm the order, and generate a grounded story when you are ready.",
        ),
        story_html=f"""
        <section class="story-card story-empty-card">
          <div class="story-meta">Awaiting image sequence</div>
          {_render_empty_state(
              title="Your story will appear here",
              description=(
                  "The main panel will show a confidence-first status, the generated story, "
                  "and a sentence-to-image story map."
              ),
              eyebrow="Story workspace",
              mascot_variant="story",
              compact=False,
          )}
        </section>
        """,
        analysis_html="""
        <section class="analysis-shell">
          <h3>Analysis</h3>
          <p class="placeholder-copy">
            Scene observations and sequence memory will appear here after generation.
          </p>
        </section>
        """,
        diagnostics_html="""
        <section class="diagnostics-shell">
          <h3>Diagnostics</h3>
          <p class="placeholder-copy">
            Evaluator scores, warnings, revision attempts, and generation mode details will appear here after generation.
          </p>
        </section>
        """,
    )


def present_sequence_preview(image_paths: Sequence[str] | None) -> str:
    if not image_paths:
        return f"""
        <section class="preview-shell">
          {_render_empty_state(
              title="Sequence preview",
              description="Add two or more images to preview the ordered storyboard frames here.",
              eyebrow="Storyboard order",
              mascot_variant="sequence",
              compact=True,
          )}
        </section>
        """

    cards = "".join(
        _render_thumbnail_card(
            image_path=path,
            label=f"Image {index}",
            caption=Path(path).name,
            badge=str(index),
            max_size=(280, 210),
        )
        for index, path in enumerate(image_paths, start=1)
    )
    return f"""
    <section class="preview-shell">
      <h2 class="section-title">Sequence preview</h2>
      <p class="section-copy">Check the order before generating. The story follows this sequence exactly.</p>
      <div class="thumb-strip">{cards}</div>
    </section>
    """


def present_story_result(
    result: StoryResult,
    *,
    sentiment: str,
    image_paths: Sequence[str],
    previous_run_snapshot: RunSnapshot | None = None,
    current_run_snapshot: RunSnapshot | None = None,
) -> SubmissionOutputs:
    confidence = _classify_confidence(result)
    comparison = _build_run_comparison(
        previous_run_snapshot=previous_run_snapshot,
        current_run_snapshot=current_run_snapshot,
    )
    return SubmissionOutputs(
        status_html=_render_status_banner(
            confidence.state,
            confidence.banner_title,
            confidence.reason,
        ),
        story_html=_render_story_tab(result, sentiment, image_paths, confidence, comparison),
        analysis_html=_render_analysis_tab(result),
        diagnostics_html=_render_diagnostics_tab(result, confidence, comparison),
    )


def present_processing_status(elapsed_seconds: int) -> str:
    return _render_status_banner(
        "processing",
        "Generating story...",
        f"Processing... {elapsed_seconds}s",
    )


def present_action_guidance(
    *,
    has_images: bool,
    has_previous_run: bool,
    has_corrections: bool,
    sentence_error: str | None,
) -> str:
    messages: list[str] = []
    if not has_images:
        messages.append("Upload at least one image to enable Generate Story.")
    if sentence_error is not None:
        messages.append(sentence_error)
    if not has_previous_run:
        messages.append("Generate a story first to unlock Regenerate and stricter grounding.")
    if not has_corrections:
        messages.append("Save at least one correction in Analysis first to unlock corrected-analysis actions.")

    if not messages:
        messages.append("Generate Story is the main action. Regenerate and corrected-analysis actions are ready.")

    items = "".join(f"<li>{html.escape(message)}</li>" for message in messages)
    return f"""
    <section class="action-guidance-shell">
      <p class="action-guidance-title">Action availability</p>
      <p class="action-guidance-copy">
        Generate Story is the main next step. Regenerate uses the latest run, and corrected-analysis actions depend on saved Analysis corrections.
      </p>
      <ul class="action-guidance-list">{items}</ul>
    </section>
    """


def present_running_action_guidance() -> str:
    return """
    <section class="action-guidance-shell running">
      <p class="action-guidance-title">Generation in progress</p>
      <p class="action-guidance-copy">
        The current run is still processing. Buttons will unlock automatically when it finishes.
      </p>
    </section>
    """


def present_error(exc: Exception) -> SubmissionOutputs:
    raw_error_text = str(exc)
    escaped_error_text = html.escape(raw_error_text)
    return SubmissionOutputs(
        status_html=_render_status_banner(
            "error",
            "We hit a problem before the story could be generated",
            raw_error_text,
        ),
        story_html=f"""
        <section class="story-card low-confidence">
          <div class="story-meta">Generation blocked</div>
          <div class="story-preview-label">Error details</div>
          <h2 class="story-title">No story yet</h2>
          <p class="placeholder-copy">{escaped_error_text}</p>
        </section>
        """,
        analysis_html=f"""
        <section class="analysis-shell">
          <h3>Analysis</h3>
          <p class="placeholder-copy">{escaped_error_text}</p>
        </section>
        """,
        diagnostics_html=f"""
        <section class="diagnostics-shell">
          <h3>Diagnostics</h3>
          <p class="diagnostic-status"><strong>Error:</strong> {escaped_error_text}</p>
        </section>
        """,
    )


def present_correction_status(
    overrides: Sequence[SceneObservationOverride],
    *,
    generation_mode: str = "default",
    generated_with_corrections: bool = False,
) -> str:
    active_count = len(overrides)
    chips = []
    if active_count:
        chips.append(_render_chip("neutral", f"{active_count} correction{'s' if active_count != 1 else ''} saved"))
    else:
        chips.append(_render_chip("neutral", "No saved corrections"))
    if generated_with_corrections:
        chips.append(_render_chip("caution", "Latest story used corrected analysis"))
    if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
        chips.append(_render_chip("caution", "Strict grounding mode"))

    if active_count:
        items = "".join(
            f"<li>{html.escape(_override_summary(override))}</li>" for override in overrides
        )
        details = f"<ul class=\"notes-list\">{items}</ul>"
    else:
        details = (
            "<p class=\"summary-text\">Save a correction on any image card to make the next corrected "
            "generation use it as authoritative input.</p>"
        )

    return f"""
    <section class="correction-status-shell">
      <h3>Correction status</h3>
      <div class="chip-row">{''.join(chips)}</div>
      {details}
    </section>
    """


def render_observation_editor_card(
    original_observation: SceneObservation,
    effective_observation: SceneObservation,
    *,
    image_path: str | None,
    active_override: SceneObservationOverride | None,
) -> str:
    thumbnail = (
        _render_thumbnail_card(
            image_path=image_path,
            label=f"Image {effective_observation.image_id}",
            caption=Path(image_path).name if image_path is not None else "Image unavailable",
            badge=str(effective_observation.image_id),
            max_size=(220, 160),
        )
        if image_path is not None
        else '<div class="thumb-card"><div class="thumb-media"><div class="thumb-fallback">Image unavailable</div></div></div>'
    )
    details = [
        ("Main subject", effective_observation.entities[0] if effective_observation.entities else "Unknown"),
        ("Setting", effective_observation.setting or "Unknown"),
        ("Visible action", effective_observation.actions[0] if effective_observation.actions else "Unknown"),
        (
            "Same as previous",
            _continuity_label(effective_observation.same_subject_as_previous),
        ),
    ]
    current_details = "".join(
        f"""
        <div class="detail-item compact">
          <span class="detail-label">{html.escape(label)}</span>
          <div class="detail-value">{html.escape(value)}</div>
        </div>
        """
        for label, value in details
    )

    saved_correction = (
        f"""
        <div class="saved-override-note">
          <span class="detail-label">Saved correction</span>
          <div class="detail-value">{html.escape(_override_summary(active_override))}</div>
        </div>
        """
        if active_override is not None
        else """
        <div class="saved-override-note muted">
          <span class="detail-label">Saved correction</span>
          <div class="detail-value">None yet. Leave fields blank unless you want to override the current analysis.</div>
        </div>
        """
    )

    return f"""
    <div class="analysis-editor-header">
      {thumbnail}
      <div class="analysis-editor-meta">
        <h4>Image {effective_observation.image_id}</h4>
        <div class="detail-grid compact">{current_details}</div>
        {saved_correction}
      </div>
    </div>
    {_render_comparison_section(original_observation, effective_observation, active_override)}
    """


def present_empty_analysis_editor() -> str:
    return f"""
    <section class="analysis-editor-empty">
      {_render_empty_state(
          title="Analysis editor",
          description="Generate a story first to inspect scene observations and save bounded corrections.",
          eyebrow="Correction tools",
          mascot_variant="analysis",
          compact=True,
      )}
    </section>
    """


def _classify_confidence(result: StoryResult) -> ConfidencePresentation:
    report = result.evaluation_report
    memory = result.sequence_memory
    flags = report.flags if report is not None else []
    unresolved_ambiguities = (
        memory.unresolved_ambiguities if memory is not None else []
    )
    provider_fallback_notes = _provider_fallback_notes(result)
    grounding_score = report.grounding_score if report is not None else 0.0
    coherence_score = report.coherence_score if report is not None else 0.0

    is_low_confidence = (
        result.is_fallback
        or bool(flags)
        or grounding_score < 0.70
        or coherence_score < 0.70
    )
    is_good = (
        not provider_fallback_notes
        and
        not result.is_fallback
        and not flags
        and grounding_score >= 0.85
        and not unresolved_ambiguities
        and result.revision_attempts == 0
    )

    if is_low_confidence:
        state = "low-confidence"
        banner_title = "We’re not confident enough to present this as a final story yet"
        meta_label = "Low confidence"
    elif is_good:
        state = "good"
        banner_title = "Story ready"
        meta_label = "Story ready"
    else:
        state = "caution"
        banner_title = "Draft story — some details are uncertain"
        meta_label = "Cautious draft"

    if result.is_fallback:
        if result.generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            reason = (
                "Strict grounding stayed active through the revision limit, so the system could not "
                "verify enough image evidence to upgrade this draft."
            )
        else:
            reason = (
                "The revision limit was reached, so unresolved "
                "quality concerns remain."
            )
    elif provider_fallback_notes:
        reason = provider_fallback_notes[0]
    elif flags:
        reason = f"Evaluator warning: {_format_flag(flags[0])}."
    elif unresolved_ambiguities:
        reason = unresolved_ambiguities[0]
    elif result.revision_attempts > 0:
        reason = "The first draft needed revision before it was safe enough to show."
    elif report is not None and grounding_score < 0.85:
        reason = "Grounding stayed below the highest-confidence threshold, so the story is shown as a draft."
    elif report is not None and coherence_score < 0.85:
        reason = "The draft is readable, but the cross-image flow is not yet in the highest-confidence range."
    else:
        reason = "The draft passed evaluation without local fallback, revision-limit warnings, or unresolved sequence ambiguity."

    return ConfidencePresentation(
        state=state,
        banner_title=banner_title,
        meta_label=meta_label,
        reason=reason,
    )


def _render_status_banner(state: str, title: str, reason: str) -> str:
    kicker = {
        "good": "Story status",
        "caution": "Trust cue",
        "low-confidence": "Confidence warning",
        "error": "Generation error",
        "processing": "Generation in progress",
        "neutral": "Workspace status",
    }.get(state, "Workspace status")
    icon_name = {
        "good": "check",
        "caution": "draft",
        "low-confidence": "warning",
        "error": "warning",
        "processing": "spinner",
        "neutral": "frames",
    }.get(state, "frames")
    icon_markup = (
        '<div class="status-spinner" aria-hidden="true"></div>'
        if icon_name == "spinner"
        else _render_icon(icon_name)
    )
    return f"""
    <section class="status-banner {state}">
      <div class="status-head">
        <div class="status-icon-wrap">{icon_markup}</div>
        <div class="status-copy">
          <p class="status-kicker">{html.escape(kicker)}</p>
          <h2 class="status-title">{html.escape(title)}</h2>
          <p class="status-reason">{html.escape(reason)}</p>
        </div>
      </div>
    </section>
    """


def _render_story_tab(
    result: StoryResult,
    sentiment: str,
    image_paths: Sequence[str],
    confidence: ConfidencePresentation,
    comparison: RunComparisonPresentation,
) -> str:
    preview_label = (
        '<div class="story-preview-label">Draft preview</div>'
        if confidence.state == "low-confidence"
        else ""
    )
    story_body = "<br/><br/>".join(
        html.escape(paragraph)
        for paragraph in result.story_text.splitlines()
        if paragraph.strip()
    ) or html.escape(result.story_text)
    story_class = "story-card"
    if confidence.state == "low-confidence":
        story_class += " low-confidence"

    meta_parts = [f"Generated from {len(image_paths)} images", sentiment, confidence.meta_label]
    indicators = []
    if result.applied_overrides:
        indicators.append(_render_chip("neutral", "Generated from corrected analysis"))
        indicators.append(
            _render_chip(
                "neutral",
                f"{len(result.applied_overrides)} manual correction{'s' if len(result.applied_overrides) != 1 else ''} applied",
            )
        )
    if result.generation_mode == STRICT_GROUNDING_GENERATION_MODE:
        indicators.append(_render_chip("caution", "Strict grounding enabled"))

    return f"""
    <section class="{story_class}">
      <div class="story-meta">{html.escape(' · '.join(meta_parts))}</div>
      <div class="story-indicators">{''.join(indicators)}</div>
      {_render_run_comparison_summary(comparison)}
      {preview_label}
      <h2 class="story-title">{html.escape(result.title)}</h2>
      <div class="story-body">{story_body}</div>
      {_render_story_map(result.story_text, result.sentence_alignment, image_paths)}
    </section>
    """


def _render_story_map(
    story_text: str,
    sentence_alignment: Sequence[Sequence[int]],
    image_paths: Sequence[str],
) -> str:
    sentences = _split_sentences(story_text)
    paired_count = min(len(sentences), len(sentence_alignment))
    items: list[str] = []

    for index, sentence in enumerate(sentences[:paired_count], start=1):
        mapped_indices = list(sentence_alignment[index - 1])
        mapped_paths = [
            image_paths[mapped_index - 1]
            for mapped_index in mapped_indices
            if 1 <= mapped_index <= len(image_paths)
        ]
        thumb_markup = "".join(
            _render_thumbnail_card(
                image_path=path,
                label=f"Image {mapped_index}",
                caption="Mapped evidence",
                badge=str(mapped_index),
                max_size=(190, 140),
            )
            for mapped_index, path in zip(mapped_indices, mapped_paths, strict=False)
        )
        mapping_label = (
            f"Images {', '.join(str(value) for value in mapped_indices)}"
            if mapped_indices
            else "No mapped image"
        )
        notes = (
            f'<div class="story-map-thumbs">{thumb_markup}</div>'
            if thumb_markup
            else '<p class="story-map-note">No mapped image evidence is available for this sentence.</p>'
        )
        items.append(
            f"""
            <article class="story-map-item">
              <div class="story-map-meta">Sentence {index} · {html.escape(mapping_label)}</div>
              <p class="story-map-sentence">{html.escape(sentence)}</p>
              {notes}
            </article>
            """
        )

    for index, sentence in enumerate(sentences[paired_count:], start=paired_count + 1):
        items.append(
            f"""
            <article class="story-map-item">
              <div class="story-map-meta">Sentence {index} · No mapped image</div>
              <p class="story-map-sentence">{html.escape(sentence)}</p>
              <p class="story-map-note">No image mapping available for this sentence yet.</p>
            </article>
            """
        )

    if not items:
        items.append(
            """
            <article class="story-map-item">
              <div class="story-map-meta">Story Map</div>
              <p class="story-map-note">No sentence-level mapping is available for this draft.</p>
            </article>
            """
        )

    return f"""
    <section class="story-map">
      <h3>Story Map</h3>
      {''.join(items)}
    </section>
    """


def _render_analysis_tab(result: StoryResult) -> str:
    if not result.scene_observations:
        return """
        <section class="analysis-shell">
          <h3>Analysis</h3>
          <p class="placeholder-copy">No scene observations were returned for this generation.</p>
        </section>
        """

    comparison_summary = _comparison_summary(
        result.original_scene_observations,
        result.scene_observations,
        result.applied_overrides,
    )
    correction_note = (
        f"{len(result.applied_overrides)} manual correction{'s' if len(result.applied_overrides) != 1 else ''} "
        "were applied before sequence linking and story generation."
        if result.applied_overrides
        else "No manual corrections were applied to this run."
    )
    memory = result.sequence_memory
    recurring_entities = (
        _join_values(memory.recurring_entities)
        if memory is not None
        else "No sequence memory available"
    )
    setting_progression = (
        " → ".join(memory.setting_progression)
        if memory is not None and memory.setting_progression
        else "No clear setting progression"
    )
    ambiguities = (
        _list_markup(memory.unresolved_ambiguities, empty_text="None")
        if memory is not None
        else "<p>No sequence memory available</p>"
    )

    return f"""
    <section class="analysis-shell">
      <h3>Analysis</h3>
      <p class="summary-text">{html.escape(correction_note)}</p>
      <p class="summary-text">
        Review the structured image cards below if you want to override the main subject, setting,
        visible action, or subject continuity before regenerating.
      </p>
      {comparison_summary}
      <div class="summary-grid">
        <section class="summary-card">
          <h4>Recurring entities</h4>
          <p>{html.escape(recurring_entities)}</p>
        </section>
        <section class="summary-card">
          <h4>Setting progression</h4>
          <p>{html.escape(setting_progression)}</p>
        </section>
        <section class="summary-card">
          <h4>Unresolved ambiguities</h4>
          {ambiguities}
        </section>
      </div>
    </section>
    """


def _render_diagnostics_tab(
    result: StoryResult,
    confidence: ConfidencePresentation,
    comparison: RunComparisonPresentation,
) -> str:
    report = result.evaluation_report
    if report is None:
        return """
        <section class="diagnostics-shell">
          <h3>Diagnostics</h3>
          <p class="placeholder-copy">No evaluation report is available for this generation.</p>
        </section>
        """

    provider_fallback_notes = _provider_fallback_notes(result)
    chips = [_render_chip(confidence.state, confidence.meta_label)]
    if result.is_fallback:
        chips.append(_render_chip("low-confidence", "Revision limit reached"))
    elif provider_fallback_notes:
        chips.append(_render_chip("caution", "Local fallback active"))
    if result.revision_attempts > 0:
        chips.append(_render_chip("caution", "Revision performed"))
    if report.grounding_score < 0.85:
        chips.append(_render_chip("caution", "Grounding risk"))
    if result.generation_mode == STRICT_GROUNDING_GENERATION_MODE:
        chips.append(_render_chip("caution", "Strict grounding mode"))
    if result.applied_overrides:
        chips.append(
            _render_chip(
                "neutral",
                f"{len(result.applied_overrides)} correction{'s' if len(result.applied_overrides) != 1 else ''} applied",
            )
        )
    if result.sequence_memory is not None and result.sequence_memory.unresolved_ambiguities:
        chips.append(_render_chip("caution", "Sequence ambiguity"))
    if report.sentiment_audit is not None:
        if report.sentiment_audit.score >= 0.78:
            chips.append(_render_chip("neutral", "Sentiment cues clear"))
        elif report.sentiment_audit.score < 0.68:
            chips.append(_render_chip("caution", "Sentiment cues weak"))
    chips.extend(_render_chip("neutral", _format_flag(flag)) for flag in report.flags)

    score_rows = "".join(
        _render_score_row(label, value)
        for label, value in [
            ("Grounding", report.grounding_score),
            ("Coherence", report.coherence_score),
            ("Redundancy", report.redundancy_score),
            ("Sentiment fit", report.sentiment_fit_score),
            ("Readability", report.readability_score),
        ]
    )
    grounding_notes = (
        _list_markup(result.grounding_notes, empty_text="No grounding notes were recorded.")
        if result.grounding_notes
        else "<p class=\"summary-text\">No grounding notes were recorded.</p>"
    )
    override_notes = (
        _list_markup(
            [_override_summary(override) for override in result.applied_overrides],
            empty_text="No manual corrections were used in this run.",
        )
        if result.applied_overrides
        else "<p class=\"summary-text\">No manual corrections were used in this run.</p>"
    )
    sentiment_audit = _render_sentiment_audit(report.sentiment_audit)
    max_attempts = (
        STRICT_MAX_REVISION_ATTEMPTS
        if result.generation_mode == STRICT_GROUNDING_GENERATION_MODE
        else DEFAULT_MAX_REVISION_ATTEMPTS
    )

    return f"""
    <section class="diagnostics-shell">
      <h3>Diagnostics</h3>
      <p class="diagnostic-status"><strong>{html.escape(confidence.meta_label)}:</strong> {html.escape(confidence.reason)}</p>
      <div class="chip-row">{''.join(chips)}</div>
      {_render_run_comparison_detail(comparison)}
      <div class="score-list">{score_rows}</div>
      <p class="diagnostic-meta"><strong>Revision attempts:</strong> {result.revision_attempts} / {max_attempts} revisions used</p>
      <p class="diagnostic-meta"><strong>Generation mode:</strong> {html.escape(_mode_label(result.generation_mode))}</p>
      <p class="summary-text"><strong>Evaluator summary:</strong> {html.escape(report.summary)}</p>
      <div class="summary-grid">
        <section class="summary-card">
          <h4>Provider status</h4>
          {_list_markup(_provider_status_lines(result), empty_text="Provider-backed execution completed without local fallback.")}
        </section>
        <section class="summary-card">
          <h4>Grounding notes</h4>
          {grounding_notes}
        </section>
        <section class="summary-card">
          <h4>Sentiment audit</h4>
          {sentiment_audit}
        </section>
        <section class="summary-card">
          <h4>Applied corrections</h4>
          {override_notes}
        </section>
      </div>
    </section>
    """


def _render_score_row(label: str, value: float) -> str:
    clamped_value = max(0.0, min(value, 1.0))
    percentage = int(round(clamped_value * 100))
    return f"""
    <div class="score-row">
      <div class="score-label">{html.escape(label)}</div>
      <div class="score-bar">
        <div class="score-fill" style="width: {percentage}%;"></div>
      </div>
      <div class="score-value">{clamped_value:.2f}</div>
    </div>
    """


def _render_chip(state: str, label: str) -> str:
    return (
        f'<span class="chip {state}">{_render_icon(_chip_icon_name(state, label))}'
        f'<span>{html.escape(label)}</span></span>'
    )


def _render_icon(name: str) -> str:
    icons = {
        "alert": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M10 2.4l7 12.2a1 1 0 0 1-.87 1.5H3.87A1 1 0 0 1 3 14.6l7-12.2z" fill="currentColor" opacity="0.18"></path>
              <path d="M10 6.2v4.8" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path>
              <circle cx="10" cy="13.8" r="1.1" fill="currentColor"></circle>
            </svg>
        """,
        "check": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <circle cx="10" cy="10" r="7.2" fill="currentColor" opacity="0.16"></circle>
              <path d="M6.5 10.3l2.2 2.2 4.8-5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.9"></path>
            </svg>
        """,
        "compare": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <rect x="2.5" y="4.2" width="6.5" height="11.6" rx="2" fill="currentColor" opacity="0.14"></rect>
              <rect x="11" y="4.2" width="6.5" height="11.6" rx="2" fill="currentColor" opacity="0.14"></rect>
              <path d="M6 7.2h-.8a1.7 1.7 0 0 0 0 3.4H8" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"></path>
              <path d="M14 12.8h.8a1.7 1.7 0 0 0 0-3.4H12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"></path>
            </svg>
        """,
        "draft": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M4.2 13.9l1 1 2.5-.4 6.5-6.5-2-2-6.5 6.5z" fill="currentColor" opacity="0.18"></path>
              <path d="M11.2 5.8l2 2 1.4-1.4a1.4 1.4 0 0 0 0-2l-.1-.1a1.4 1.4 0 0 0-2 0z" fill="currentColor"></path>
              <path d="M5.1 14.9l2.4-.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.4"></path>
            </svg>
        """,
        "edit": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M4.5 14.6l2.6-.5 7.1-7.1-2.1-2.1-7.1 7.1z" fill="currentColor" opacity="0.16"></path>
              <path d="M11.8 4.9l2.1 2.1" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.7"></path>
              <path d="M4.5 14.6l2.2-.4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"></path>
            </svg>
        """,
        "frames": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <rect x="3" y="4" width="6.8" height="9.2" rx="1.6" fill="currentColor" opacity="0.14"></rect>
              <rect x="10.2" y="6.8" width="6.8" height="9.2" rx="1.6" fill="currentColor" opacity="0.18"></rect>
              <path d="M5.2 7h2.4M12.3 9.8h2.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.4"></path>
            </svg>
        """,
        "spark": """
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M10 3.2l1.5 3.5L15 8.2l-3.5 1.5L10 13.2 8.5 9.7 5 8.2l3.5-1.5z" fill="currentColor" opacity="0.18"></path>
              <path d="M15.2 3.8l.5 1.2 1.2.5-1.2.5-.5 1.2-.5-1.2-1.2-.5 1.2-.5zM4.6 12.9l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6z" fill="currentColor"></path>
            </svg>
        """,
    }
    svg = icons.get(name, icons["spark"])
    return f'<span class="ui-icon {name}">{svg}</span>'


def _chip_icon_name(state: str, label: str) -> str:
    normalized = label.lower()
    if "strict grounding" in normalized:
        return "compare"
    if "correction" in normalized or "corrected analysis" in normalized:
        return "edit"
    if "fallback" in normalized or "risk" in normalized or "ambiguity" in normalized:
        return "alert"
    if "comparison" in normalized:
        return "compare"
    if "trust improved" in normalized or state == "good":
        return "check"
    if "mixed result" in normalized or state == "caution":
        return "draft"
    if state in {"low-confidence", "error"}:
        return "alert"
    if "same images" in normalized or "different images" in normalized:
        return "frames"
    return "spark"


def _render_run_comparison_summary(comparison: RunComparisonPresentation) -> str:
    if not comparison.available:
        return f"""
        <section class="run-summary-shell">
          <div class="run-summary-head">{_render_icon("compare")}<span>Run comparison</span></div>
          <div class="run-summary-empty">
            {_render_mascot("comparison")}
            <p class="run-summary-copy">No previous run in this session yet. Generate again to compare trust signals.</p>
          </div>
        </section>
        """

    highlight_markup = ""
    if comparison.comparable:
        highlight_metrics = comparison.metric_rows[:3]
        highlight_markup = "".join(
            f"""
            <div class="run-highlight">
              <span class="run-highlight-label">{html.escape(metric.label)}</span>
              <span class="run-highlight-value {metric.trend}">{html.escape(metric.delta_value)}</span>
            </div>
            """
            for metric in highlight_metrics
        )

    verdict_chip = ""
    if comparison.verdict != comparison.scope_label:
        verdict_chip = _render_chip(
            "caution" if comparison.verdict == "Mixed result" else "good" if comparison.verdict == "Trust improved" else "neutral",
            comparison.verdict,
        )

    return f"""
    <section class="run-summary-shell">
      <div class="run-summary-head">{_render_icon("compare")}<span>Run comparison</span></div>
      <div class="chip-row">
        {_render_chip("neutral", comparison.scope_label)}
        {verdict_chip}
      </div>
      <p class="run-summary-copy">{html.escape(comparison.summary)}</p>
      <div class="run-highlight-grid">{highlight_markup}</div>
    </section>
    """


def _render_run_comparison_detail(comparison: RunComparisonPresentation) -> str:
    if not comparison.available:
        return f"""
        <section class="run-detail-shell">
          <h4 class="icon-heading">{_render_icon("compare")}<span>Previous vs current run</span></h4>
          <p class="summary-text">No previous run in this session yet. A detailed comparison appears after the next generation.</p>
        </section>
        """

    previous = comparison.previous_snapshot
    current = comparison.current_snapshot
    assert previous is not None

    metadata_chips = [
        _render_chip("neutral" if comparison.same_images else "caution", "Same images" if comparison.same_images else "Different images"),
        _render_chip("neutral" if comparison.same_sentiment else "caution", "Same sentiment" if comparison.same_sentiment else "Different sentiment"),
        _render_chip("neutral", f"Corrections {previous.correction_count} → {current.correction_count}"),
        _render_chip(
            "neutral",
            f"Strict grounding {'on' if previous.strict_grounding else 'off'} → {'on' if current.strict_grounding else 'off'}",
        ),
    ]
    verdict_chip = ""
    if comparison.verdict != comparison.scope_label:
        verdict_chip = _render_chip(
            "caution" if comparison.verdict == "Mixed result" else "good" if comparison.verdict == "Trust improved" else "neutral",
            comparison.verdict,
        )
    rows = "".join(
        f"""
        <div class="run-table-cell metric">{html.escape(metric.label)}</div>
        <div class="run-table-cell">{html.escape(metric.previous_value)}</div>
        <div class="run-table-cell">{html.escape(metric.current_value)}</div>
        <div class="run-table-cell {metric.trend}">{html.escape(metric.delta_value)}</div>
        """
        for metric in comparison.metric_rows
    )

    return f"""
    <section class="run-detail-shell">
      <h4 class="icon-heading">{_render_icon("compare")}<span>Previous vs current run</span></h4>
      <div class="chip-row">
        {_render_chip("neutral", comparison.scope_label)}
        {verdict_chip}
        {''.join(metadata_chips)}
      </div>
      <p class="summary-text">{html.escape(comparison.summary)}</p>
      <div class="run-comparison-table">
        <div class="run-table-head">Metric</div>
        <div class="run-table-head">Previous</div>
        <div class="run-table-head">Current</div>
        <div class="run-table-head">Delta</div>
        {rows}
      </div>
    </section>
    """


def _build_run_comparison(
    *,
    previous_run_snapshot: RunSnapshot | None,
    current_run_snapshot: RunSnapshot | None,
) -> RunComparisonPresentation:
    if current_run_snapshot is None:
        return RunComparisonPresentation(
            available=False,
            comparable=False,
            scope_label="No comparison yet",
            verdict="No previous run",
            summary="No previous run in this session yet.",
            metric_rows=[],
            same_images=False,
            same_sentiment=False,
            previous_snapshot=previous_run_snapshot,
            current_snapshot=RunSnapshot(
                image_signature=[],
                image_count=0,
                sentiment="unknown",
                correction_count=0,
                generation_mode="default",
                strict_grounding=False,
                fallback_used=False,
                flag_count=0,
                grounding_score=0.0,
                coherence_score=0.0,
                redundancy_score=0.0,
                sentiment_fit_score=0.0,
                readability_score=0.0,
            ),
        )

    if previous_run_snapshot is None:
        return RunComparisonPresentation(
            available=False,
            comparable=False,
            scope_label="No previous run",
            verdict="No previous run",
            summary="No previous run in this session yet.",
            metric_rows=[],
            same_images=False,
            same_sentiment=False,
            previous_snapshot=None,
            current_snapshot=current_run_snapshot,
        )

    same_images = previous_run_snapshot.image_signature == current_run_snapshot.image_signature
    same_sentiment = previous_run_snapshot.sentiment == current_run_snapshot.sentiment
    comparable = same_images and same_sentiment
    scope_label = "Direct comparison" if comparable else "Limited comparison"
    metric_rows = _build_metric_rows(previous_run_snapshot, current_run_snapshot)
    verdict, summary = _generate_comparison_verdict(
        previous_run_snapshot,
        current_run_snapshot,
        comparable=comparable,
        same_images=same_images,
        same_sentiment=same_sentiment,
    )
    return RunComparisonPresentation(
        available=True,
        comparable=comparable,
        scope_label=scope_label,
        verdict=verdict,
        summary=summary,
        metric_rows=metric_rows,
        same_images=same_images,
        same_sentiment=same_sentiment,
        previous_snapshot=previous_run_snapshot,
        current_snapshot=current_run_snapshot,
    )


def _build_metric_rows(
    previous_snapshot: RunSnapshot,
    current_snapshot: RunSnapshot,
) -> list[MetricDeltaPresentation]:
    score_rows = [
        _metric_delta_row("Grounding", previous_snapshot.grounding_score, current_snapshot.grounding_score),
        _metric_delta_row("Coherence", previous_snapshot.coherence_score, current_snapshot.coherence_score),
        _metric_delta_row("Redundancy", previous_snapshot.redundancy_score, current_snapshot.redundancy_score),
        _metric_delta_row("Sentiment fit", previous_snapshot.sentiment_fit_score, current_snapshot.sentiment_fit_score),
        _metric_delta_row("Readability", previous_snapshot.readability_score, current_snapshot.readability_score),
    ]
    warning_delta = current_snapshot.flag_count - previous_snapshot.flag_count
    warning_trend = "positive" if warning_delta < 0 else "negative" if warning_delta > 0 else "neutral"
    fallback_delta = _fallback_delta(previous_snapshot.fallback_used, current_snapshot.fallback_used)
    fallback_trend = "positive" if fallback_delta == "Improved" else "negative" if fallback_delta == "Worse" else "neutral"

    score_rows.extend(
        [
            MetricDeltaPresentation(
                label="Revision limit reached",
                previous_value="Yes" if previous_snapshot.fallback_used else "No",
                current_value="Yes" if current_snapshot.fallback_used else "No",
                delta_value=fallback_delta,
                trend=fallback_trend,
            ),
            MetricDeltaPresentation(
                label="Warning count",
                previous_value=str(previous_snapshot.flag_count),
                current_value=str(current_snapshot.flag_count),
                delta_value=f"{warning_delta:+d}",
                trend=warning_trend,
            ),
        ]
    )
    return score_rows


def _metric_delta_row(label: str, previous_value: float, current_value: float) -> MetricDeltaPresentation:
    delta = current_value - previous_value
    trend = "positive" if delta >= 0.03 else "negative" if delta <= -0.03 else "neutral"
    return MetricDeltaPresentation(
        label=label,
        previous_value=f"{previous_value:.2f}",
        current_value=f"{current_value:.2f}",
        delta_value=f"{delta:+.2f}",
        trend=trend,
    )


def _generate_comparison_verdict(
    previous_snapshot: RunSnapshot,
    current_snapshot: RunSnapshot,
    *,
    comparable: bool,
    same_images: bool,
    same_sentiment: bool,
) -> tuple[str, str]:
    if not comparable:
        reasons = []
        if not same_images:
            reasons.append("different images")
        if not same_sentiment:
            reasons.append("different sentiment")
        reason_text = " and ".join(reasons)
        return (
            "Limited comparison",
            f"The previous run used {reason_text}, so this comparison is informative but not a direct trust benchmark.",
        )

    score_deltas = [
        current_snapshot.grounding_score - previous_snapshot.grounding_score,
        current_snapshot.coherence_score - previous_snapshot.coherence_score,
        current_snapshot.redundancy_score - previous_snapshot.redundancy_score,
        current_snapshot.sentiment_fit_score - previous_snapshot.sentiment_fit_score,
        current_snapshot.readability_score - previous_snapshot.readability_score,
    ]
    positive_signals = sum(1 for delta in score_deltas if delta >= 0.03)
    negative_signals = sum(1 for delta in score_deltas if delta <= -0.03)

    if previous_snapshot.fallback_used and not current_snapshot.fallback_used:
        positive_signals += 2
    elif not previous_snapshot.fallback_used and current_snapshot.fallback_used:
        negative_signals += 2

    if current_snapshot.flag_count < previous_snapshot.flag_count:
        positive_signals += 1
    elif current_snapshot.flag_count > previous_snapshot.flag_count:
        negative_signals += 1

    if positive_signals >= 2 and negative_signals == 0:
        return (
            "Trust improved",
            "Compared with the previous run on the same images and sentiment, the latest run improved trust signals without any clear regression.",
        )
    if positive_signals == 0 and negative_signals == 0:
        return (
            "No meaningful change",
            "Compared with the previous run on the same images and sentiment, the latest run is materially similar.",
        )
    return (
        "Mixed result",
        "Some trust signals improved, but others stayed flat or weakened, so the result should be reviewed with care.",
    )


def _fallback_delta(previous_value: bool, current_value: bool) -> str:
    if previous_value and not current_value:
        return "Improved"
    if not previous_value and current_value:
        return "Worse"
    return "No change"


def _render_comparison_section(
    original_observation: SceneObservation,
    effective_observation: SceneObservation,
    active_override: SceneObservationOverride | None,
) -> str:
    comparisons = [
        (
            "Main subject",
            original_observation.entities[0] if original_observation.entities else "Unknown",
            effective_observation.entities[0] if effective_observation.entities else "Unknown",
        ),
        (
            "Setting",
            original_observation.setting or "Unknown",
            effective_observation.setting or "Unknown",
        ),
        (
            "Visible action",
            original_observation.actions[0] if original_observation.actions else "Unknown",
            effective_observation.actions[0] if effective_observation.actions else "Unknown",
        ),
        (
            "Same-subject continuity",
            _continuity_label(original_observation.same_subject_as_previous),
            _continuity_label(effective_observation.same_subject_as_previous),
        ),
        (
            "User note",
            "No note",
            active_override.generation_note if active_override and active_override.generation_note else "No note",
        ),
    ]
    rows = "".join(
        _render_comparison_row(label, original_value, effective_value)
        for label, original_value, effective_value in comparisons
    )
    return f"""
    <section class="comparison-shell">
      <div class="comparison-header">
        <h5>Original vs corrected</h5>
        <p>Changed fields are highlighted so you can inspect exactly what will feed the next regeneration.</p>
      </div>
      <div class="comparison-table">
        <div class="comparison-table-head">Field</div>
        <div class="comparison-table-head">Original</div>
        <div class="comparison-table-head">Effective</div>
        <div class="comparison-table-head">Status</div>
        {rows}
      </div>
    </section>
    """


def _render_comparison_row(label: str, original_value: str, effective_value: str) -> str:
    changed = original_value != effective_value
    status_label = "Changed" if changed else "Unchanged"
    status_class = "changed" if changed else "unchanged"
    return f"""
    <div class="comparison-cell field">{html.escape(label)}</div>
    <div class="comparison-cell original">{html.escape(original_value)}</div>
    <div class="comparison-cell effective">{html.escape(effective_value)}</div>
    <div class="comparison-cell status">
      <span class="comparison-pill {status_class}">{html.escape(status_label)}</span>
    </div>
    """


def _comparison_summary(
    original_observations: Sequence[SceneObservation],
    effective_observations: Sequence[SceneObservation],
    applied_overrides: Sequence[SceneObservationOverride],
) -> str:
    if not original_observations or not effective_observations:
        return ""
    changed_fields = 0
    for original, effective in zip(original_observations, effective_observations, strict=False):
        if (original.entities[:1] or ["Unknown"]) != (effective.entities[:1] or ["Unknown"]):
            changed_fields += 1
        if (original.setting or "Unknown") != (effective.setting or "Unknown"):
            changed_fields += 1
        if (original.actions[:1] or ["Unknown"]) != (effective.actions[:1] or ["Unknown"]):
            changed_fields += 1
        if original.same_subject_as_previous != effective.same_subject_as_previous:
            changed_fields += 1
    if any(override.generation_note for override in applied_overrides):
        changed_fields += sum(1 for override in applied_overrides if override.generation_note)

    changed_images = len(applied_overrides)
    if changed_fields == 0:
        return """
        <section class="comparison-summary-shell">
          <p class="summary-text">No comparison deltas are active yet. Save a correction to preview the effective analysis beside the original.</p>
        </section>
        """
    return f"""
    <section class="comparison-summary-shell">
      <div class="chip-row">
        { _render_chip("neutral", f"{changed_images} corrected image{'s' if changed_images != 1 else ''}") }
        { _render_chip("caution", f"{changed_fields} changed field{'s' if changed_fields != 1 else ''}") }
      </div>
      <p class="summary-text">Compare the original analysis with the effective corrected version in the cards below before regenerating.</p>
    </section>
    """


def _render_empty_state(
    *,
    title: str,
    description: str,
    eyebrow: str,
    mascot_variant: str,
    compact: bool,
) -> str:
    compact_class = " compact" if compact else ""
    return f"""
    <div class="empty-state-shell{compact_class}">
      <div class="empty-state-illustration">
        {_render_mascot(mascot_variant)}
      </div>
      <div class="empty-state-copy">
        <div class="empty-state-eyebrow">{html.escape(eyebrow)}</div>
        <h3>{html.escape(title)}</h3>
        <p class="placeholder-copy">{html.escape(description)}</p>
      </div>
    </div>
    """


def _render_mascot(variant: str) -> str:
    class_name = html.escape(variant)
    return f"""
    <div class="story-mascot {class_name}" aria-hidden="true">
      <svg viewBox="0 0 120 120" role="presentation">
        <defs>
          <linearGradient id="mascot-body-{class_name}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff"></stop>
            <stop offset="100%" stop-color="#f5f7fa"></stop>
          </linearGradient>
        </defs>
        <circle cx="60" cy="60" r="44" fill="#ffffff"></circle>
        <path d="M27 43h22a8 8 0 0 1 8 8v27a8 8 0 0 1-8 8H27a8 8 0 0 1-8-8V51a8 8 0 0 1 8-8z" fill="#eef1f5"></path>
        <path d="M71 33h22a8 8 0 0 1 8 8v31a8 8 0 0 1-8 8H71a8 8 0 0 1-8-8V41a8 8 0 0 1 8-8z" fill="url(#mascot-body-{class_name})" stroke="#d9dee5" stroke-width="2"></path>
        <path d="M75 43h14M75 50h10" fill="none" stroke="#e16f46" stroke-linecap="round" stroke-width="3"></path>
        <circle cx="80" cy="60" r="2.8" fill="#050505"></circle>
        <circle cx="92" cy="60" r="2.8" fill="#050505"></circle>
        <path d="M79 69c3.1 3.1 10.9 3.1 14 0" fill="none" stroke="#1f6f78" stroke-linecap="round" stroke-width="2.6"></path>
        <circle cx="42" cy="35" r="6" fill="#f8cbb8"></circle>
        <circle cx="97" cy="91" r="5" fill="#edf4f6"></circle>
        <path d="M38 89l4 8 8 4-8 4-4 8-4-8-8-4 8-4z" fill="#f8cbb8"></path>
      </svg>
    </div>
    """


def _render_thumbnail_card(
    *,
    image_path: str,
    label: str,
    caption: str,
    badge: str,
    max_size: tuple[int, int],
) -> str:
    data_uri = _build_thumbnail_data_uri(image_path, max_size=max_size)
    media = (
        f'<img alt="{html.escape(label)}" src="{data_uri}" />'
        if data_uri is not None
        else '<div class="thumb-fallback">Preview unavailable</div>'
    )
    return f"""
    <div class="thumb-card">
      <div class="thumb-media">
        {media}
        <span class="thumb-badge">{html.escape(badge)}</span>
      </div>
      <div class="thumb-meta">
        <div class="thumb-name">{html.escape(label)}</div>
        <div class="thumb-caption">{html.escape(caption)}</div>
      </div>
    </div>
    """


def _build_thumbnail_data_uri(
    image_path: str,
    *,
    max_size: tuple[int, int],
) -> str | None:
    try:
        with Image.open(image_path) as image:
            preview = image.convert("RGB")
            preview.thumbnail(max_size)
            canvas = Image.new("RGB", max_size, color="#f5f7fa")
            x_offset = (max_size[0] - preview.width) // 2
            y_offset = (max_size[1] - preview.height) // 2
            canvas.paste(preview, (x_offset, y_offset))
            buffer = io.BytesIO()
            canvas.save(buffer, format="PNG")
    except (FileNotFoundError, OSError, UnidentifiedImageError):
        return None

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _split_sentences(story_text: str) -> list[str]:
    normalized = " ".join(story_text.strip().split())
    if not normalized:
        return []
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalized)
        if sentence.strip()
    ]
    return sentences or [normalized]


def _join_values(values: Sequence[str]) -> str:
    return ", ".join(values) if values else "None"


def _provider_fallback_notes(result: StoryResult) -> list[str]:
    if result.provider_status:
        return [
            entry.reason
            for entry in result.provider_status
            if entry.execution_mode == "local_fallback" and entry.reason is not None
        ]

    notes: list[str] = []

    for note in result.grounding_notes:
        if "Local fallback was used" in note or "Local deterministic fallback was used" in note:
            notes.append(note)

    report = result.evaluation_report
    if report is not None:
        summary = report.summary
        if "Local fallback was used" in summary or "Local deterministic evaluation was used" in summary:
            notes.append(summary)

    return _dedupe_preserving_order(notes)


def _provider_status_lines(result: StoryResult) -> list[str]:
    if result.provider_status:
        lines: list[str] = []
        for entry in result.provider_status:
            stage_label = entry.stage.replace("_", " ")
            mode_label = (
                "Local fallback"
                if entry.execution_mode == "local_fallback"
                else "Provider"
            )
            line = f"{stage_label}: {mode_label}"
            if entry.reason is not None:
                line += f". {entry.reason}"
            if entry.recovery_hint is not None:
                line += f" Recovery: {entry.recovery_hint}"
            lines.append(line)
        return lines

    return _provider_fallback_notes(result)


def _list_markup(values: Sequence[str], *, empty_text: str) -> str:
    if not values:
        return f"<p>{html.escape(empty_text)}</p>"
    items = "".join(f"<li>{html.escape(value)}</li>" for value in values)
    return f"<ul>{items}</ul>"


def _render_sentiment_audit(audit: SentimentAudit | None) -> str:
    if audit is None:
        return '<p class="summary-text">No deterministic sentiment audit was recorded for this run.</p>'

    details = [
        f"Target: {audit.target_sentiment}",
        f"Audit score: {audit.score:.2f}",
        f"Matched keywords: {', '.join(audit.matched_keywords) if audit.matched_keywords else 'none'}",
        f"Matched style cues: {', '.join(audit.matched_style_cues) if audit.matched_style_cues else 'none'}",
    ]
    if audit.missing_keywords:
        details.append(f"Still missing keywords: {', '.join(audit.missing_keywords[:3])}")
    if audit.missing_style_cues:
        details.append(f"Still missing style cues: {', '.join(audit.missing_style_cues[:2])}")

    return (
        f'<p class="summary-text">{html.escape(audit.summary)}</p>'
        f'{_list_markup(details, empty_text="No audit details were recorded.")}'
    )


def _dedupe_preserving_order(values: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()

    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)

    return deduped


def _format_flag(flag: str) -> str:
    return flag.replace("_", " ").strip().capitalize()


def _override_summary(override: SceneObservationOverride) -> str:
    parts = [f"Image {override.image_id}"]
    if override.main_entity is not None:
        parts.append(f"subject={override.main_entity}")
    if override.setting is not None:
        parts.append(f"setting={override.setting}")
    if override.visible_action is not None:
        parts.append(f"action={override.visible_action}")
    if override.same_subject_as_previous is not None:
        continuity = "same as previous" if override.same_subject_as_previous else "different from previous"
        parts.append(f"continuity={continuity}")
    if override.generation_note is not None:
        parts.append(f"note={override.generation_note}")
    return "; ".join(parts)


def _mode_label(generation_mode: str) -> str:
    if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
        return "Strict grounding"
    return "Default"


def _continuity_label(value: bool | None) -> str:
    if value is True:
        return "Confirmed same subject as previous"
    if value is False:
        return "Confirmed different subject from previous"
    return "Not manually confirmed"
