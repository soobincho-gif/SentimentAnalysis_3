# 다음 작업용 컨텍스트 브리프

## 이번 세션의 핵심 설계 변화

- 프로젝트 파이프라인이 이제 `scene observation -> sequence memory -> narrative planning -> sentiment control -> story draft -> evaluation -> revision` 기준으로 정의됐다.
- `submission/app.py`는 thin wrapper이며, 실제 비즈니스 로직은 절대 두지 않는다는 경계가 정해졌다.
- failure taxonomy가 정의되어 이후 테스트와 로그가 같은 언어를 쓰게 됐다.

## 다음 구현자가 바로 알아야 할 것

- `docs/02_architecture/system-architecture.md`가 이번 세션의 중심 문서다.
- `docs/02_architecture/data-contracts.md`에 이제 구현해야 할 canonical contracts가 정의되어 있다.
- `projects/visual-storytelling/SKILLS/system-iteration.SKILL.md`를 읽고 루프형 구현을 따라야 한다.
- `projects/visual-storytelling/IMPLEMENTATION_PROMPT.md`는 다음 코딩 세션에서 바로 사용할 수 있다.

## 다음 가장 자연스러운 구현 순서

1. `packages/core`에 typed models 추가
2. `packages/services` 단계별 interface 추가
3. `packages/prompts` prompt contract와 초기 자산 추가
4. `submission/app.py`는 마지막에 thin orchestration으로 연결
