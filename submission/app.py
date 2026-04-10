from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

# Make repo root importable when running: python submission/app.py
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv()

from packages.prompts.sentiment_profiles import SUPPORTED_SENTIMENT_LABELS  # noqa: E402
from submission.controller import (  # noqa: E402
    KEEP_CONTINUITY,
    clear_all_corrections,
    clear_analysis_correction,
    continuity_choice_value,
    deserialize_observations,
    deserialize_overrides,
    initial_correction_status,
    reset_workspace_for_images,
    save_analysis_correction,
    stream_generate_default_story,
    stream_generate_from_corrected_analysis,
    stream_generate_from_corrected_analysis_strict,
    stream_generate_strict_story,
    stream_regenerate_story,
    update_generation_controls,
)
from submission.presentation import (  # noqa: E402
    present_action_guidance,
    present_empty_analysis_editor,
    present_initial_outputs,
    present_sequence_preview,
    render_observation_editor_card,
)
from submission.styles import APP_CSS, APP_HEAD  # noqa: E402

SENTIMENT_OPTIONS = list(SUPPORTED_SENTIMENT_LABELS)


def build_ui() -> gr.Blocks:
    initial_outputs = present_initial_outputs()
    initial_action_guidance = present_action_guidance(
        has_images=False,
        has_previous_run=False,
        has_corrections=False,
        sentence_error=None,
    )

    with gr.Blocks(title="Visual Storytelling", fill_width=True) as demo:
        gr.HTML(
            """
            <section class="studio-shell">
              <div class="studio-header">
                <p class="studio-kicker">Grounded visual storytelling</p>
                <h1>Visual Storytelling from Images + Sentiment</h1>
                <p>
                  Arrange a sequence of images, choose the emotional tone, and review a
                  confidence-first story that keeps its evidence visible.
                </p>
              </div>
            </section>
            """
        )

        observation_state = gr.State([])
        original_observation_state = gr.State([])
        correction_state = gr.State([])
        run_snapshot_state = gr.State(None)
        uploaded_image_state = gr.State([])

        with gr.Row(equal_height=False, elem_classes=["workspace-row"]):
            with gr.Column(scale=5, elem_classes=["workspace-column", "workspace-input-column"]):
                with gr.Group(elem_classes=["panel-card", "input-panel"]):
                    gr.HTML(
                        """
                        <h2 class="section-title">Build the sequence</h2>
                        <p class="section-copy">
                          Upload the frames you want to connect. You can reorder them before generation.
                        </p>
                        """
                    )
                    image_input = gr.File(
                        file_count="multiple",
                        file_types=["image"],
                        type="filepath",
                        label="Upload images",
                    )
                    sentiment_input = gr.Radio(
                        choices=SENTIMENT_OPTIONS,
                        value="happy",
                        label="Sentiment",
                        info="Tone shapes style, not facts.",
                        elem_id="sentiment-choices",
                    )
                    max_sentences_input = gr.Number(
                        value=5,
                        minimum=1,
                        step=1,
                        precision=0,
                        label="Max sentences",
                        info="Use any positive number. The model may still stop earlier if the image evidence runs out.",
                    )
                    gr.HTML('<p class="primary-action-label">Main action</p>')
                    generate_button = gr.Button(
                        "Generate Story",
                        variant="primary",
                        elem_id="generate-button",
                        elem_classes=["primary-cta-button"],
                        interactive=False,
                    )
                    gr.HTML('<div id="sequence-helper">Story follows image order</div>')
                    sequence_preview_output = gr.HTML(value=present_sequence_preview([]))

            with gr.Column(scale=7, elem_classes=["workspace-column", "workspace-result-column"]):
                with gr.Group(elem_classes=["panel-card", "result-panel"]):
                    status_output = gr.HTML(value=initial_outputs.status_html)
                    gr.HTML('<p class="action-group-label">Optional follow-up</p>')
                    with gr.Row(elem_classes=["action-row", "followup-row"]):
                        regenerate_button = gr.Button(
                            "Regenerate",
                            variant="secondary",
                            elem_id="regenerate-button",
                            elem_classes=["followup-button"],
                            interactive=False,
                        )
                        strict_regenerate_button = gr.Button(
                            "Regenerate with stricter grounding",
                            variant="secondary",
                            elem_id="strict-regenerate-button",
                            elem_classes=["followup-button"],
                            interactive=False,
                        )
                    gr.HTML(
                        '<p class="action-group-label action-group-label-muted">'
                        "Advanced: uses saved Analysis corrections"
                        "</p>"
                    )
                    with gr.Row(elem_classes=["action-row", "advanced-row"]):
                        corrected_generate_button = gr.Button(
                            "Generate from corrected analysis",
                            variant="secondary",
                            elem_id="corrected-generate-button",
                            elem_classes=["advanced-button"],
                            interactive=False,
                        )
                        corrected_strict_generate_button = gr.Button(
                            "Corrected analysis + stricter grounding",
                            variant="secondary",
                            elem_id="corrected-strict-generate-button",
                            elem_classes=["advanced-button"],
                            interactive=False,
                        )
                    action_guidance_output = gr.HTML(value=initial_action_guidance)
                    with gr.Tabs(elem_id="results-tabs"):
                        with gr.Tab("Story"):
                            story_output = gr.HTML(value=initial_outputs.story_html)
                        with gr.Tab("Analysis"):
                            analysis_output = gr.HTML(value=initial_outputs.analysis_html)
                            correction_status_output = gr.HTML(value=initial_correction_status())
                            clear_corrections_button = gr.Button(
                                "Clear all saved corrections",
                                variant="secondary",
                                elem_id="clear-corrections-button",
                                elem_classes=["quiet-button"],
                            )

                            @gr.render(
                                inputs=[
                                    original_observation_state,
                                    observation_state,
                                    correction_state,
                                    uploaded_image_state,
                                ]
                            )
                            def render_analysis_editor(
                                original_observation_payload: list[dict],
                                observation_payload: list[dict],
                                correction_payload: list[dict],
                                uploaded_images: list[str] | None,
                            ) -> None:
                                original_observations = deserialize_observations(original_observation_payload)
                                observations = deserialize_observations(observation_payload)
                                overrides = {
                                    override.image_id: override
                                    for override in deserialize_overrides(correction_payload)
                                }
                                image_paths = list(uploaded_images or [])

                                if not observations or not original_observations:
                                    gr.HTML(present_empty_analysis_editor())
                                    return

                                for original_observation, observation in zip(
                                    original_observations,
                                    observations,
                                    strict=False,
                                ):
                                    image_id_state = gr.State(observation.image_id)
                                    image_path = (
                                        image_paths[observation.image_id - 1]
                                        if observation.image_id <= len(image_paths)
                                        else None
                                    )
                                    active_override = overrides.get(observation.image_id)

                                    with gr.Group(elem_classes=["analysis-editor-card"]):
                                        gr.HTML(
                                            render_observation_editor_card(
                                                original_observation,
                                                observation,
                                                image_path=image_path,
                                                active_override=active_override,
                                            )
                                        )
                                        with gr.Row():
                                            subject_input = gr.Textbox(
                                                label="Correct main subject",
                                                value=active_override.main_entity if active_override else "",
                                                placeholder=observation.entities[0] if observation.entities else "e.g. small brown dog",
                                            )
                                            setting_input = gr.Textbox(
                                                label="Correct setting",
                                                value=active_override.setting if active_override else "",
                                                placeholder=observation.setting or "e.g. cafe interior",
                                            )
                                        with gr.Row():
                                            action_input = gr.Textbox(
                                                label="Correct visible action",
                                                value=active_override.visible_action if active_override else "",
                                                placeholder=observation.actions[0] if observation.actions else "e.g. holding a cup",
                                            )
                                            continuity_input = gr.Radio(
                                                choices=[
                                                    ("Keep current", KEEP_CONTINUITY),
                                                    ("Same as previous image", "same"),
                                                    ("Different from previous image", "different"),
                                                ],
                                                value=continuity_choice_value(
                                                    active_override.same_subject_as_previous
                                                    if active_override is not None
                                                    else None
                                                ),
                                                label="Same subject as previous?",
                                            )
                                        generation_note_input = gr.Textbox(
                                            label="Optional note for generation",
                                            value=active_override.generation_note if active_override else "",
                                            lines=2,
                                            placeholder="Only if you want the next corrected generation to keep a short, explicit constraint.",
                                        )
                                        with gr.Row():
                                            save_button = gr.Button(
                                                "Save correction",
                                                variant="secondary",
                                            )
                                            clear_button = gr.Button(
                                                "Clear saved correction",
                                                variant="secondary",
                                            )

                                        save_button.click(
                                            fn=save_analysis_correction,
                                            inputs=[
                                                original_observation_state,
                                                correction_state,
                                                image_id_state,
                                                subject_input,
                                                setting_input,
                                                action_input,
                                                continuity_input,
                                                generation_note_input,
                                            ],
                                            outputs=[
                                                correction_state,
                                                observation_state,
                                                correction_status_output,
                                            ],
                                            queue=False,
                                            show_progress="hidden",
                                        ).then(
                                            fn=update_generation_controls,
                                            inputs=[
                                                uploaded_image_state,
                                                correction_state,
                                                run_snapshot_state,
                                                max_sentences_input,
                                            ],
                                            outputs=[
                                                generate_button,
                                                regenerate_button,
                                                strict_regenerate_button,
                                                corrected_generate_button,
                                                corrected_strict_generate_button,
                                                action_guidance_output,
                                            ],
                                            queue=False,
                                            show_progress="hidden",
                                        )
                                        clear_button.click(
                                            fn=clear_analysis_correction,
                                            inputs=[
                                                original_observation_state,
                                                correction_state,
                                                image_id_state,
                                            ],
                                            outputs=[
                                                correction_state,
                                                observation_state,
                                                correction_status_output,
                                            ],
                                            queue=False,
                                            show_progress="hidden",
                                        ).then(
                                            fn=update_generation_controls,
                                            inputs=[
                                                uploaded_image_state,
                                                correction_state,
                                                run_snapshot_state,
                                                max_sentences_input,
                                            ],
                                            outputs=[
                                                generate_button,
                                                regenerate_button,
                                                strict_regenerate_button,
                                                corrected_generate_button,
                                                corrected_strict_generate_button,
                                                action_guidance_output,
                                            ],
                                            queue=False,
                                            show_progress="hidden",
                                        )

                        with gr.Tab("Diagnostics"):
                            diagnostics_output = gr.HTML(value=initial_outputs.diagnostics_html)

        clear_corrections_button.click(
            fn=clear_all_corrections,
            inputs=[original_observation_state],
            outputs=[correction_state, observation_state, correction_status_output],
            queue=False,
            show_progress="hidden",
        ).then(
            fn=update_generation_controls,
            inputs=[
                uploaded_image_state,
                correction_state,
                run_snapshot_state,
                max_sentences_input,
            ],
            outputs=[
                generate_button,
                regenerate_button,
                strict_regenerate_button,
                corrected_generate_button,
                corrected_strict_generate_button,
                action_guidance_output,
            ],
            queue=False,
            show_progress="hidden",
        )

        image_input.change(
            fn=reset_workspace_for_images,
            inputs=[image_input],
            outputs=[
                sequence_preview_output,
                status_output,
                story_output,
                analysis_output,
                diagnostics_output,
                observation_state,
                original_observation_state,
                correction_state,
                correction_status_output,
                uploaded_image_state,
                run_snapshot_state,
            ],
            queue=False,
            show_progress="hidden",
        ).then(
            fn=update_generation_controls,
            inputs=[
                uploaded_image_state,
                correction_state,
                run_snapshot_state,
                max_sentences_input,
            ],
            outputs=[
                generate_button,
                regenerate_button,
                strict_regenerate_button,
                corrected_generate_button,
                corrected_strict_generate_button,
                action_guidance_output,
            ],
            queue=False,
            show_progress="hidden",
        )

        max_sentences_input.change(
            fn=update_generation_controls,
            inputs=[
                uploaded_image_state,
                correction_state,
                run_snapshot_state,
                max_sentences_input,
            ],
            outputs=[
                generate_button,
                regenerate_button,
                strict_regenerate_button,
                corrected_generate_button,
                corrected_strict_generate_button,
                action_guidance_output,
            ],
            queue=False,
            show_progress="hidden",
        )

        generation_outputs = [
            status_output,
            story_output,
            analysis_output,
            diagnostics_output,
            observation_state,
            original_observation_state,
            correction_status_output,
            run_snapshot_state,
            generate_button,
            regenerate_button,
            strict_regenerate_button,
            corrected_generate_button,
            corrected_strict_generate_button,
            action_guidance_output,
        ]

        generation_inputs = [
            image_input,
            sentiment_input,
            max_sentences_input,
            correction_state,
            run_snapshot_state,
            story_output,
            analysis_output,
            diagnostics_output,
            observation_state,
            original_observation_state,
            correction_status_output,
        ]

        for button, handler in [
            (generate_button, stream_generate_default_story),
            (regenerate_button, stream_regenerate_story),
            (strict_regenerate_button, stream_generate_strict_story),
            (corrected_generate_button, stream_generate_from_corrected_analysis),
        ]:
            button.click(
                fn=handler,
                inputs=generation_inputs,
                outputs=generation_outputs,
                queue=True,
                show_progress="hidden",
                scroll_to_output=True,
            )

        corrected_strict_generate_button.click(
            fn=stream_generate_from_corrected_analysis_strict,
            inputs=generation_inputs,
            outputs=generation_outputs,
            queue=True,
            show_progress="hidden",
            scroll_to_output=True,
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(css=APP_CSS, head=APP_HEAD, footer_links=[])
