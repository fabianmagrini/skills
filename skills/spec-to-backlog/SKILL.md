---
name: spec-to-backlog
description: Convert a product specification, PRD, or feature description into a sequenced backlog of epics, user stories, technical stories, and spikes with acceptance criteria and dependency ordering.
compatibility: Accepts natural language descriptions, markdown spec files, or local paths. Optionally reads existing API schemas and issue conventions.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Convert the given specification into a structured, sequenced backlog ready for sprint planning.

## Determine the target

Accept any of:
- A feature or domain description: `passkey auth`, `semantic layer`, `multi-tenant billing`
- A local spec file: `docs/specs/passkey-auth.md`, `PRD.md`
- A directory of spec documents: `docs/specs/`
- A combination: `docs/specs/passkey.md — focus on the mobile flow`

If a local path is given, read the spec file(s) first. Also read:
- API schemas (`**/openapi.yaml`, `**/swagger.json`, `**/*.graphql`) to understand what already exists and avoid re-speccing it
- Existing issue or story templates (`.github/ISSUE_TEMPLATE/`, `docs/templates/`) to match the team's format conventions
- Feature flag configuration to determine if rollout should be phased

If only a description is given, derive the backlog from the description and flag any gaps where the spec is underspecified — these should become spikes, not committed stories.

## Analysis steps

Work through the following before writing any stories:

### 1. Identify the scope boundary
What is explicitly in scope? What is explicitly out of scope? If the spec does not state out-of-scope items, infer them and list them for confirmation. A common failure mode is generating stories for work the team did not intend to include.

### 2. Identify existing capabilities
From the API schemas or codebase, determine what already exists that the feature can build on. Do not generate stories for work that is already done. Note the existing capabilities in the output.

### 3. Identify unknowns
List questions that cannot be answered from the spec alone and that would block story writing if left open. Convert each unknown into a spike rather than a committed story.

### 4. Identify work item types
For each piece of work, classify it before writing:
- **User story** — delivers direct user-facing value. Uses the "As a / I want / So that" format.
- **Technical story** — infrastructure, migration, API contract, or enabler work with no direct user value. Uses a direct action statement.
- **Spike** — time-boxed research or investigation for an unknown. Has a fixed timebox and a specific question to answer, not a deliverable.

### 5. Identify dependencies
Map which stories must be completed before others can start. This determines the sequence. Infrastructure and API contract stories almost always precede user stories that depend on them.

### 6. Identify rollout considerations
Does the feature need a feature flag? A phased rollout? A migration step before or after the feature is live? If so, add the corresponding technical stories.

## Output format

By default, write the backlog to a file. Infer the path from any existing spec or docs structure. If none exists, default to `docs/backlog/{kebab-case-feature}.md`. If the user passes `--inline`, respond inline instead.

After writing the file, print the file path and a one-paragraph summary of the epic scope and story count, suitable for sharing with a product manager.

### Backlog content

```markdown
# Backlog: {Feature Name}

**Source spec:** {file path or "inline description"}
**Generated:** {YYYY-MM-DD}
**Total stories:** {n user stories, n technical stories, n spikes}

---

## Scope

**In scope:**
- {item}

**Out of scope:**
- {item}

**Existing capabilities (no stories needed):**
- {what already exists and can be reused}

---

## Epics

{Group related stories into epics. Each epic delivers a coherent slice of value.}

### Epic {N}: {Title}
**Goal:** One sentence — what this epic delivers and for whom.

---

## Stories

Use this format for every story:

---
### {TYPE}-{N}: {Title}
**Type:** User Story / Technical Story / Spike
**Epic:** {Epic title}
**Size:** S / M / L / XL
**Depends on:** {story IDs, or "none"}

**{For user stories}**
As a {persona}, I want {capability} so that {benefit}.

**{For technical stories}**
{Direct action statement: implement / migrate / configure / expose}

**{For spikes}**
Investigate: {specific question to answer}
Timebox: {hours or days}
Output: {what the spike produces — a decision, a proof of concept, a measured result}

**Acceptance criteria**
- [ ] {Specific, testable criterion}
- [ ] {Another criterion}

**Technical notes**
{Optional: constraints, integration points, security considerations, or implementation hints surfaced from the spec or existing codebase. Omit if none.}

---
```

## Sequencing

After all stories are written, produce a dependency table and a recommended sprint sequence:

**Dependency map**

| Story | Depends on |
|-------|-----------|
| {ID} | {ID, ID} |

**Recommended sequence**

Group stories into waves that can be worked in parallel within each wave:

- **Wave 1 (start here):** {IDs} — foundation and spikes
- **Wave 2:** {IDs} — core implementation
- **Wave 3:** {IDs} — user-facing features
- **Wave 4:** {IDs} — polish, rollout, and cleanup

## Gotchas

- Do not generate stories for work that already exists in the codebase or API schema. Read the existing contracts first.
- Every user story must have at least two acceptance criteria. A story without acceptance criteria cannot be verified as done.
- Spikes must have a timebox and a specific output. An open-ended research task is not a spike — it is a sign the spec needs more work before stories can be written.
- Technical stories are not optional extras. Infrastructure, API design, database migrations, and feature flag setup are real work that must be sized and sequenced. Hiding them inside user stories leads to blown estimates.
- Size honestly. XL stories should be split. A story that cannot be completed and reviewed in a sprint is too large regardless of what the spec implies.
- If the spec is ambiguous about a significant design decision (data model, API shape, third-party integration), convert it to a spike rather than assuming an answer and building stories on top of that assumption.
- Rollout stories (feature flag on/off, gradual rollout, cleanup of flag after full release) are commonly forgotten. If the feature uses a feature flag, the backlog is incomplete without a story to remove it after rollout.
