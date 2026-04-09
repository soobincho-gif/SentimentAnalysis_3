# 남은 리스크와 확인 필요 사항

## 리스크

- 실제 코드 구현 전이라 `submission/app.py`는 아직 placeholder 상태다.
- Scene analysis 결과에서 recurring entity linking이 어느 정도까지 가능한지 실제 이미지 데이터로 검증되지 않았다.
- evaluator 기준은 문서화됐지만 점수화 방식은 아직 구현되지 않았다.

## 확인 필요 사항

- MVP에서 Streamlit, Gradio, CLI 중 어떤 submission UI를 쓸지
- evaluator를 rule-based로 시작할지 model-assisted로 시작할지
- image analysis와 story generation에서 같은 모델을 쓸지 stage별로 나눌지

## 다음 권장 작업

1. `packages/core` domain contracts 구현
2. `packages/services` 단계별 interface 생성
3. `packages/prompts` 계약 및 초기 prompt assets 생성
