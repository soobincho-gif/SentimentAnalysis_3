# Change Log

- Failure type: `SENTIMENT_MISMATCH`
- Verification scope:
  - provider-backed sentiment quality on a synthetic 3-image storyboard
  - runtime log inspection under `logs/runtime/2026-04-09_sentiment_runs.jsonl`
  - browser UI smoke at narrow width for upload and generate request dispatch
- Findings:
  - provider mode is active when the app loads `.env`; recent verification runs recorded only `provider` execution modes in runtime logs
  - `is_fallback=true` in the runtime log means the draft hit the revision limit with remaining flags; it does not necessarily mean the OpenAI provider path fell back to local execution
  - `happy` and `heartwarming` now audit as clearly expressed after the deterministic sentiment-audit alias expansion
  - `suspenseful` remains weak on the tested park storyboard because the model tends to drift into moodier language without sustaining enough grounded suspense cues
  - narrow-width UI stacks correctly and browser automation confirmed upload plus `POST /gradio_api/run/predict` dispatch from `Generate Story`
- Evidence snippets:
  - `2026-04-09T05:53:25Z happy`: `sentiment_fit=0.75`, `audit_score=0.91`, modes=`provider`
  - `2026-04-09T05:53:49Z heartwarming`: `sentiment_fit=0.75`, `audit_score=0.99`, modes=`provider`
  - `2026-04-09T05:54:12Z suspenseful`: `sentiment_fit=0.65`, `audit_score=0.59`, modes=`provider`
  - browser smoke at 760px saw the input column at `y=331` and result column at `y=1530`, confirming stacked layout, and captured a real `POST /gradio_api/run/predict` after clicking `Generate Story`
- Remaining risk:
  - the provider-backed UI render path is slower than the backend-only verification path, so a full headless browser round-trip can outlast a short smoke window even when request dispatch is healthy
