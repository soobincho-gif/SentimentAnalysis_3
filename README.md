# Visual Storytelling Monorepo

- Purpose: Orient contributors to the repository, explain what we are building, and point to the right documents first.
- Owner: Repository maintainers.
- When to read: First entry point for any new human or coding agent entering the project.
- Decisions that belong here: Repository overview, quick start, directory map, and document navigation.

## What We Are Building

This repository is for an MVP that turns multiple user-uploaded images plus a chosen sentiment into a short, grounded story.

Core product promises:

- users can upload multiple images in sequence,
- the story follows that sequence naturally,
- the selected sentiment influences tone and style,
- story details stay grounded in visible image content,
- the UI can later support refinement and regeneration without breaking the core architecture.

## Current Status

The repository is intentionally documentation-first. The first pass establishes:

- a repo-wide engineering rulebook,
- a global design system,
- project-specific execution docs,
- feature-specific skill docs,
- a monorepo layout for backend, frontend, prompts, and shared domain logic.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

This setup currently prepares the repository for MVP implementation work. Application code is still expected to be added in the next phase.

## Top-Level Directory Guide

- `apps/`: Deployable applications such as the backend API and the future web client.
- `packages/`: Shared domain logic, services, prompt assets, and optional shared UI assets.
- `submission/`: Thin Python-first entrypoint for coursework submission or simple demos.
- `docs/`: Planning, architecture, product behavior, engineering standards, ADRs, and handoff material.
- `projects/`: Project-specific execution documents that narrow the repository rules to one delivery stream.
- `logs/`: Dated work logs for plans, resolved items, change summaries, and report-ready handoff notes.
- `tests/`: Cross-package tests, integration tests, fixtures, and evaluation coverage.

## Document Navigation

Read documents in this order:

1. [AGENTS.md](/Users/sarahc/Downloads/SentimentAnalysis_3/AGENTS.md)
2. [DESIGN.md](/Users/sarahc/Downloads/SentimentAnalysis_3/DESIGN.md)
3. [projects/visual-storytelling/PROJECT.md](/Users/sarahc/Downloads/SentimentAnalysis_3/projects/visual-storytelling/PROJECT.md)
4. Relevant skill docs in [projects/visual-storytelling/SKILLS](/Users/sarahc/Downloads/SentimentAnalysis_3/projects/visual-storytelling/SKILLS)
5. Architecture and planning docs under [docs](/Users/sarahc/Downloads/SentimentAnalysis_3/docs)
6. Local README files for implementation details

## MVP Roadmap Snapshot

- Phase 1: Documentation, contracts, and module boundaries.
- Phase 2: Core domain models plus service interfaces.
- Phase 3: Image analysis and sequencing flow.
- Phase 4: Story generation and regeneration flow.
- Phase 5: API surface and first-pass web UI.

The detailed handoff plan lives in [docs/06_handoffs/implementation-roadmap.md](/Users/sarahc/Downloads/SentimentAnalysis_3/docs/06_handoffs/implementation-roadmap.md).
