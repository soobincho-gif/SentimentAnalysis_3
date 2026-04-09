from __future__ import annotations

import base64
import os
from typing import Any, Type, TypeVar

from pydantic import BaseModel

try:
    import instructor
    from openai import OpenAI
except ModuleNotFoundError:
    instructor = None
    OpenAI = None

T = TypeVar("T", bound=BaseModel)

MOCK_MODE_FALLBACK_REASON = "mock_mode"
MISSING_PROVIDER_SDK_FALLBACK_REASON = "missing_provider_sdk"
MISSING_API_KEY_FALLBACK_REASON = "missing_api_key"
PROVIDER_REQUEST_FAILED_FALLBACK_REASON = "provider_request_failed"


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class ProviderClient:
    """Handles external model calls using an instructor-wrapped client."""

    def __init__(self, use_mock: bool = False) -> None:
        self.use_mock = use_mock
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.has_provider_sdk = instructor is not None and OpenAI is not None
        self.is_configured = bool(self.api_key) and self.has_provider_sdk
        self.raw_client: Any | None = None
        self.client: Any | None = None
        self.last_request_used_fallback = False
        self.last_fallback_reason: str | None = None
        self.last_failure_message: str | None = None

        if self.has_provider_sdk:
            api_key = self.api_key or "mock-key-for-test"
            self.raw_client = OpenAI(api_key=api_key)
            self.client = instructor.from_openai(self.raw_client)

    def analyze_image(
        self,
        image_path: str,
        prompt: str,
        response_model: Type[T],
    ) -> T:
        self._reset_request_state()

        if self.use_mock:
            self._record_fallback(MOCK_MODE_FALLBACK_REASON)
            return self._mock_fallback(response_model)
        if not self.has_provider_sdk or self.client is None:
            self._record_fallback(MISSING_PROVIDER_SDK_FALLBACK_REASON)
            return self._mock_fallback(response_model)
        if not self.api_key:
            self._record_fallback(MISSING_API_KEY_FALLBACK_REASON)
            return self._mock_fallback(response_model)

        base64_image = encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]

        try:
            return self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=response_model,
                messages=messages,
                temperature=0.0,
            )
        except Exception as e:
            print(f"Provider connection error: {e}")
            self._record_fallback(PROVIDER_REQUEST_FAILED_FALLBACK_REASON, str(e))
            return self._mock_fallback(response_model)

    def generate_text(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str = "You are a grounded visual storyteller.",
        temperature: float = 0.3,
    ) -> T:
        self._reset_request_state()

        if self.use_mock:
            self._record_fallback(MOCK_MODE_FALLBACK_REASON)
            return self._mock_fallback(response_model)
        if not self.has_provider_sdk or self.client is None:
            self._record_fallback(MISSING_PROVIDER_SDK_FALLBACK_REASON)
            return self._mock_fallback(response_model)
        if not self.api_key:
            self._record_fallback(MISSING_API_KEY_FALLBACK_REASON)
            return self._mock_fallback(response_model)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            return self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=response_model,
                messages=messages,
                temperature=temperature,
            )
        except Exception as e:
            print(f"Provider connection error: {e}")
            self._record_fallback(PROVIDER_REQUEST_FAILED_FALLBACK_REASON, str(e))
            return self._mock_fallback(response_model)

    def describe_fallback(self, *, stage: str) -> str | None:
        reason = self.last_fallback_reason
        if reason is None:
            if self.use_mock:
                reason = MOCK_MODE_FALLBACK_REASON
            elif not self.has_provider_sdk or self.client is None:
                reason = MISSING_PROVIDER_SDK_FALLBACK_REASON
            elif not self.api_key:
                reason = MISSING_API_KEY_FALLBACK_REASON
        if reason is None:
            return None
        if reason == MOCK_MODE_FALLBACK_REASON:
            return f"Local fallback was used for {stage} because mock mode is active."
        if reason == MISSING_PROVIDER_SDK_FALLBACK_REASON:
            return (
                f"Local fallback was used for {stage} because the OpenAI provider SDK is unavailable "
                "in this environment."
            )
        if reason == MISSING_API_KEY_FALLBACK_REASON:
            return f"Local fallback was used for {stage} because OPENAI_API_KEY is not configured."
        if reason == PROVIDER_REQUEST_FAILED_FALLBACK_REASON:
            return (
                f"Local fallback was used for {stage} because the OpenAI provider request failed. "
                "Check network access and provider credentials."
            )
        return f"Local fallback was used for {stage}."

    def fallback_recovery_hint(self) -> str | None:
        reason = self.last_fallback_reason
        if reason is None:
            if self.use_mock:
                reason = MOCK_MODE_FALLBACK_REASON
            elif not self.has_provider_sdk or self.client is None:
                reason = MISSING_PROVIDER_SDK_FALLBACK_REASON
            elif not self.api_key:
                reason = MISSING_API_KEY_FALLBACK_REASON

        if reason == MOCK_MODE_FALLBACK_REASON:
            return "Disable mock mode to use the configured provider path."
        if reason == MISSING_PROVIDER_SDK_FALLBACK_REASON:
            return "Install the declared openai and instructor dependencies in this environment."
        if reason == MISSING_API_KEY_FALLBACK_REASON:
            return "Set OPENAI_API_KEY in the environment or .env file."
        if reason == PROVIDER_REQUEST_FAILED_FALLBACK_REASON:
            return "Check network access, provider credentials, and model availability, then retry."
        return None

    def status_payload(self, *, stage: str) -> dict[str, str | None]:
        reason = self.describe_fallback(stage=stage)
        if reason is None:
            return {
                "stage": stage,
                "execution_mode": "provider",
                "reason": None,
                "recovery_hint": None,
            }
        return {
            "stage": stage,
            "execution_mode": "local_fallback",
            "reason": reason,
            "recovery_hint": self.fallback_recovery_hint(),
        }

    def _reset_request_state(self) -> None:
        self.last_request_used_fallback = False
        self.last_fallback_reason = None
        self.last_failure_message = None

    def _record_fallback(self, reason: str, failure_message: str | None = None) -> None:
        self.last_request_used_fallback = True
        self.last_fallback_reason = reason
        self.last_failure_message = failure_message

    def _mock_fallback(self, response_model: Type[T]) -> T:
        """Graceful fallback behavior returning dummy schema data if requested or if network fails."""
        name = response_model.__name__
        if name == "SceneObservation":
            return response_model(
                image_id=1,
                entities=["shadowy figure"],
                setting="unknown location",
                objects=["small item"],
                actions=["moving"],
                visible_mood="neutral",
                text_in_image=[],
                uncertainty_notes=["MOCK DATA: Actual provider bypassed or failed."]
            )
        if name == "SequenceMemory":
            return response_model(
                recurring_entities=["shadowy figure"],
                setting_progression=["unknown location"],
                event_candidates=["a mock event occurs"],
                unresolved_ambiguities=["MOCK DATA: Fallback logic used"]
            )
        if name == "NarrativePlan":
            return response_model(
                arc_type="mock arc",
                beat_list=["mock beat 1"],
                sentence_image_map=[[1]],
                allowed_inferences=["mock inference"],
                forbidden_claims=["mock forbidden"],
                title_candidates=["Mock Plan"]
            )
        if name == "EvaluationReport":
            return response_model(
                grounding_score=0.9,
                coherence_score=0.9,
                redundancy_score=0.9,
                sentiment_fit_score=0.9,
                readability_score=0.9,
                flags=[],
                summary="MOCK DATA: Draft passes evaluation."
            )
        if name == "StoryDraft":
            return response_model(
                title="Mock Supported Story",
                story_text="This is a gracefully degraded mock story due to missing API keys or test mode.",
                sentence_alignment=[[1]],
                grounding_notes=["MOCK DATA: Provider fallback"]
            )

        # Generic fallback attempt using construct
        return response_model.model_construct()
