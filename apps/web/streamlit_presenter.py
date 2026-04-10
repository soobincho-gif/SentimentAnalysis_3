from __future__ import annotations

from dataclasses import dataclass
import re

from packages.core.models.scene import SceneObservation
from packages.core.models.story import StoryResult


@dataclass(frozen=True)
class StoryStatus:
    state: str
    label: str
    title: str
    reason: str


def classify_story_result(result: StoryResult) -> StoryStatus:
    report = result.evaluation_report
    flags = report.flags if report is not None else []
    grounding_score = report.grounding_score if report is not None else 0.0
    coherence_score = report.coherence_score if report is not None else 0.0
    fallback_notes = provider_fallback_notes(result)
    ambiguities = (
        result.sequence_memory.unresolved_ambiguities
        if result.sequence_memory is not None
        else []
    )

    if (
        result.is_fallback
        or grounding_score < 0.70
        or coherence_score < 0.70
        or len(flags) >= 2
        or (fallback_notes and len(ambiguities) >= 2)
    ):
        return StoryStatus(
            state="low-confidence",
            label="Low confidence",
            title="Draft kept visible with warnings",
            reason=_primary_reason(result, flags, ambiguities, fallback_notes),
        )

    if fallback_notes or flags or ambiguities or result.revision_attempts > 0:
        return StoryStatus(
            state="caution",
            label="Cautious draft",
            title="Grounded draft with active caveats",
            reason=_primary_reason(result, flags, ambiguities, fallback_notes),
        )

    return StoryStatus(
        state="good",
        label="Story ready",
        title="Story ready",
        reason="The draft passed evaluation without unresolved ambiguity or fallback warnings.",
    )


def provider_fallback_notes(result: StoryResult) -> list[str]:
    return [
        status.reason
        for status in result.provider_status
        if status.execution_mode == "local_fallback" and status.reason
    ]


def metric_rows(result: StoryResult) -> list[tuple[str, float]]:
    report = result.evaluation_report
    if report is None:
        return []
    return [
        ("Grounding", report.grounding_score),
        ("Coherence", report.coherence_score),
        ("Redundancy", report.redundancy_score),
        ("Sentiment fit", report.sentiment_fit_score),
        ("Readability", report.readability_score),
    ]


def story_map_rows(result: StoryResult) -> list[tuple[str, list[int]]]:
    sentences = _split_story_sentences(result.story_text)
    if not sentences:
        return []
    alignments = result.sentence_alignment or []
    rows: list[tuple[str, list[int]]] = []
    for index, sentence in enumerate(sentences):
        mapped_images = alignments[index] if index < len(alignments) else []
        rows.append((sentence, mapped_images))
    return rows


def observation_payload(observation: SceneObservation) -> dict[str, str]:
    return {
        "Entities": ", ".join(observation.entities) or "No strong entity cue",
        "Setting": observation.setting or "Unresolved setting",
        "Actions": ", ".join(observation.actions) or "No explicit action cue",
        "Objects": ", ".join(observation.objects) or "No notable objects",
        "Visible mood": observation.visible_mood or "Neutral",
        "Continuity": _continuity_label(observation.same_subject_as_previous),
        "Uncertainty": ", ".join(observation.uncertainty_notes) or "No additional uncertainty notes",
    }


def _continuity_label(value: bool | None) -> str:
    if value is True:
        return "Same subject as previous image"
    if value is False:
        return "Different subject from previous image"
    return "Not explicitly confirmed"


def _split_story_sentences(story_text: str) -> list[str]:
    stripped = story_text.strip()
    if not stripped:
        return []
    fragments = re.split(r"(?<=[.!?])\s+", stripped)
    return [fragment.strip() for fragment in fragments if fragment.strip()]


def _primary_reason(
    result: StoryResult,
    flags: list[str],
    ambiguities: list[str],
    fallback_notes: list[str],
) -> str:
    if result.is_fallback:
        return (
            "The revision limit was reached before the system could clear all quality checks, "
            "so this story stays visible as a draft."
        )
    if fallback_notes:
        return fallback_notes[0]
    if flags:
        return f"Evaluator warning: {_format_flag(flags[0])}."
    if ambiguities:
        return ambiguities[0]
    if result.revision_attempts > 0:
        return "The first draft needed revision before it was safe enough to show."
    return "The draft carries mild uncertainty even though the main story remains readable."


def _format_flag(flag: str) -> str:
    return flag.replace("_", " ")
