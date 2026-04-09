# Problem Definition

- Purpose: Translate the product vision into a concrete engineering and product problem statement.
- Owner: Product lead and tech lead.
- When to read: Before writing requirements, contracts, or implementation plans.
- Decisions that belong here: Problem framing, assumptions, constraints, and failure conditions.

## Problem Statement

We need to build a system that receives an ordered list of user-uploaded images plus a selected sentiment, analyzes visible content in each image, links the images into a coherent sequence, and generates a short story whose tone matches the sentiment without inventing too many unsupported facts.

## Why This Is Hard

- Multi-image understanding is not the same as single-image captioning.
- Narrative coherence depends on image order and transition logic.
- Sentiment control can easily overpower factual grounding.
- UI and prompt iteration will likely change quickly during MVP learning.
- Without explicit contracts, analysis and generation outputs can drift into untestable free text.

## Inputs

- 2 to 8 user-uploaded images for the initial MVP assumption.
- User-selected sentiment such as happy, sad, suspenseful, wistful, or hopeful.
- Optional future regeneration hints, not required for the first pass.

## Expected Outputs

- Structured analysis per image.
- A linked sequence representation capturing narrative progression.
- A short grounded story in the requested tone.
- UI-visible status information across upload, analysis, and generation steps.

## Constraints

- Grounding matters more than literary complexity.
- The system must preserve the user-selected image order.
- Prompt templates should remain separable from orchestration code.
- The design must allow later UI refinement without reworking core domain logic.
- The MVP should avoid unnecessary persistence and platform complexity.

## Failure Modes To Design Around

- Story introduces events or relationships not supported by the images.
- Image sequence is ignored or collapsed into a generic summary.
- Sentiment control causes repetitive or exaggerated tone.
- Partial analysis failure blocks the full workflow without useful recovery.
- Frontend and backend drift into incompatible schema definitions.

## Working Assumptions

- The first implementation can operate synchronously for small workloads.
- A single backend service can coordinate analysis and generation for the MVP.
- We can start with a small curated sentiment set instead of unconstrained free-form tone input.
