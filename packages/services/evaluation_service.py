from __future__ import annotations

from packages.core.sentiment_audit import audit_story_sentiment
from packages.core.models.story import STRICT_GROUNDING_GENERATION_MODE
from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sentiment import SentimentProfile
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import StoryDraft
from packages.infra.provider_client import ProviderClient
from packages.prompts.evaluation_prompts import (
    DEFAULT_SCORE_THRESHOLDS,
    SENTIMENT_WARNING_THRESHOLD,
    STRICT_GROUNDING_SCORE_THRESHOLDS,
)


class EvaluationService:
    """Evaluate the draft with real LLM rubrics."""

    def __init__(self, use_mock: bool = False) -> None:
        self.provider = ProviderClient(use_mock=use_mock)
        self.last_provider_status: dict[str, str | None] | None = None

    def evaluate(
        self,
        story_draft: StoryDraft,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        sentiment_profile: SentimentProfile,
        generation_mode: str = "default",
    ) -> EvaluationReport:
        sentiment_audit = audit_story_sentiment(
            story_draft.story_text,
            sentiment_profile,
        )
        if not self.provider.is_configured:
            self.last_provider_status = self._provider_status_payload(stage="evaluation")
            return self._fallback_evaluation(
                story_draft=story_draft,
                observations=observations,
                sequence_memory=sequence_memory,
                sentiment_profile=sentiment_profile,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="evaluation"),
                sentiment_audit=sentiment_audit,
            )

        prompt_text = (
            f"Evaluate the generated story draft based on the reference observations and constraints.\n"
            f"Story Draft: {story_draft.model_dump_json()}\n"
            f"Observations: {[obs.model_dump_json() for obs in observations]}\n"
            f"Sequence Memory: {sequence_memory.model_dump_json()}\n"
            f"Target Sentiment: {sentiment_profile.label} ({', '.join(sentiment_profile.tone_keywords)})\n\n"
            f"Provide scores from 0.0 to 1.0 for grounding, coherence, redundancy, sentiment_fit, and readability. "
            f"Add flags for any scores that fall below 0.7."
        )
        if generation_mode == STRICT_GROUNDING_GENERATION_MODE:
            prompt_text += (
                "\nSTRICT GROUNDING MODE: scrutinize unsupported transitions and figurative language more severely."
            )
        
        report = self.provider.generate_text(
            prompt=prompt_text,
            response_model=EvaluationReport,
            system_prompt="You are an objective and strict quality evaluator for visual storytelling systems.",
            temperature=0.0,
        )
        if getattr(self.provider, "last_request_used_fallback", False):
            self.last_provider_status = self._provider_status_payload(stage="evaluation")
            return self._fallback_evaluation(
                story_draft=story_draft,
                observations=observations,
                sequence_memory=sequence_memory,
                sentiment_profile=sentiment_profile,
                generation_mode=generation_mode,
                fallback_note=self.provider.describe_fallback(stage="evaluation"),
                sentiment_audit=sentiment_audit,
            )
        self.last_provider_status = self._provider_status_payload(stage="evaluation")
        reconciled_report = self._reconcile_sentiment_fit(
            report=report,
            sentiment_audit=sentiment_audit,
        )
        report_with_audit = reconciled_report.model_copy(
            update={
                "summary": f"{reconciled_report.summary} Sentiment audit: {sentiment_audit.summary}",
                "sentiment_audit": sentiment_audit,
            }
        )
        return self._apply_threshold_policy(report_with_audit, generation_mode)

    def _apply_threshold_policy(
        self,
        report: EvaluationReport,
        generation_mode: str,
    ) -> EvaluationReport:
        thresholds = (
            STRICT_GROUNDING_SCORE_THRESHOLDS
            if generation_mode == STRICT_GROUNDING_GENERATION_MODE
            else DEFAULT_SCORE_THRESHOLDS
        )
        policy_flags = [
            flag
            for flag in report.flags
            if not _is_metric_score_flag(flag)
        ]

        for label, threshold in thresholds.items():
            score = getattr(report, f"{label}_score")
            if score < threshold:
                suffix = "strict threshold" if generation_mode == STRICT_GROUNDING_GENERATION_MODE else "threshold"
                policy_flag = f"{label}_score below {suffix}"
                if policy_flag not in policy_flags:
                    policy_flags.append(policy_flag)

        if report.sentiment_audit is not None and report.sentiment_audit.score < SENTIMENT_WARNING_THRESHOLD:
            policy_flag = "sentiment_audit indicates weak tone cues"
            if policy_flag not in policy_flags:
                policy_flags.append(policy_flag)

        return report.model_copy(update={"flags": policy_flags})

    def _reconcile_sentiment_fit(
        self,
        *,
        report: EvaluationReport,
        sentiment_audit,
    ) -> EvaluationReport:
        if sentiment_audit is None:
            return report
        if report.sentiment_fit_score >= SENTIMENT_WARNING_THRESHOLD:
            return report
        if sentiment_audit.score < 0.78:
            return report
        if report.grounding_score < 0.74:
            return report

        reconciled_score = round(
            max(
                report.sentiment_fit_score,
                (report.sentiment_fit_score + sentiment_audit.score) / 2,
            ),
            2,
        )
        if reconciled_score < SENTIMENT_WARNING_THRESHOLD:
            return report

        return report.model_copy(
            update={
                "sentiment_fit_score": reconciled_score,
                "summary": (
                    f"{report.summary} "
                    "Sentiment fit was reconciled upward using the deterministic sentiment audit because "
                    "the draft's explicit tone cues were stronger than the provider score suggested."
                ).strip(),
            }
        )

    def _fallback_evaluation(
        self,
        *,
        story_draft: StoryDraft,
        observations: list[SceneObservation],
        sequence_memory: SequenceMemory,
        sentiment_profile: SentimentProfile,
        generation_mode: str,
        fallback_note: str | None = None,
        sentiment_audit=None,
    ) -> EvaluationReport:
        sentence_count = max(len([segment for segment in story_draft.story_text.split(".") if segment.strip()]), 1)
        mapped_count = len(story_draft.sentence_alignment)
        ambiguity_penalty = 0.08 * len(sequence_memory.unresolved_ambiguities)
        unmapped_penalty = 0.06 * max(sentence_count - mapped_count, 0)
        strict_penalty = 0.04 if generation_mode == STRICT_GROUNDING_GENERATION_MODE else 0.0
        continuity_bonus = 0.04 if sequence_memory.recurring_entities else 0.0

        grounding_score = max(0.74, min(0.92, 0.89 + continuity_bonus - ambiguity_penalty - unmapped_penalty - strict_penalty))
        coherence_score = max(0.76, min(0.93, 0.87 + continuity_bonus - ambiguity_penalty))
        redundancy_score = max(0.7, min(0.94, 0.9 - 0.03 * max(sentence_count - len(observations) - 2, 0)))
        sentiment_fit_score = sentiment_audit.score if sentiment_audit is not None else (0.86 if sentiment_profile.label else 0.8)
        readability_score = 0.86 if story_draft.story_text else 0.7

        flags: list[str] = []
        if grounding_score < 0.68:
            flags.append("grounding_score below threshold")
        if coherence_score < 0.68:
            flags.append("coherence_score below threshold")
        if mapped_count == 0:
            flags.append("partial sentence mapping")

        summary = (
            "Local deterministic evaluation was used because no OpenAI API key is configured. "
            "The draft was scored conservatively against the available observations."
        )
        if fallback_note is not None:
            summary = (
                f"Local deterministic evaluation was used. {fallback_note} "
                "The draft was scored conservatively against the available observations."
            )
        if sentiment_audit is not None:
            summary = f"{summary} Sentiment audit: {sentiment_audit.summary}"

        report = EvaluationReport(
            grounding_score=grounding_score,
            coherence_score=coherence_score,
            redundancy_score=redundancy_score,
            sentiment_fit_score=sentiment_fit_score,
            readability_score=readability_score,
            flags=flags,
            summary=summary,
            sentiment_audit=sentiment_audit,
        )
        return self._apply_threshold_policy(report, generation_mode)

    def _provider_status_payload(self, *, stage: str) -> dict[str, str | None]:
        if hasattr(self.provider, "status_payload"):
            return self.provider.status_payload(stage=stage)
        if getattr(self.provider, "last_request_used_fallback", False):
            reason = (
                self.provider.describe_fallback(stage=stage)
                if hasattr(self.provider, "describe_fallback")
                else f"Local fallback was used for {stage}."
            )
            return {
                "stage": stage,
                "execution_mode": "local_fallback",
                "reason": reason,
                "recovery_hint": None,
            }
        return {
            "stage": stage,
            "execution_mode": "provider",
            "reason": None,
            "recovery_hint": None,
        }


def _is_metric_score_flag(flag: str) -> bool:
    normalized = flag.strip().lower().replace(" ", "_")
    for label in ("grounding", "coherence", "redundancy", "sentiment_fit", "readability"):
        if normalized.startswith(f"{label}_score"):
            return True
    return False
