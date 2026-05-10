---
name: estimate-effort
description: Produce a justified effort estimate (S/M/L/XL) for a ticket, story, or feature request — assessing scope clarity, code touchpoints, test burden, unknowns, and risk factors, with a split recommendation if XL.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts a ticket file, a story description, or natural language without file access.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.1"
  last-updated: 2026-05-10
---

Produce a structured, justified effort estimate for the given piece of work — grounded in what the codebase actually looks like, not just the ticket description.

This is not a planning poker replacement. Use this skill before a ticket enters a sprint to surface unknowns, identify split opportunities, and give the implementing engineer a head start on where complexity lies.

## Determine the target

Accept any of:
- A ticket file: `docs/tickets/add-csv-export.md`
- A ticket title or keyword: `csv export` — search `docs/tickets/` and `docs/changes/` for a matching file
- A story description inline: `add pagination to the orders list endpoint`
- A spec section: `docs/specs/passkey-auth.md — focus on the registration flow`
- No argument — estimate the most recent `status:todo` ticket

If no local path is given and no codebase is accessible, derive estimates from the description alone and flag every factor as `Assumed — not verified in code`.

## Discovery steps

Work through each factor before producing the estimate. Every factor assessment must be grounded in what was actually read or found — not assumed.

### 1. Read the ticket or description

Extract:
- **What** is being built or changed — the concrete deliverable
- **Acceptance criteria** — the list of conditions that define done. Count them: more criteria = larger scope.
- **Stated constraints** — performance targets, backward compatibility, specific APIs to use
- **Open questions** — anything in the ticket marked as unclear, TBD, or requiring a decision

If there are more than 5 acceptance criteria, the ticket is likely M or larger before any code analysis.

### 2. Find affected code

Grep for the ticket's primary nouns (feature name, model name, endpoint path, component name) in the source tree. Glob for likely file locations.

Count:
- How many files will need to change?
- How many layers are involved? (e.g. route + service + model + test = 4 layers minimum)
- Are the changes concentrated (one module) or spread (cross-cutting)?

| Touchpoints | Signal |
|-------------|--------|
| 1–3 files, 1 layer | S candidate |
| 4–8 files, 2–3 layers | M candidate |
| 9–15 files, multiple layers | L candidate |
| 15+ files or cross-service | XL candidate |

### 3. Check for prior art

Grep for a similar pattern already implemented in the codebase (e.g. another export endpoint, another paginated list, another auth flow). Prior art means the implementing engineer can follow an established pattern — this reduces complexity by one size step. Absence of prior art means design work is required.

### 4. Assess test burden

Glob for test files in the affected area (`**/*.test.*`, `**/*.spec.*`, `**/test_*.py`).

- **Existing test infrastructure present** — new tests follow established patterns: lower burden
- **No tests in the affected area** — test setup must be created: higher burden
- **Integration or E2E tests required** — significantly higher burden than unit tests alone
- **External service mocking required** — adds setup complexity

### 5. Identify external dependencies

Grep for any of the following that the ticket will need to introduce or extend:
- Database schema changes (`migration`, `ALTER TABLE`, `addColumn`, `prisma migrate`)
- External API integrations (new HTTP client calls, SDK initialization)
- Infrastructure changes (new queue, new cache, new storage bucket)
- Feature flag setup (`LaunchDarkly`, `Unleash`, `Split`, `getFlag`)
- Auth or permission model changes

Each external dependency adds coordination overhead and increases the risk of delay.

### 6. Assess unknowns

List questions that cannot be answered from the ticket or the codebase alone — things the implementing engineer would have to investigate or decide:

- Ambiguous acceptance criteria with multiple valid interpretations
- Missing data model decisions (which table? which field type?)
- Unclear error handling expectations
- No specification for edge cases the engineer will encounter

Each unresolved unknown is a risk multiplier. More than 2 unknowns on an otherwise S ticket makes it M. More than 2 unknowns on an L ticket makes it XL.

## Sizing definitions

| Size | Calendar time | What it means |
|------|--------------|---------------|
| **S** | < 1 day | Clear scope, ≤5 files, existing patterns, tests straightforward, no external dependencies, no unknowns |
| **M** | 1–3 days | Some complexity in one area — moderate touchpoints, minor design decisions, or one external dependency |
| **L** | 3–5 days | Significant complexity — many touchpoints, design decisions required, no prior art, schema migration, or integration work |
| **XL** | > 1 week | Should be split — multiple L-level concerns combined, or significant unknowns requiring a spike |

These are engineering days, not calendar days. They assume the implementing engineer is familiar with the codebase.

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/estimates/{kebab-case-target}.md`.

---

### Estimate: `{ticket title}`

**Size: {S / M / L / XL}** — {one sentence: the dominant reason for this size}

**Factor breakdown**

| Factor | Finding | Impact |
|--------|---------|--------|
| Scope clarity | {e.g. 4 clear acceptance criteria, no ambiguity} | Low risk |
| Code touchpoints | {e.g. 6 files across route, service, model, test layers} | Medium |
| Prior art | {e.g. similar CSV export exists at src/reports/export.ts} | Reduces size |
| Test burden | {e.g. integration test infrastructure already in place} | Low |
| External dependencies | {e.g. no schema changes, no external APIs} | None |
| Unknowns | {e.g. error format for partial export failure not specified} | 1 open question |

**Confidence: {High / Medium / Low}**

High = all factors are verified in code and criteria are clear.
Medium = 1–2 factors are assumed or unverified.
Low = significant unknowns; estimate could shift a full size in either direction.

**Main uncertainty**

{What single thing, if resolved, would most change this estimate? Name the specific open question or missing information.}

**Split recommendation** *(XL only)*

If the estimate is XL, propose a concrete split into 2–3 L-or-smaller pieces that are each independently deployable:

1. **{Part 1 title}** — scope, size, why it can ship first
2. **{Part 2 title}** — scope, size, dependency on Part 1
3. **{Part 3 title if needed}** — scope, size

**Quick wins** *(optional)*

If any acceptance criteria could be delivered ahead of the full ticket as a smaller standalone change, note them here.

---

## Gotchas

- An estimate is not a commitment. State the confidence level and the main uncertainty explicitly — a Medium-confidence M is not the same as a High-confidence M.
- Do not conflate calendar time with engineering time. A ticket that requires waiting for a third-party API or a team dependency is not necessarily a larger engineering effort — flag the dependency separately.
- Prior art cuts both ways. If the "prior art" is poorly structured legacy code, following it adds risk rather than reducing it. Note when prior art is low quality.
- Unknowns that seem minor often aren't. An unspecified error format, an ambiguous ownership model, or an undecided caching strategy can each consume a full day of back-and-forth. Surface them in the main uncertainty section.
- XL is always a split recommendation, not a size to accept. If the estimate comes out XL, the output must include a concrete split — not just a note that it's large.
- Do not adjust estimates to match what the team wants to hear. A ticket that is genuinely L should be called L, even if the sprint plan assumes M.
- This skill pairs naturally with `/create-ticket` (estimate a ticket immediately after writing it, before it enters a sprint), `/complete-ticket` (the estimate surfaces unknowns the implementing engineer will encounter), and `/spec-to-backlog` (for a full backlog, spec-to-backlog assigns inline sizes; use estimate-effort for a deeper analysis of any individual story before it is picked up).
