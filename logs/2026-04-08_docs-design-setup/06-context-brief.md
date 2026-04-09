# 다음 작업용 컨텍스트 브리프

## 프로젝트 핵심

- 목표는 여러 장의 이미지와 선택된 감정을 바탕으로 짧고 grounded 된 스토리를 생성하는 MVP이다.
- 구조 원칙은 `global md > project md > skill md > docs > readme` 이다.
- 디자인 문서는 `awesome-design-md` 스타일의 9개 섹션 구조를 채택했다.

## 이미 정해진 구조

- 전역 규칙: `AGENTS.md`
- 전역 디자인 시스템: `DESIGN.md`
- 프로젝트 범위: `projects/visual-storytelling/PROJECT.md`
- 실행 루프 프롬프트: `projects/visual-storytelling/EXECUTION_LOOP_PROMPT.md`
- 기능별 구현 규칙: `projects/visual-storytelling/SKILLS/*.SKILL.md`
- 아키텍처/요구사항: `docs/**`
- 실행 기록: `logs/**`

## 지금 가장 자연스러운 다음 단계

1. `packages/core`에 domain models 추가
2. `packages/prompts`에 prompt contract와 초기 prompt 파일 추가
3. `packages/services`에 analysis / sequencing / generation / session interface 추가
4. 그 다음에 `apps/api` transport 뼈대 추가

## 유지해야 할 설계 원칙

- prompt는 서비스 코드에 인라인으로 넣지 않는다.
- 분석, 시퀀싱, 생성, 재생성은 분리된 서비스 경계로 유지한다.
- regeneration은 원본 analysis 결과를 in-place 변경하지 않는다.
- logs는 다음 작업자가 바로 이어갈 수 있을 만큼 현재 상태를 진실하게 남긴다.

## 보고서용으로 특히 중요한 포인트

- 문서 계층과 우선순위를 명시적으로 설계했다는 점
- 디자인과 개발 규칙을 분리했다는 점
- 스파게티 방지 규칙을 먼저 고정한 뒤 구현으로 넘어간다는 점
- 작업 흔적을 `logs/`에 구조적으로 남기도록 만들었다는 점
