from __future__ import annotations

import os
from pathlib import Path

import pytest

from packages.core.models.scene import SceneObservation
from packages.core.models.story import StoryDraft
import packages.infra.provider_client as provider_client_module
from packages.infra.provider_client import ProviderClient


def test_provider_client_mock_boundary() -> None:
    client = ProviderClient(use_mock=True)
    
    # Test SceneObservation mock/fallback
    scene = client.analyze_image("/fake/path.png", "prompt", SceneObservation)
    assert isinstance(scene, SceneObservation)
    assert scene.image_id == 1
    assert "shadowy figure" in scene.entities
    
    # Test StoryDraft mock/fallback
    draft = client.generate_text("prompt", StoryDraft)
    assert isinstance(draft, StoryDraft)
    assert draft.title == "Mock Supported Story"

def test_provider_client_real_fallback_on_network_error(tmp_path: Path) -> None:
    # Set a bogus key so real client fails and falls back
    os.environ["OPENAI_API_KEY"] = "bogus-key-for-testing"
    client = ProviderClient(use_mock=False)
    
    # Create dummy image to pass encode_image
    image_path = tmp_path / "dummy.png"
    image_path.write_bytes(b"dummy content")
    
    # Test SceneObservation mock/fallback triggered by network fail
    scene = client.analyze_image(str(image_path), "prompt", SceneObservation)  
    # Exception will be caught, fallback invoked
    assert isinstance(scene, SceneObservation)
    assert scene.image_id == 1


def test_provider_client_missing_sdk_gracefully_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    monkeypatch.setattr(provider_client_module, "instructor", None)
    monkeypatch.setattr(provider_client_module, "OpenAI", None)

    client = provider_client_module.ProviderClient(use_mock=False)

    assert client.is_configured is False

    draft = client.generate_text("prompt", StoryDraft)

    assert isinstance(draft, StoryDraft)
    assert draft.title == "Mock Supported Story"
