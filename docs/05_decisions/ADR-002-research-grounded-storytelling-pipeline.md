# ADR-002: Research-Grounded Storytelling Pipeline

- Purpose: Record the decision to use a staged visual storytelling pipeline instead of one-shot caption-like generation.
- Owner: Tech lead.
- When to read: Before questioning why the system separates observation, memory, planning, style control, generation, evaluation, and revision.
- Decisions that belong here: Durable architecture choices that shape module boundaries and evaluation strategy.

## Status

Accepted

## Context

The project is solving visual storytelling, not single-image captioning. Research in the area repeatedly highlights failures around cross-image coherence, recurring entity consistency, controllable style, and weak evaluation. A one-shot "images in, story out" architecture would make these failures difficult to isolate and correct.

## Decision

Use a staged pipeline:

1. input validation and preprocessing,
2. observable scene extraction,
3. sequence linking and entity memory,
4. narrative planning,
5. sentiment-controlled draft generation,
6. evaluation and revision.

Structured intermediates are required between stages. Final prose must not be generated directly from raw images once a structured observation layer exists.

## Consequences

Positive:

- easier debugging and targeted revision,
- clearer ownership boundaries,
- better grounding visibility,
- more meaningful evaluation hooks.

Tradeoffs:

- more moving parts,
- more intermediate contracts to maintain,
- slightly slower early implementation than a one-shot prototype.

## Supporting Sources

- [Visual Storytelling](https://aclanthology.org/N16-1147.pdf)
- [SEE&TELL: Controllable Narrative Generation from Images](https://openreview.net/pdf?id=_8Ity3P03Z1)
- [Make-a-Story](https://openaccess.thecvf.com/content/CVPR2023/papers/Rahman_Make-a-Story_Visual_Memory_Conditioned_Consistent_Story_Generation_CVPR_2023_paper.pdf)
- [Image-grounded controllable stylistic story generation](https://aclanthology.org/2022.latechclfl-1.6.pdf)
- [RoViST](https://aclanthology.org/2022.findings-naacl.206/)
