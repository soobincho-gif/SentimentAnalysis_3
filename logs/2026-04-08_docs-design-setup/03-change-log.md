# 변경 로그

## 생성 및 수정 파일

- `DESIGN.md`
- `AGENTS.md`
- `README.md`
- `.gitignore`
- `.env`
- `logs/README.md`
- `logs/2026-04-08_docs-design-setup/01-plan.md`
- `logs/2026-04-08_docs-design-setup/02-resolved-items.md`
- `logs/2026-04-08_docs-design-setup/03-change-log.md`
- `logs/2026-04-08_docs-design-setup/04-open-risks.md`
- `logs/2026-04-08_docs-design-setup/05-sources.md`

## 핵심 변경 내용

### `DESIGN.md`

- `awesome-design-md` 스타일에 맞춰 9개 섹션 구조로 재작성
- 프로젝트 특성에 맞는 warm editorial storyboard 방향 유지
- 에이전트가 바로 사용할 수 있는 color reference와 component prompt 추가

### `AGENTS.md`

- `logs/` 폴더 운영 규칙 추가
- 로그가 규칙 문서를 대체하지 않는다는 경계 명시

### `README.md`

- 최상위 디렉터리 설명에 `logs/` 추가

### `.gitignore`

- `.env`와 Python 캐시 계열 추적 방지 추가

### `.env`

- 새 OpenAI API 키 반영
- 나머지 설정은 현재 구조에 맞는 기본값 유지
