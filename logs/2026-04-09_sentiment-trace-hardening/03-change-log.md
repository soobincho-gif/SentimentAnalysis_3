# Change Log

- Failure type: `SENTIMENT_MISMATCH`
- Observed issue: local fallback stories changed sentiment labels only superficially and fallback evaluation returned nearly identical `sentiment_fit_score` values, which made it hard to verify whether tone control was actually working.
- Changes made:
  - added a typed `SentimentAudit` contract and deterministic audit rules in `packages/core`
  - attached the audit to `EvaluationReport` and surfaced it in the Diagnostics tab
  - added `SentimentRunLogger` so each run appends a JSONL record under `logs/runtime/`
  - strengthened fallback story phrasing and sentence flow so sentiment differences are visible without inventing unsupported events
- Verification:
  - focused tests for fallback generation, evaluation audit details, presentation rendering, contract round-trip, and pipeline logging all passed
  - full test suite passed with `72 passed`
- Example runtime log path:
  - `logs/runtime/2026-04-09_sentiment_runs.jsonl`
