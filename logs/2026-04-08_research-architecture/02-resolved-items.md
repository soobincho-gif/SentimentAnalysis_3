# 해결한 항목

## 1. captioning과 storytelling 혼동 해결

- 아키텍처 문서에 이 과제가 단순 이미지 캡셔닝이 아니라 ordered multi-image storytelling 문제라는 점을 명시했다.

## 2. reasoning과 realization 혼합 문제 해결

- 관측 사실 추출, 메모리, 서사 계획, 감정 제어, 초안 생성, 평가, 수정의 경계를 분리했다.

## 3. submission 구조로 인한 스파게티 위험 해결

- `submission/app.py`를 thin wrapper로 정의하고 실제 비즈니스 로직은 패키지 구조에 남기도록 경계를 고정했다.

## 4. 반복 개선 루프 부재 해결

- `system-iteration.SKILL.md`와 구현 프롬프트에 design -> attempt -> evaluate -> revise -> record 흐름을 강제했다.
