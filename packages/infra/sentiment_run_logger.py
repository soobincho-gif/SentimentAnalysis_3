from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from packages.core.models.sentiment import SentimentProfile
from packages.core.models.story import StoryRequest, StoryResult


class SentimentRunLogger:
    """Persist one JSONL record per generation run for sentiment traceability."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        if log_dir is None:
            log_dir = os.environ.get("VISUAL_STORY_LOG_DIR")
        self.log_dir = (
            Path(log_dir)
            if log_dir is not None
            else Path(__file__).resolve().parents[2] / "logs" / "runtime"
        )

    def record(
        self,
        *,
        request: StoryRequest,
        sentiment_profile: SentimentProfile,
        result: StoryResult,
    ) -> Path:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_sentiment_runs.jsonl"

        evaluation = result.evaluation_report
        payload = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "request": {
                "sentiment": request.sentiment,
                "generation_mode": request.generation_mode,
                "image_count": len(request.image_paths),
                "max_sentences": request.max_sentences,
                "override_count": len(request.analysis_overrides),
            },
            "sentiment_profile": sentiment_profile.model_dump(mode="json"),
            "story": {
                "title": result.title,
                "text": result.story_text,
                "sentence_alignment": result.sentence_alignment,
            },
            "evaluation": (
                {
                    "grounding_score": evaluation.grounding_score,
                    "coherence_score": evaluation.coherence_score,
                    "redundancy_score": evaluation.redundancy_score,
                    "sentiment_fit_score": evaluation.sentiment_fit_score,
                    "readability_score": evaluation.readability_score,
                    "flags": evaluation.flags,
                    "summary": evaluation.summary,
                    "sentiment_audit": (
                        evaluation.sentiment_audit.model_dump(mode="json")
                        if evaluation.sentiment_audit is not None
                        else None
                    ),
                }
                if evaluation is not None
                else None
            ),
            "provider_status": [
                status.model_dump(mode="json") for status in result.provider_status
            ],
            "revision_attempts": result.revision_attempts,
            "revision_limit_reached": result.is_fallback,
            "is_fallback": result.is_fallback,
        }

        with log_path.open("a", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True)
            handle.write("\n")

        return log_path
