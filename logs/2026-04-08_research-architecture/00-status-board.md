# 상태 보드

## 현재 진행 중

- `packages/core`의 typed domain contracts 구현 준비
- 단계별 서비스 interface 설계 준비
- submission wrapper를 실제 파이프라인에 연결하기 전 thin-wrapper 원칙 유지

## 방금 끝남

- 기존 단순 분석-생성 구조를 observation -> memory -> plan -> sentiment -> draft -> evaluate -> revise 구조로 재정의
- `packages/infra`와 `submission/` 경계를 문서에 반영
- `system-iteration.SKILL.md`와 구현 프롬프트 문서 추가
- `pyproject.toml`에 `packages/infra/src` 경로 반영
- `.env`와 `.env.example`에 evaluation/revision 모델 설정 슬롯 추가

## 이제 안 봐도 됨

- "이 프로젝트를 image captioning처럼 다뤄도 되는가"에 대한 초기 모호성
- submission 구조를 개발 구조와 동일 파일에 몰아넣을지에 대한 고민
