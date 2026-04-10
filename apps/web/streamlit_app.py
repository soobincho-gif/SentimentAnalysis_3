from __future__ import annotations

import os
from pathlib import Path
import sys
from time import sleep

from dotenv import load_dotenv
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from apps.web.streamlit_presenter import (  # noqa: E402
    StoryStatus,
    classify_story_result,
    metric_rows,
    observation_payload,
    provider_fallback_notes,
    story_map_rows,
)
from apps.web.streamlit_styles import STREAMLIT_CSS  # noqa: E402
from packages.core.models.story import (  # noqa: E402
    DEFAULT_GENERATION_MODE,
    STRICT_GROUNDING_GENERATION_MODE,
    StoryRequest,
    StoryResult,
)
from packages.infra.bootstrap import build_pipeline  # noqa: E402
from packages.infra.upload_persistence import cleanup_persisted_images, persist_uploaded_images  # noqa: E402
from packages.prompts.sentiment_profiles import SUPPORTED_SENTIMENT_LABELS  # noqa: E402

GITHUB_REPO_URL = "https://github.com/soobincho-gif/SentimentAnalysis_3"
STREAMLIT_PLACEHOLDER_URL = "Streamlit Cloud publish pending"
SAMPLE_SEQUENCES = {
    "Dog walk sequence": {
        "description": "Three ordered frames that usually produce a coherent, grounded slice-of-life story.",
        "paths": [
            ROOT_DIR / "assets" / "raw_samples" / "dog_walk_sequence" / "dog_park_walking.png",
            ROOT_DIR / "assets" / "raw_samples" / "dog_walk_sequence" / "dog_park_playing.png",
            ROOT_DIR / "assets" / "raw_samples" / "dog_walk_sequence" / "dog_home_resting.png",
        ],
    },
    "Ambiguous abstract sequence": {
        "description": "Abstract frames used to surface low-confidence and ambiguity handling.",
        "paths": [
            ROOT_DIR / "assets" / "raw_samples" / "ambiguous_sequence" / "frame_01.png",
            ROOT_DIR / "assets" / "raw_samples" / "ambiguous_sequence" / "frame_02.png",
            ROOT_DIR / "assets" / "raw_samples" / "ambiguous_sequence" / "frame_03.png",
        ],
    },
}
SUPPORTED_SENTIMENTS = list(SUPPORTED_SENTIMENT_LABELS)


@st.cache_resource(show_spinner=False)
def get_pipeline():
    return build_pipeline()


