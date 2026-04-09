# Change Log

- Failure type: `SENTIMENT_MISMATCH`
- Verification scope:
  - suspenseful-only prompt tuning for provider-backed story generation
  - revision prompt grounding reinforcement
  - focused prompt regression tests plus full pytest regression
- Findings:
  - the generation prompt now adds explicit suspense guidance that asks for grounded tension cues while forbidding invented off-screen threats
  - the revision prompt now re-includes the raw scene observations so repair attempts stay closer to visible evidence
  - the tuned prompt improved one provider-backed suspenseful run from the earlier low point of `sentiment_fit=0.40 / audit_score=0.48` up to `0.65 / 0.71`, but the result still stayed below threshold
  - a second provider-backed suspenseful run remained at `sentiment_fit=0.65` and slipped back to `audit_score=0.59`, which confirms the park storyboard still does not produce reliable suspenseful quality under the current prompt
- Evidence snippets:
  - focused regression: `pytest -q tests/services/test_generation_modes.py` -> `8 passed`
  - full regression: `pytest -q` -> `77 passed`
  - `2026-04-09T06:32:54Z suspenseful`: `sentiment_fit=0.65`, `audit_score=0.71`, `revision_limit_reached=true`
  - `2026-04-09T06:34:14Z suspenseful`: `sentiment_fit=0.65`, `audit_score=0.59`, `revision_limit_reached=true`
- Remaining risk:
  - on gentle, low-conflict image sequences, the provider still oscillates between weak suspense and invented unease, so the prompt is more controlled than before but not yet reliable enough to call the sentiment fixed
