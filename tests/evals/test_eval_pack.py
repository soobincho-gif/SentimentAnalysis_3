from __future__ import annotations

import pytest

from packages.core.models.story import StoryRequest
from packages.infra.bootstrap import build_pipeline
from tests.evals.fixtures import EVAL_CASES, EvalCase


from dotenv import load_dotenv
load_dotenv()

@pytest.mark.parametrize("case", EVAL_CASES, ids=lambda c: c.name)
def test_eval_case_pipeline_run(case: EvalCase) -> None:
    pipeline = build_pipeline(use_mock=False)
    
    # Normally scene analysis returns observations. We use our fixture directly.
    observations = case.observations
    
    # 2. Sequence Memory
    sequence_memory = pipeline.sequence_linking_service.build(observations)
    
    # 3. Narrative Plan
    narrative_plan = pipeline.narrative_planning_service.plan(
        observations=observations,
        sequence_memory=sequence_memory,
        max_sentences=6
    )
    
    # 4. Sentiment Profile
    sentiment_profile = pipeline.sentiment_control_service.resolve(case.sentiment)
    
    # 5. Story Generation
    story_draft = pipeline.story_generation_service.generate(
        observations=observations,
        sequence_memory=sequence_memory,
        narrative_plan=narrative_plan,
        sentiment_profile=sentiment_profile,
        max_sentences=6
    )
    
    # 6. Evaluation
    evaluation = pipeline.evaluation_service.evaluate(
        story_draft=story_draft,
        observations=observations,
        sequence_memory=sequence_memory,
        sentiment_profile=sentiment_profile,
    )
    
    # Asserts - Basic sanity that the pipeline produces results
    assert story_draft.title
    assert story_draft.story_text
    assert evaluation.grounding_score > 0
    assert evaluation.coherence_score > 0
    
    # Print out summary for manual review / regression logging
    print(f"\n--- EVAL CASE: {case.name} ---")
    print(f"Goal: {case.expected_success_criteria}")
    print(f"Story: {story_draft.story_text}")
    print(f"Eval Scores: Grounding={evaluation.grounding_score:.2f}, Coherence={evaluation.coherence_score:.2f}, Redundancy={evaluation.redundancy_score:.2f}, Sentiment={evaluation.sentiment_fit_score:.2f}")
    if evaluation.flags:
        print(f"Flags detected: {evaluation.flags}")
