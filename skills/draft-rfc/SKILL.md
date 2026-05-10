---
name: draft-rfc
description: Scaffold a technical RFC (Request for Comments) or design spec for a feature or initiative, covering goals, non-goals, proposed solution, architecture, security, rollout, and alternatives.
compatibility: Accepts natural language descriptions. Optionally reads local code, existing RFCs, or ADRs to ground the design in the current system.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Draft a comprehensive RFC for the given feature or initiative.

## Determine the target

Accept any of:
- A feature or initiative description: `global rate limiting`, `passkey authentication`, `semantic search layer`
- A local notes or spec file: `docs/notes/rate-limiting.md`, `scratch/auth-rfc-notes.md`
- A combination: `docs/notes/passkey.md — focus on the mobile flow`

If a local path is given, read the file(s) first. Also read:
- Existing RFCs or specs (`docs/rfcs/`, `docs/specs/`, `docs/design/`, files matching `RFC-*.md`, `*.rfc.md`) to match the team's numbering scheme, status vocabulary, and any custom sections
- Relevant ADRs (`docs/adr/`) for decisions already made that constrain the design
- Relevant source files for the affected area — read enough to ground the proposed solution in how the system actually works today

If only a description is given, derive the RFC from the description and flag any gaps where more context is needed before the document can be finalized.

## Discovery steps (for local targets)

1. **Existing RFCs** — Glob for `docs/rfcs/*.md`, `docs/design/*.md`, `RFC-*.md`. Read the most recent 1–2 to infer: numbering format (e.g. `RFC-007`), status values, and any custom sections the team uses.

2. **Related ADRs** — Glob for `docs/adr/*.md`. Read any ADRs relevant to the feature area. These represent decisions already made — the RFC must not reopen closed ADRs without explicitly noting the change.

3. **Affected code** — Read representative files in the area the RFC will change: entry points, service interfaces, data models, API routes. The proposed solution must describe changes in terms of what actually exists, not a hypothetical clean slate.

4. **Existing API contracts** — Glob for `**/openapi.yaml`, `**/swagger.json`, `**/*.graphql`. If the RFC introduces API changes, the document must reference the current contract and show what changes.

## What to capture

Work through each section before writing:

- **Background**: What problem exists today? What is the evidence (metrics, user reports, incidents)? Why does it need solving now?
- **Goals**: What does success look like? Make each goal measurable where possible. A goal without a success criterion cannot be verified.
- **Non-Goals**: What is explicitly out of scope? This is as important as Goals — ambiguity here causes scope creep. Name at least two non-goals.
- **Proposed Solution**: How does the design work? Be specific enough that a senior engineer can assess feasibility without additional context.
- **Architecture changes**: What components change, are added, or are removed? Include a diagram if the change is non-trivial.
- **API / Interface changes**: New or modified endpoints, schemas, or contracts. Show before and after where applicable.
- **Data model changes**: New tables, fields, or indices. Note migration requirements.
- **Security considerations**: Authentication, authorization, input validation, secrets handling, data sensitivity. This section must never be left as TBD.
- **Performance and scalability**: Expected load, latency targets, scale constraints. Note any new I/O, caching requirements, or database query patterns.
- **Observability**: What new metrics, logs, and traces are needed? How will the team know if this is working in production?
- **Rollout plan**: How is this deployed safely? Feature flag, dark launch, gradual rollout, migration order. What is the rollback strategy?
- **Alternatives considered**: At least two genuine alternatives with honest trade-offs explaining why each was not chosen.
- **Open questions**: Decisions still to be made. Each must have a named owner and a target resolution date.

## Output format

By default, write the RFC to a file. Infer the output path from any existing RFC directory structure. If none exists, default to `docs/rfcs/`. Number sequentially from existing RFCs, or start at `RFC-001` if none exist.

If the user passes `--inline`, respond inline instead of writing a file.

### File name

