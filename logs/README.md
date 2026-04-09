# Logs

- Purpose: Keep report-friendly records of major repository work in one predictable place.
- Owner: Whoever performs the work.
- When to read: During handoff, reporting, retrospective review, or when reconstructing why something changed.
- Decisions that belong here: Historical summaries only. Logs do not define repo policy.

## Folder Convention

Create one dated folder per meaningful work session:

- `logs/YYYY-MM-DD_slug/`

Recommended files:

- `00-status-board.md`
- `01-plan.md`
- `02-resolved-items.md`
- `03-change-log.md`
- `04-open-risks.md`
- `05-sources.md`
- `06-context-brief.md`

## Runtime Trace Logs

- Machine-generated run traces may also be stored in `logs/runtime/` when the app needs repeatable audit artifacts.
- Keep these files append-only and secret-free.
- Prefer JSONL for automated inspection and markdown summaries in dated folders for human handoff.

## Writing Style

- Prefer concise factual summaries over diary-style narration.
- Include assumptions, boundaries, and changed files.
- Never store secret values in logs.
- In `00-status-board.md`, always split work into:
  - `현재 진행 중`
  - `방금 끝남`
  - `이제 안 봐도 됨`
