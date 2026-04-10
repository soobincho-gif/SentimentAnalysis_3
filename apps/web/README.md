# Web App

`apps/web` now hosts the Streamlit presentation layer for the visual storytelling system.

## Current entrypoints

- [`streamlit_app.py`](/Users/sarahc/Downloads/SentimentAnalysis_3/streamlit_app.py): repository-root Streamlit Cloud entrypoint
- [`apps/web/streamlit_app.py`](/Users/sarahc/Downloads/SentimentAnalysis_3/apps/web/streamlit_app.py): main Streamlit workspace implementation
- [`apps/web/streamlit_presenter.py`](/Users/sarahc/Downloads/SentimentAnalysis_3/apps/web/streamlit_presenter.py): UI-only presentation helpers for confidence state, story maps, and observation formatting

## Scope

The Streamlit app is responsible for:

- collecting ordered image input,
- exposing the supported sentiment choices,
- calling the shared storytelling pipeline,
- rendering the story, diagnostics, and intermediate trace data,
- surfacing confidence and fallback states clearly.

## Boundary

This layer stays presentation-only.

It may:

- choose layout,
- format results for readability,
- manage lightweight UI state,
- offer built-in sample sequences for demonstration.

It may not:

- redefine grounding rules,
- embed prompt text,
- duplicate sequence reasoning logic,
- replace the shared service pipeline.
