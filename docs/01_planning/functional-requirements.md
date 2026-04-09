# Functional Requirements

- Purpose: Capture the product behaviors the MVP must support.
- Owner: Product lead with engineering review.
- When to read: Before implementing service flows, API contracts, or UI states.
- Decisions that belong here: User-visible capabilities, scope boundaries, and acceptance-level behavior.

## FR-01 Image Upload

The system must allow the user to upload multiple images in one storytelling session.

- Initial target: 2 to 8 images.
- The system must preserve file association to a session request.

## FR-02 Explicit Image Order

The system must preserve the user-defined order of images and treat that order as the primary narrative sequence input.

- The user must be able to review the current order before generation.
- Future UI iterations may allow reordering before regeneration.

## FR-03 Sentiment Selection

The system must allow the user to select a sentiment or tone preset for story generation.

- Example sentiments: happy, sad, suspenseful, hopeful, wistful.
- The chosen sentiment must influence voice and pacing without replacing grounded content.

## FR-04 Per-Image Analysis

The system must analyze each image and extract structured grounded observations.

Required observation categories:

- characters or visible subjects,
- setting or scene context,
- visible actions,
- notable objects,
- visible mood cues,
- uncertainty notes when evidence is weak.

## FR-05 Sequence Linking

The system must derive a linked interpretation of how the images relate across time or narrative progression.

- It must reference the actual image order.
- It must not assume continuity when the evidence is weak without flagging uncertainty.

## FR-06 Grounded Story Generation

The system must generate a short story based on the image analyses, linked sequence, and chosen sentiment.

- The story should feel coherent from first image to last image.
- The story should avoid unsupported named entities, backstory, or hidden motives unless clearly framed as mild inference.

## FR-07 Visible Workflow States

The system must expose clear status stages to the user:

- upload ready,
- analyzing images,
- linking sequence,
- generating story,
- completed,
- failed with actionable recovery.

## FR-08 Regeneration Readiness

The system architecture must support future regeneration flows.

- The original image analyses should remain reusable.
- Changing sentiment should not require recomputing analysis unless inputs changed.

## FR-09 Extensible Prompting

The system must keep prompt templates versioned and separate from service orchestration so that prompt iteration does not require rewriting domain logic.

## FR-10 API And UI Contract Consistency

The system must use explicit contracts for request and response payloads so backend and frontend can evolve together without ad hoc field drift.
