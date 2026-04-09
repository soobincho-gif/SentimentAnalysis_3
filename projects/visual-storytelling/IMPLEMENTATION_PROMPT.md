# Research-Grounded Implementation Prompt

- Purpose: Give future coding agents a concrete prompt for turning the completed planning work into implementation without collapsing boundaries.
- Owner: Project lead and principal engineer.
- When to read: After planning is complete and before implementation begins.
- Decisions that belong here: Prompted execution scope, required boundaries, and expected deliverables for the next implementation phase.

## Ready-To-Use Prompt

```text
Use the existing architecture decisions in this repository and implement the project in two coordinated layers:

1. Development architecture
- Keep a clean package structure with:
  - packages/core
  - packages/services
  - packages/prompts
  - packages/infra
  - apps/api if needed
- Preserve strict boundaries between:
  - observable scene extraction
  - sequence memory
  - narrative planning
  - sentiment control
  - story generation
  - evaluation
  - revision

2. Submission architecture
- Create and maintain a submission-facing Python entrypoint at submission/app.py
- This file must stay thin and only orchestrate startup and user interaction
- Do not place core business logic in submission/app.py
- Keep the project runnable in a simple Python-first way suitable for coursework submission

Read and obey documents in this order:
1. AGENTS.md
2. DESIGN.md
3. projects/visual-storytelling/PROJECT.md
4. projects/visual-storytelling/EXECUTION_LOOP_PROMPT.md
5. projects/visual-storytelling/IMPLEMENTATION_PROMPT.md
6. relevant skill docs under projects/visual-storytelling/SKILLS/
7. docs/** architecture and planning docs
8. README.md files
9. current logs/** files

Task:
- generate the initial folder structure
- create Python modules and typed contracts
- create placeholder or MVP implementations for each pipeline stage
- add one end-to-end smoke path:
  images -> scene observations -> sequence memory -> narrative plan -> story draft -> evaluation report
- add minimal tests for contracts and one smoke test
- add README_submission.md explaining how to run the submitted Python app

Rules:
- one module, one reason to change
- no giant utils.py
- no prompt strings inside service logic
- keep all prompts in packages/prompts
- keep domain schemas explicit
- separate observed facts from narrative claims
- do not bypass structured intermediates
- do not move business rules into route handlers
- do not hide state in globals
- add TODO markers only where uncertainty is real
- prefer MVP practicality over overengineering

Required output:
1. final repo tree
2. created file list
3. short explanation of each layer
4. assumptions made
5. what was verified
6. what remains risky
```
