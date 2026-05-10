---
name: refactor-strategy
description: Produce a large-scale refactoring or modernization roadmap with incremental migration phases, blast radius analysis, rollback plan, and risk register.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts natural language descriptions of the current and target state.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Produce an actionable refactoring roadmap for the given migration or modernization goal.

## Determine the target

Accept any of:
- A migration goal: `monolith to microservices`, `REST to GraphQL`, `class components to hooks`
- A modernization goal: `upgrade to Python 3.12`, `migrate from Moment.js to date-fns`
- A local path to refactor: `src/legacy/`, `services/payments/`
- A combination: `src/auth/ — extract to standalone service`

If a local path is given, read the codebase before planning. The roadmap must be grounded in what actually exists, not a generic template.

If only a description is given, state your assumptions about the current state, team size, and deployment model before proceeding.

## Discovery steps (for local targets)

1. **Scope the codebase** — Glob for source files in the target path. Count files and estimate lines of code to calibrate the effort estimate.

2. **Identify coupling** — Grep for imports, references, and usages of the code being refactored. Map what depends on it and what it depends on. This is the blast radius.

3. **Find the seams** — Identify natural boundaries where the refactor can be split: module boundaries, interface points, domain boundaries, data ownership lines. These become phase boundaries.

4. **Assess test coverage** — Glob for test files (`**/*.test.*`, `**/*.spec.*`, `**/test_*.py`). Check whether the code under refactor has meaningful test coverage. Low coverage is a blocker that must be addressed in Phase 0.

5. **Identify shared state** — Grep for global state, shared databases, shared caches, or shared config that crosses the refactor boundary. Each is a coordination risk.

6. **Check deployment model** — Look for CI/CD pipeline definitions, Docker/Kubernetes configs, and feature flag infrastructure. These determine how incremental releases can be delivered.

## Planning process

Work through the following before producing output:

### 1. Define the current and target state
One sentence each: what exists now, what the end state looks like, and what the primary driver is (performance, maintainability, scalability, compliance, cost).

### 2. Identify the strangler fig opportunities
Where can the new implementation run alongside the old one? Where is a clean interface boundary (HTTP, event, function call) that can be used to route traffic incrementally? If no such boundary exists, Phase 0 must create one.

### 3. Define phases
Each phase must be:
- **Independently deployable** — it can ship without the next phase being complete
- **Reversible** — if it goes wrong, there is a defined rollback
- **Testable** — there is a clear definition of done

Aim for 3–5 phases. A phase that takes more than 4–6 weeks is too large — split it.

### 4. Assess blast radius per phase
For each phase, identify: what breaks if this goes wrong, who is affected (internal, external, downstream systems), and how quickly the impact would be detected.

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/refactoring/{kebab-case-title}.md`.

### Refactoring Strategy: `{target}`

**Current State**

2–3 sentences: what exists now, its key pain points, and why the refactor is necessary.

**Target State**

2–3 sentences: what the end state looks like, the primary quality improvement, and any explicit non-goals (what this refactor does not change).

**Assumptions**

Bullet list of assumptions about team size, deployment cadence, test coverage baseline, or technology constraints. Correct these before proceeding.

**Seam Map**

Where the refactor can be split. For each seam:
- **{Seam name}**: interface type (HTTP boundary, event, function call, data ownership line) — what sits on each side

**Migration Phases**

For each phase, use this format:

---
#### Phase {N}: {Title}
**Goal:** One sentence — what this phase achieves.
**Scope:** What changes in this phase (files, components, services).
**Approach:** How the change is made — strangler fig, branch-by-abstraction, parallel run, feature flag, big bang (flag if big bang, it requires justification).
**Definition of done:** Measurable criteria — tests passing, traffic migrated, old code deleted.
**Blast radius:** What breaks if this phase fails and who is affected.
**Rollback:** How to revert — feature flag off, redeploy previous image, data migration reversal.
**Effort estimate:** S / M / L / XL (S = days, M = 1–2 weeks, L = 3–4 weeks, XL = split this phase further).

---

**Risk Register**

| Risk | Likelihood | Impact | Phase | Mitigation |
|------|-----------|--------|-------|------------|

**Dependency Map**

What must be true before each phase can start:

| Phase | Depends on | External dependency |
|-------|-----------|---------------------|

**Test Strategy**

What testing must be in place before the refactor begins and how coverage will be maintained or improved across phases:
- Characterization tests / golden master tests for legacy behaviour
- Contract tests at seam boundaries
- Load/performance baselines if performance is a goal

**Open Questions**

Bullet list of decisions that must be resolved before or during the refactor. Name the owner and the decision needed.

## Gotchas

- Never plan a big-bang refactor for code with external consumers or a shared database without an explicit migration window. Flag it and recommend strangler fig instead.
- Phase 0 must exist if test coverage is low — do not plan a refactor on untested code without first adding characterization tests.
- Blast radius must be assessed from actual imports and usages, not guessed. Read the code.
- Rollback plans must be specific. "Revert the PR" is not a rollback plan if the phase includes a data migration.
- Effort estimates should be honest. XL phases are a signal to split, not a reason to pad the timeline.
- If the refactor crosses a team boundary (another team owns a dependency), name the coordination risk explicitly and do not assume their availability.
- This skill pairs naturally with `/research-codebase` (a full research pass before planning gives the blast radius assessment firm ground — especially useful for unfamiliar or large codebases), `/write-adr` (documenting the decision to refactor and the approach chosen), `/test-strategy` (characterization test coverage must be in place before refactoring — see Phase 0), and `/migrate-data` (refactors that include data model changes need a dedicated migration plan for each schema change).
