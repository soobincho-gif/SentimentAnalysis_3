# Change Log

- Failure type: `SENTIMENT_MISMATCH`
- Verification scope:
  - provider-backed quality review for `sad`, `mysterious`, and `playful`
  - sentiment-specific prompt guidance for non-suspense sentiments
  - deterministic audit alias expansion for provider-style language
- Findings:
  - `sad` now performs reliably on the park storyboard with a reflective, bittersweet tone and a strong audit trace
  - `playful` now produces clearer lively/energetic wording and the audit no longer under-credits common provider wording such as `fun`, `laughter`, `delightful`, and `joyful`
  - `mysterious` audit mismatch improved substantially after alias expansion, but provider-side `sentiment_fit` still varies run to run even when the deterministic audit reads the draft as on-tone
- Evidence snippets:
  - focused regression: `pytest -q tests/contracts/test_sentiment_audit.py tests/services/test_generation_modes.py tests/submission/test_presentation.py` -> `31 passed`
  - full regression: `pytest -q` -> `81 passed`
  - `2026-04-09T06:46:24Z sad`: `sentiment_fit=0.85`, `audit_score=0.99`
  - `2026-04-09T06:47:22Z playful`: `sentiment_fit=0.85`, `audit_score=0.82`
  - latest provider-backed `mysterious` probe after alias tuning: `sentiment_fit=0.60`, `audit_score=0.89`
- Remaining risk:
  - `mysterious` and `suspenseful` still have the largest evaluator/generation mismatch on gentle park scenes, so the current system is more inspectable and better tuned but not yet fully stable for every sentiment-storyboard pairing
