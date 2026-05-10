---
name: write-adr
description: Generate an Architecture Decision Record (ADR) for a technical choice, capturing context, decision, alternatives considered, and consequences.
compatibility: Accepts a natural language description. Optionally reads local code or existing ADRs to infer context.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Generate a well-structured ADR for the given technical decision.

## Determine the target

Accept any of:
- A natural language decision statement: `use GraphQL federation`, `Redis for authorization cache`
- A file or directory for context: `src/auth/`, `src/api/schema.ts`
- An explicit title: `"ADR: Replace REST with tRPC for internal services"`

If a file or directory is given, read the relevant source files to infer the current state before writing the ADR.

If existing ADRs are present in the repo (look for `docs/adr/`, `docs/decisions/`, `adr/`, or files matching `**/ADR-*.md`, `**/0*.md`), read the most recent 2–3 to match the project's numbering scheme, status vocabulary, and formatting conventions.

## Discovery steps (for local targets)

1. **Existing ADRs** — Glob for `docs/adr/*.md`, `docs/decisions/*.md`, `adr/*.md`. Read the last 2–3 to infer: numbering format (e.g. `ADR-001`), status values used (e.g. `Proposed`, `Accepted`, `Deprecated`), and any custom sections the project adds.

2. **Current implementation** — If a source path is given, read relevant files to understand the current approach being replaced or extended.

3. **Dependencies and constraints** — Grep for related packages, config, or infrastructure references that inform the decision context (`package.json`, `go.mod`, `requirements.txt`, `*.tf`, `docker-compose.yml`).

## What to capture

Work through each section before writing:

- **Context**: What problem exists? What forces are in play — technical constraints, team capability, scale requirements, cost, security, compliance? Be specific about what triggered this decision.
- **Decision**: State the chosen option clearly in one sentence. This is the headline — make it unambiguous.
- **Alternatives**: What else was considered? For each alternative, give a brief rationale for why it was not chosen. Two or three alternatives is typical; more than four is usually a sign the decision scope is too broad.
- **Consequences**: What does this decision make easier? What does it make harder? Include: migration effort, learning curve, operational impact, future constraints, and any decisions this one unlocks or forecloses.
- **Status**: Default to `Proposed` unless the user specifies otherwise.

## Output format

By default, write the ADR to a file. Infer the output path from any existing ADR directory structure in the repo. If none exists, default to `docs/adr/`. Number sequentially from existing ADRs, or start at `ADR-001` if none exist.

If the user passes `--inline`, respond inline instead of writing a file.

### File name

Use the format: `{number}-{kebab-case-title}.md`
Example: `docs/adr/ADR-004-use-graphql-federation.md`

### ADR content

```markdown
# {NUMBER}: {Title}

**Date:** {YYYY-MM-DD}
**Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-XXX]
**Deciders:** {list if known, otherwise omit}

## Context

{2–4 sentences describing the problem, the forces in play, and what makes this decision necessary now. Be concrete — name the system, the scale, the pain point.}

## Decision

{One clear sentence stating the chosen approach.}

{1–2 paragraphs elaborating on the decision: what it covers, what it explicitly does not cover, and any conditions or constraints under which it applies.}

## Alternatives Considered

### {Alternative 1}
{What it is and why it was not chosen — one short paragraph.}

### {Alternative 2}
{What it is and why it was not chosen — one short paragraph.}

## Consequences

**Positive:**
- {Benefit 1}
- {Benefit 2}

**Negative / Trade-offs:**
- {Cost or constraint 1}
- {Cost or constraint 2}

**Risks:**
- {Risk 1 and how it will be mitigated}

## References

- {Link to relevant RFC, PR, spike, or external resource — omit section if none}
```

After writing the file, respond inline with:
- The file path written
- A one-paragraph summary of the decision for use in a PR description or Slack message

## Gotchas

- The decision statement must be a statement, not a question. "Use Redis for session storage" not "Should we use Redis?".
- Do not pad Alternatives with straw men. Each alternative should be something the team genuinely considered.
- Consequences should be honest about trade-offs — an ADR that lists only positives will not be trusted.
- If the decision has already been implemented, set status to `Accepted` and note the date of implementation in the Context.
- Do not create a new ADR directory structure without confirming with the user if the repo has no existing ADR convention — ask where they want it.
- This skill pairs naturally with `/draft-rfc` (an RFC captures the proposal and discussion; an ADR records the final decision that came out of it), `/design-system` (each significant architectural choice made during system design warrants its own ADR), and `/migrate-data` (schema changes significant enough to need a migration plan often warrant an ADR to record the data model decision).
