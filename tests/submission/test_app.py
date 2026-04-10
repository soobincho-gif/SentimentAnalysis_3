from __future__ import annotations

from submission.app import SENTIMENT_OPTIONS, build_ui
from submission.styles import APP_CSS, APP_HEAD


def test_build_ui_constructs_without_error() -> None:
    demo = build_ui()

    assert demo is not None


def test_file_input_disables_reordering_and_resets_workspace_on_change() -> None:
    demo = build_ui()
    file_component = next(
        component for component in demo.config["components"] if component.get("type") == "file"
    )
    file_id = file_component["id"]
    target_events = [
        target
        for dependency in demo.config["dependencies"]
        for target in dependency.get("targets", [])
        if target[0] == file_id
    ]

    assert file_component["props"]["allow_reordering"] is False
    assert (file_id, "change") in target_events


def test_generate_actions_scroll_to_output_for_story_visibility() -> None:
    demo = build_ui()
    components_by_id = {component["id"]: component for component in demo.config["components"]}
    generate_actions = [
        dependency
        for dependency in demo.config["dependencies"]
        if any(
            components_by_id.get(target[0], {}).get("props", {}).get("elem_id")
            in {
                "generate-button",
                "regenerate-button",
                "strict-regenerate-button",
                "corrected-generate-button",
                "corrected-strict-generate-button",
            }
            for target in dependency.get("targets", [])
        )
    ]

    assert len(generate_actions) == 5
    assert all(action["scroll_to_output"] is True for action in generate_actions)


def test_sentiment_options_keep_expected_order_for_icon_styling() -> None:
    assert SENTIMENT_OPTIONS == [
        "happy",
        "sad",
        "suspenseful",
        "mysterious",
        "heartwarming",
        "playful",
    ]


def test_app_css_includes_sentiment_icon_rules() -> None:
    assert '#sentiment-choices label:nth-of-type(1)::before' in APP_CSS
    assert '#sentiment-choices label:nth-of-type(6)::before' in APP_CSS
    assert '#sentiment-choices input[type="radio"]' in APP_CSS
    assert "accent-color: var(--sentiment-accent);" in APP_CSS
    assert "--sentiment-playful-soft" in APP_CSS
    assert "--checkbox-label-border-color: var(--story-border);" in APP_CSS
    assert "--checkbox-label-background-fill-selected: var(--sentiment-soft);" in APP_CSS
    assert "#sentiment-choices label.selected" in APP_CSS
    assert "background: var(--sentiment-soft) !important;" in APP_CSS
    assert "background-color: var(--sentiment-soft) !important;" in APP_CSS
    assert "box-shadow: inset 0 0 0 999px var(--sentiment-soft)" in APP_CSS
    assert "outline: 1px solid var(--sentiment-accent) !important;" in APP_CSS
    assert "#sentiment-choices label.selected:nth-of-type(2)" in APP_CSS
    assert "background: #dbeafe !important;" in APP_CSS
    assert "box-shadow: inset 0 0 0 999px #dbeafe" in APP_CSS


def test_app_css_includes_fullscreen_layout_guards() -> None:
    assert "width: 100% !important;" in APP_CSS
    assert "max-width: 1680px !important;" in APP_CSS
    assert ".gradio-container .main.fillable.app" in APP_CSS
    assert ".visually-hidden" in APP_CSS
    assert '[data-testid="status-tracker"]' in APP_CSS
    assert ".thumb-strip" in APP_CSS
    assert "@media (max-width: 1280px)" in APP_CSS
    assert "@media (min-width: 1281px)" in APP_CSS
    assert "flex-wrap: wrap !important;" in APP_CSS
    assert "@media (max-width: 640px)" in APP_CSS


def test_app_shell_forces_light_mode_even_when_browser_prefers_dark() -> None:
    assert APP_HEAD == ""
    assert "body.dark" in APP_CSS
    assert "footer" in APP_CSS
    assert "body.story-busy::after" in APP_CSS


def test_app_css_keeps_native_upload_rows_readable_without_global_overrides() -> None:
    assert "--block-background-fill: #fffaf2 !important;" in APP_CSS
    assert '.gradio-container .file-preview tr.file:nth-child(odd)' in APP_CSS
    assert '.gradio-container .file-preview .label-clear-button' in APP_CSS
    assert '.panel-card .styler' in APP_CSS
    assert '.gradio-container [data-testid="file-upload"]' not in APP_CSS
    assert '.gradio-container button {' not in APP_CSS
    assert '.gradio-container [data-testid="file-upload"] *' not in APP_CSS


def test_app_css_strengthens_tab_active_state_and_action_hierarchy() -> None:
    assert '#results-tabs [role="tab"][aria-selected="true"]' in APP_CSS
    assert "box-shadow: 0 12px 20px rgba(77, 60, 43, 0.1), inset 0 -2px 0 var(--story-accent) !important;" in APP_CSS
    assert ".primary-action-label" in APP_CSS
    assert ".action-group-label" in APP_CSS
    assert ".primary-cta-button" in APP_CSS
    assert ".followup-button" in APP_CSS
    assert ".advanced-button" in APP_CSS
    assert "#generate-button:hover:not(:disabled)" in APP_CSS


def test_app_avoids_custom_head_runtime_that_can_block_gradio_hydration() -> None:
    assert APP_HEAD == ""
