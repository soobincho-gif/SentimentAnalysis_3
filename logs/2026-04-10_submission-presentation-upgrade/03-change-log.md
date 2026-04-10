# 2026-04-10 Submission Presentation Upgrade

## Scope

- raise the repository from implementation-ready to submission-ready presentation quality,
- add a deployable Streamlit surface,
- create organized sample assets and screenshot evidence,
- produce a polished notebook artifact in `submission_package/`.

## What changed

- rewrote the top-level `README.md` into a product-facing document with architecture, screenshots, deployment notes, repository structure, expected outputs, and sample-result explanations
- added `streamlit_app.py` and the `apps/web/` Streamlit presentation layer
- added `.streamlit/config.toml` and Streamlit dependencies for deployment readiness
- extended upload persistence so the Streamlit UI can safely persist uploaded file buffers into pipeline-ready temp files
- created reusable raw sample image sets, example run artifacts, screenshots, and an architecture diagram under `assets/`
- created `submission_package/실습3_조수빈.ipynb` with saved outputs and result evidence

## Verification

- `python -m compileall apps/web packages/infra tests/apps tests/infra streamlit_app.py`
- `pytest -q tests/apps/test_streamlit_presenter.py tests/infra/test_upload_persistence.py`
- local Streamlit smoke checks for:
  - idle workspace
  - generation in progress
  - successful generation result
  - low-confidence fallback result
  - blocked input state

## Remaining blocker

The repository is ready for Streamlit Community Cloud, but the permanent hosted deployment still depends on repo-owner authentication in the Streamlit Cloud dashboard. A temporary live preview link is available while the local Streamlit session remains active, and both the README and notebook mark that preview as temporary.