Use the format: `{number}-{kebab-case-title}.md`
Example: `docs/rfcs/RFC-007-global-rate-limiting.md`

### RFC content

```markdown
# {NUMBER}: {Title}

**Date:** {YYYY-MM-DD}
**Status:** Draft | In Review | Accepted | Rejected | Superseded by [{RFC-XXX}]
**Author:** {if known}
**Reviewers:** {if known, else omit}
**Related:** {ADR links, prior RFC links, issue/ticket links}

---

## Summary

{2–3 sentence TL;DR. What is being proposed, why, and what the key trade-off is. A busy reader should understand the essence without reading further.}

---

## Background

{What is the current situation? What problem exists, and what evidence supports it? Why does this need to be addressed now rather than later? Be concrete — cite metrics, incidents, or user pain where possible.}

---

## Goals

- {Measurable goal 1}
- {Measurable goal 2}

**Success criteria:** {How will the team know this RFC achieved its goals? What metrics will be measured and what are the targets?}

---

## Non-Goals

The following are explicitly out of scope for this RFC:

- {Non-goal 1 — and why it is deferred}
- {Non-goal 2}

---

## Proposed Solution

### Overview

{High-level description of the approach. What is being built or changed, and how does it address the problem stated in Background?}

### Architecture

{Describe component-level changes. Use a Mermaid diagram for non-trivial changes:}

```mermaid
{diagram}
```

### API / Interface Changes

{New or modified endpoints, schemas, or contracts. Show before and after where applicable. If no API changes, state "No API changes."}

### Data Model Changes

{New tables, columns, indices, or migrations. If no data model changes, state "No data model changes."}

### Security Considerations

{Authentication and authorization implications, input validation, sensitive data handling, secrets, threat vectors introduced. This section must not be left as TBD.}

### Performance and Scalability

{Expected load, latency targets, new I/O patterns, caching strategy, database query impact, scale constraints.}

### Observability

{New metrics to instrument, log fields to add, trace spans to introduce. How will the team know this is working correctly in production?}

### Rollout Plan

{How is this deployed safely? Feature flag name, dark launch strategy, gradual rollout percentage, migration order. What is the rollback strategy if the rollout fails?}

---

## Alternatives Considered

### {Alternative 1}

{What it is and why it was not chosen — be honest about trade-offs, not dismissive.}

### {Alternative 2}

{What it is and why it was not chosen.}

---

## Open Questions

| Question | Owner | Target date |
|----------|-------|-------------|
| {Unresolved question} | {Name or team} | {YYYY-MM-DD} |

---

## References

- {Link to related RFC, ADR, issue, ticket, or external resource — omit section if none}
```

After writing the file, respond inline with:
- The file path written
- A two-sentence summary suitable for a Slack announcement or PR description
- A note on which Open Questions are most critical to resolve before the RFC can move to Accepted

## Gotchas

- Non-Goals must be named explicitly. An RFC without non-goals will attract scope creep during review. If the user has not named any, infer the most likely ones from the description and include them.
- Security Considerations must never be left as TBD. If the security implications are genuinely unknown, make that an Open Question with an owner — but do not skip the section.
- The proposed solution must be grounded in how the system works today. If local files were not read, flag that the architecture section may need revision once the current system is understood.
- Alternatives must be genuine. An alternative that is obviously wrong with no real trade-off is not an alternative — it is a straw man. Each alternative should be something a reasonable engineer might have proposed.
- Do not reopen closed ADRs without explicitly flagging it. If the RFC requires revisiting a prior decision, note the ADR by number and explain why the decision is being reconsidered.
- Open Questions with no owner and no target date will not get resolved. Every open question must have both.
- This skill pairs naturally with `/design-system` (a system design is a natural precursor to an RFC for a new service or platform), `/write-adr` (for individual decisions that emerge from RFC review), and `/spec-to-backlog` (to convert an accepted RFC into implementation stories).
