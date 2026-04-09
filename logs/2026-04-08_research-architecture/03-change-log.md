# 변경 로그

## 생성 및 수정 파일

- `AGENTS.md`
- `README.md`
- `.env.example`
- `.env`
- `pyproject.toml`
- `docs/02_architecture/system-architecture.md`
- `docs/02_architecture/data-contracts.md`
- `docs/04_engineering/code-structure.md`
- `docs/05_decisions/ADR-002-research-grounded-storytelling-pipeline.md`
- `docs/06_handoffs/implementation-roadmap.md`
- `projects/visual-storytelling/README.md`
- `projects/visual-storytelling/TASKS.md`
- `projects/visual-storytelling/IMPLEMENTATION_PROMPT.md`
- `projects/visual-storytelling/SKILLS/system-iteration.SKILL.md`
- `packages/infra/README.md`
- `packages/infra/src/.gitkeep`
- `submission/README_submission.md`
- `submission/app.py`
- `logs/2026-04-08_research-architecture/00-status-board.md`
- `logs/2026-04-08_research-architecture/01-plan.md`
- `logs/2026-04-08_research-architecture/02-resolved-items.md`
- `logs/2026-04-08_research-architecture/03-change-log.md`
- `logs/2026-04-08_research-architecture/04-open-risks.md`
- `logs/2026-04-08_research-architecture/05-sources.md`
- `logs/2026-04-08_research-architecture/06-context-brief.md`

## 핵심 변경

- 파이프라인을 one-shot generation이 아닌 staged storytelling pipeline으로 재설계
- entity memory와 evaluator/revision을 구조 안에 명시적으로 추가
- infra와 submission 경계를 분리
- evaluation/revision 단계에 맞는 환경 설정 슬롯을 추가
- 다음 구현 루프용 프롬프트와 skill 문서 추가