def main() -> None:
    st.set_page_config(
        page_title="Visual Storytelling from Images + Sentiment",
        page_icon="📚",
        layout="wide",
    )
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
    _init_state()

    st.markdown(
        f"""
        <section class="hero-shell">
          <p class="hero-kicker">Grounded visual storytelling</p>
          <h1 class="hero-title">Visual Storytelling from Images + Sentiment</h1>
          <p class="hero-copy">
            Upload an ordered image sequence or load a built-in sample, choose the narrative tone,
            and generate a short story that stays anchored to the visible scene evidence.
          </p>
          <div class="repo-links">
            <a href="{GITHUB_REPO_URL}" target="_blank" rel="noopener noreferrer">GitHub repository</a>
            <span class="link-pill">Streamlit demo: {STREAMLIT_PLACEHOLDER_URL}</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _render_sidebar()

    left_col, right_col = st.columns([1.02, 1.24], gap="large")
    with left_col:
        active_source = _render_input_panel()
        _render_sequence_preview(active_source)

    with right_col:
        _render_result_panel(active_source)


def _init_state() -> None:
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("status", None)
    st.session_state.setdefault("last_error", None)
    st.session_state.setdefault("last_run_signature", None)
    st.session_state.setdefault("last_run_meta", {})
    st.session_state.setdefault("input_mode", "Use included sample")
    st.session_state.setdefault("sample_name", "Dog walk sequence")
    st.session_state.setdefault("strict_grounding", False)
    st.session_state.setdefault("sentiment", "heartwarming")
    st.session_state.setdefault("max_sentences", 5)


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Workspace guide")
        st.markdown(
            """
            1. Choose an input source.
            2. Confirm the image order.
            3. Pick a sentiment and optional stricter grounding.
            4. Generate the story, then inspect the trace tabs.
            """
        )
        st.markdown("### Pipeline stages")
        st.markdown(
            """
            `Image preprocessing` -> `Scene observations` -> `Sequence memory`
            -> `Narrative plan` -> `Sentiment profile` -> `Story draft`
            -> `Evaluation`
            """
        )
        if st.button("Clear current result", use_container_width=True):
            st.session_state.result = None
            st.session_state.status = None
            st.session_state.last_error = None
            st.session_state.last_run_signature = None
            st.session_state.last_run_meta = {}
            st.rerun()


def _render_input_panel() -> dict[str, object]:
    st.markdown(
        """
        <section class="panel-card">
          <p class="section-kicker">Input workspace</p>
          <h2 class="panel-title">Build the image sequence</h2>
          <p class="panel-copy">
            Upload images in the intended order or start from one of the included sample sets.
            The story generator follows this sequence exactly.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.input_mode = st.radio(
        "Input source",
        options=["Use included sample", "Upload images"],
        horizontal=True,
        key="input_mode_radio",
        index=0 if st.session_state.input_mode == "Use included sample" else 1,
    )
    st.session_state.input_mode = st.session_state.input_mode_radio

    uploaded_files = None
    sample_paths: list[Path] = []
    source_label = ""

    if st.session_state.input_mode == "Use included sample":
        st.session_state.sample_name = st.selectbox(
            "Sample sequence",
            options=list(SAMPLE_SEQUENCES.keys()),
            index=list(SAMPLE_SEQUENCES.keys()).index(st.session_state.sample_name),
        )
        selected = SAMPLE_SEQUENCES[st.session_state.sample_name]
        sample_paths = list(selected["paths"])
        source_label = st.session_state.sample_name
        st.caption(selected["description"])
    else:
        uploaded_files = st.file_uploader(
            "Upload images",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Upload the frames in the order you want the story to follow.",
        )
        source_label = "Uploaded sequence"

    st.session_state.sentiment = st.radio(
        "Sentiment",
        options=SUPPORTED_SENTIMENTS,
        index=SUPPORTED_SENTIMENTS.index(st.session_state.sentiment),
        horizontal=True,
        help="Tone shapes wording and pacing, not the underlying facts.",
    )
    st.session_state.max_sentences = int(
        st.slider(
            "Maximum sentences",
            min_value=3,
            max_value=7,
            value=int(st.session_state.max_sentences),
            step=1,
        )
    )
    st.session_state.strict_grounding = st.toggle(
        "Use stricter grounding",
        value=bool(st.session_state.strict_grounding),
        help="Prefer more literal transitions and less speculative bridge language.",
    )

    active_source = {
        "mode": st.session_state.input_mode,
        "source_label": source_label,
        "uploaded_files": uploaded_files or [],
        "sample_paths": sample_paths,
    }

    signature = _build_signature(active_source)
    if (
        st.session_state.result is not None
        and st.session_state.last_run_signature is not None
        and signature != st.session_state.last_run_signature
    ):
        st.info("Inputs changed since the last run. Generate again to refresh the story and diagnostics.")

    if st.button("Generate story", type="primary", use_container_width=True):
        _generate_story(active_source, signature)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    return active_source


def _render_sequence_preview(active_source: dict[str, object]) -> None:
    image_items = _preview_items(active_source)
    st.markdown(
        """
        <section class="panel-card">
          <p class="section-kicker">Ordered storyboard</p>
          <h2 class="panel-title">Sequence preview</h2>
          <p class="panel-copy">The story follows these frames from left to right.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not image_items:
        st.markdown(
            """
            <section class="placeholder-card">
              <p class="label-chip">Awaiting sequence</p>
              <div class="body-copy">Choose a sample set or upload images to preview the frames here.</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        return

    preview_columns = st.columns(len(image_items))
    for column, item in zip(preview_columns, image_items, strict=False):
        with column:
            st.markdown('<div class="streamlit-image-frame">', unsafe_allow_html=True)
            st.image(item["image"], caption=item["caption"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _render_result_panel(active_source: dict[str, object]) -> None:
    result = st.session_state.result
    if result is None:
        st.markdown(
            """
            <section class="status-card caution">
              <p class="status-kicker">Workspace status</p>
              <h2 class="status-title">Ready to generate a grounded story</h2>
              <p class="status-copy">
                The right panel will show the generated story, confidence state, scene observations,
                sequence memory, and evaluator diagnostics after a run completes.
              </p>
            </section>
            <section class="story-card">
              <p class="story-meta">Story output</p>
              <h2 class="story-title">No story yet</h2>
              <div class="story-body">
                Start with the included sample sequence or upload your own ordered images, then generate to inspect the full storytelling pipeline.
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        return

    status = st.session_state.status or classify_story_result(result)
    _render_status_card(status)
    _render_story_card(result, status, active_source)

    metric_columns = st.columns(max(len(metric_rows(result)), 1))
    for column, metric in zip(metric_columns, metric_rows(result), strict=False):
        with column:
            label, value = metric
            st.metric(label=label, value=f"{value:.2f}")
            st.caption("0.00 to 1.00 quality score")

    story_tab, analysis_tab, diagnostics_tab = st.tabs(["Story", "Analysis", "Diagnostics"])

    with story_tab:
        story_map = story_map_rows(result)
        if story_map:
            st.markdown("#### Sentence-to-image map")
            for index, (sentence, image_ids) in enumerate(story_map, start=1):
                mapped = ", ".join(f"Image {image_id}" for image_id in image_ids) or "No explicit alignment"
                st.markdown(
                    f"""
                    <section class="story-map-card">
                      <p class="label-chip">Sentence {index}</p>
                      <div class="body-copy"><strong>{mapped}</strong></div>
                      <div class="body-copy">{sentence}</div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )

        if result.grounding_notes:
            st.markdown("#### Grounding notes")
            st.markdown(
                "".join(
                    f'<section class="note-card"><div class="body-copy">{note}</div></section>'
                    for note in result.grounding_notes
                ),
                unsafe_allow_html=True,
            )

    with analysis_tab:
        st.markdown("#### Scene observations")
        for observation in result.scene_observations:
            payload = observation_payload(observation)
            items = "".join(
                f"<li><strong>{label}:</strong> {value}</li>"
                for label, value in payload.items()
            )
            st.markdown(
                f"""
                <section class="observation-card">
                  <p class="label-chip">Image {observation.image_id}</p>
                  <ul>{items}</ul>
                </section>
                """,
                unsafe_allow_html=True,
            )

        if result.sequence_memory is not None:
            memory = result.sequence_memory
            st.markdown("#### Sequence memory")
            memory_items = [
                ("Recurring entities", ", ".join(memory.recurring_entities) or "No strong recurrence"),
                ("Setting progression", " -> ".join(memory.setting_progression) or "No progression recorded"),
                ("Event candidates", "; ".join(memory.event_candidates) or "No event chain recorded"),
                ("Unresolved ambiguities", "; ".join(memory.unresolved_ambiguities) or "No major ambiguity"),
            ]
            items = "".join(f"<li><strong>{label}:</strong> {value}</li>" for label, value in memory_items)
            st.markdown(
                f"""
                <section class="note-card">
                  <ul>{items}</ul>
                </section>
                """,
                unsafe_allow_html=True,
            )

        if result.narrative_plan is not None:
            plan = result.narrative_plan
            plan_items = [
                ("Arc type", plan.arc_type),
                ("Beat list", "; ".join(plan.beat_list) or "No beats recorded"),
                ("Allowed inferences", "; ".join(plan.allowed_inferences) or "None"),
                ("Forbidden claims", "; ".join(plan.forbidden_claims) or "None"),
            ]
            items = "".join(f"<li><strong>{label}:</strong> {value}</li>" for label, value in plan_items)
            st.markdown("#### Narrative plan")
            st.markdown(
                f"""
                <section class="note-card">
                  <ul>{items}</ul>
                </section>
                """,
                unsafe_allow_html=True,
            )

    with diagnostics_tab:
        report = result.evaluation_report
        if report is not None:
            st.markdown("#### Evaluator summary")
            st.markdown(
                f"""
                <section class="note-card">
                  <div class="body-copy">{report.summary}</div>
                </section>
                """,
                unsafe_allow_html=True,
            )
            if report.flags:
                st.warning("Active flags: " + "; ".join(report.flags))
            else:
                st.success("No evaluator flags were raised on the final draft.")
            if report.sentiment_audit is not None:
                audit = report.sentiment_audit
                st.markdown(
                    f"""
                    <section class="note-card">
                      <p class="label-chip">Sentiment audit</p>
                      <div class="body-copy">
                        Target: <strong>{audit.target_sentiment}</strong><br/>
                        Audit score: <strong>{audit.score:.2f}</strong><br/>
                        {audit.summary}
                      </div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )

        if result.provider_status:
            st.markdown("#### Provider execution trace")
            for status_item in result.provider_status:
                reason = status_item.reason or "Provider-backed execution"
                st.markdown(
                    f"""
                    <section class="note-card">
                      <p class="label-chip">{status_item.stage}</p>
                      <div class="body-copy">
                        Mode: <strong>{status_item.execution_mode}</strong><br/>
                        {reason}
                      </div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )

        if result.applied_overrides:
            st.markdown("#### Applied analysis overrides")
            st.json([override.model_dump(exclude_none=True) for override in result.applied_overrides])


def _render_status_card(status: StoryStatus) -> None:
    st.markdown(
        f"""
        <section class="status-card {status.state}">
          <p class="status-kicker">Story status</p>
          <span class="state-chip {status.state}">{status.label}</span>
          <h2 class="status-title">{status.title}</h2>
          <p class="status-copy">{status.reason}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_story_card(
    result: StoryResult,
    status: StoryStatus,
    active_source: dict[str, object],
) -> None:
    source_label = str(active_source["source_label"])
    fallback_notes = provider_fallback_notes(result)
    meta_parts = [
        f"Source: {source_label}",
        f"Sentiment: {st.session_state.sentiment}",
        f"Mode: {'Strict grounding' if st.session_state.strict_grounding else 'Default'}",
    ]
    if fallback_notes:
        meta_parts.append("Execution: local deterministic fallback")
    story_meta = " • ".join(meta_parts)
    st.markdown(
        f"""
        <section class="story-card">
          <p class="story-meta">{story_meta}</p>
          <h2 class="story-title">{result.title}</h2>
          <div class="story-body">{result.story_text}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _generate_story(active_source: dict[str, object], signature: tuple[object, ...]) -> None:
    image_paths = _pipeline_image_paths(active_source)
    if not image_paths:
        st.session_state.last_error = "Select a sample sequence or upload at least one image before generating."
        st.session_state.result = None
        st.session_state.status = StoryStatus(
            state="error",
            label="Blocked",
            title="Generation blocked",
            reason=st.session_state.last_error,
        )
        return

    st.session_state.last_error = None
    request = StoryRequest(
        image_paths=image_paths,
        sentiment=st.session_state.sentiment,
        max_sentences=int(st.session_state.max_sentences),
        include_debug=True,
        generation_mode=(
            STRICT_GROUNDING_GENERATION_MODE
            if st.session_state.strict_grounding
            else DEFAULT_GENERATION_MODE
        ),
    )
    cleanup_paths = image_paths if st.session_state.input_mode == "Upload images" else []
    try:
        with st.spinner("Analyzing images, linking the sequence, and writing the story..."):
            delay_seconds = float(os.environ.get("VISUAL_STORY_DEMO_DELAY_SECONDS", "0") or 0.0)
            if delay_seconds > 0:
                sleep(delay_seconds)
            result = get_pipeline().run(request)
    except Exception as exc:  # pragma: no cover - runtime safety surface
        st.session_state.last_error = str(exc)
        st.session_state.result = None
        st.session_state.status = StoryStatus(
            state="error",
            label="Error",
            title="Could not generate a story",
            reason=str(exc),
        )
    else:
        st.session_state.result = result
        st.session_state.status = classify_story_result(result)
        st.session_state.last_run_signature = signature
        st.session_state.last_run_meta = {
            "image_count": len(image_paths),
            "sentiment": st.session_state.sentiment,
            "source_label": active_source["source_label"],
        }
    finally:
        cleanup_persisted_images(cleanup_paths)


def _preview_items(active_source: dict[str, object]) -> list[dict[str, object]]:
    if active_source["mode"] == "Use included sample":
        return [
            {"image": str(path), "caption": f"Image {index}: {Path(path).stem.replace('_', ' ')}"}
            for index, path in enumerate(active_source["sample_paths"], start=1)
        ]

    uploaded_files = active_source["uploaded_files"]
    return [
        {"image": uploaded_file.getvalue(), "caption": f"Image {index}: {uploaded_file.name}"}
        for index, uploaded_file in enumerate(uploaded_files, start=1)
    ]


def _pipeline_image_paths(active_source: dict[str, object]) -> list[str]:
    if active_source["mode"] == "Use included sample":
        return [str(path) for path in active_source["sample_paths"]]
    return persist_uploaded_images(list(active_source["uploaded_files"]))


def _build_signature(active_source: dict[str, object]) -> tuple[object, ...]:
    if active_source["mode"] == "Use included sample":
        sequence_signature = tuple(str(path) for path in active_source["sample_paths"])
    else:
        sequence_signature = tuple(uploaded_file.name for uploaded_file in active_source["uploaded_files"])
    return (
        active_source["mode"],
        sequence_signature,
        st.session_state.sentiment,
        int(st.session_state.max_sentences),
        bool(st.session_state.strict_grounding),
    )


if __name__ == "__main__":
    main()
