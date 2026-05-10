---
name: create-ticket
description: Create a well-formed change ticket from a description, bug report, or feature request — extracting problem statement, acceptance criteria, and technical context into a ready-to-implement ticket file.
compatibility: Requires Read, Glob, Grep, Write. Reads existing ticket files to match the project's schema before writing. Accepts natural language input or a file.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Create a single, well-formed ticket file that `/complete-ticket` can implement without ambiguity.

This is the input side of the ticket workflow. Use `/create-ticket` to capture and structure work. Use `/complete-ticket` to implement a ticket once it is written.

## Determine the target

Accept any of:
- A natural language description: `add a CSV export endpoint to the orders API`
- A bug description: `login fails with a 500 when the email contains a plus sign`
- A feature request fragment: `users need to be able to set a display name`
- A file containing a rough note or slack thread: `docs/notes/export-idea.md`
- A combination: `docs/notes/export-idea.md — focus on the CSV format, not PDF`

Also accept an optional destination flag:
- `--changes` — write to `docs/changes/` instead of `docs/tickets/`
- `--inline` — print the ticket without writing a file (for review before committing)

If the description is too vague to write acceptance criteria (e.g. "improve performance"), ask one clarifying question before proceeding: what specific behaviour should change, and how would we know it is better?

## Discovery steps

### 1. Find the existing ticket schema

Glob for existing tickets to understand the project's format before writing:
- `docs/tickets/*.md`, `docs/changes/*.md`

Read 1–2 examples. Extract:
- Which frontmatter fields are used beyond `title` and `status` (e.g. `type`, `priority`, `assignee`, `labels`)
- The body section headings used (`## What`, `## Why`, `## Acceptance criteria`, or different)
- Whether checklists (`- [ ]`) or prose are used for criteria

If no existing tickets exist, use the default format defined below. State that the format is a default — the user can adjust.

### 2. Check for duplicates

Grep existing ticket files for keywords from the description:
- Search `docs/tickets/` and `docs/changes/` for significant nouns and verbs from the input (e.g. `export`, `CSV`, `orders`, `login`, `plus sign`)
- If a matching `status:todo` or `status:doing` ticket is found, report it and ask whether to proceed with a new ticket or update the existing one

Do not create a duplicate without flagging the conflict.

### 3. Identify affected code areas (optional)

If a local codebase is present and the description names a feature, endpoint, or module:
- Grep for related route definitions, service files, or model names
- Note the likely affected files in the ticket's technical notes section — this gives the implementer a head start without prescribing the solution

Do not read deeply into the code for this step — surface-level file identification is enough.

## Ticket writing process

Work through the following before writing the file:

### 1. Extract the problem statement

From the input, identify:
- **What** is wrong or missing — the gap between current and desired behaviour
- **Who** is affected — user type, team, or system
- **Why** it matters — the consequence of not fixing it

Write these as prose, not as implementation instructions. A ticket describes the problem; the implementer designs the solution.

### 2. Write acceptance criteria

Derive measurable, testable criteria from the description. Each criterion must be verifiable — something that can be ticked off with a test or a manual check. Aim for 2–5 criteria.

Good criterion: `A GET /orders?format=csv request returns a valid CSV file with all order fields`
Bad criterion: `The export feature works`

If the description implies an edge case or error state, add it: `A request with an unsupported format returns 400 with a machine-readable error code`

### 3. Choose a filename

Generate a kebab-case filename from the problem description. Keep it under 50 characters. Omit articles (a, the, an).

Examples:
- `add-csv-export-to-orders-api.md`
- `fix-login-500-on-plus-sign-email.md`
- `allow-users-to-set-display-name.md`

## Default ticket format

If no existing format is found, use:

```markdown
---
title: {Title in sentence case}
status: todo
type: {feature | bug | chore}
created: {YYYY-MM-DD}
---

## What

{1–3 sentences describing the problem or missing capability. What is wrong or absent?}

## Why

{1–2 sentences on the motivation. What is the impact on users or the system?}

## Acceptance criteria

- [ ] {Specific, testable criterion}
- [ ] {Another criterion}
- [ ] {Edge case or error state, if applicable}

## Technical notes

{Optional. Likely affected files, integration points, or constraints surfaced from the codebase. Omit if none. Do not prescribe the implementation.}
```

Valid `type` values: `feature` (new capability), `bug` (something broken), `chore` (maintenance, cleanup, or non-user-facing improvement).

## Output

Write the ticket to `docs/tickets/{filename}` by default. If `--changes` is passed, write to `docs/changes/{filename}`. Create the directory if it does not exist.

After writing, print:

**Ticket created:** `{path}`
**Title:** {title}
**Type:** {type}
**Criteria:** {n}
**Ready to implement with:** `/complete-ticket {path}`

If `--inline` was passed, print the ticket content instead of writing, with a note showing the path it would be written to.

## Gotchas

- Write the problem, not the solution. A ticket that says "add a `convertToCSV` function in `src/utils/export.ts`" is over-specified — the implementer cannot make better choices. A ticket that says "orders can be downloaded as a CSV file" leaves room for the right implementation.
- Acceptance criteria must be testable. If a criterion cannot be verified by a test or a manual check, rewrite it until it can.
- Do not create a ticket for work that is already in progress (`status: doing`) without flagging the conflict. Duplicate doing-tickets cause split attention and merge conflicts.
- If the input is a multi-feature request, write one ticket per independent piece of work — not one ticket for everything. Tickets that span multiple unrelated changes are hard to review and hard to revert.
- Technical notes are optional and should be short. Their purpose is to save the implementer a grep — not to design the solution for them.
- If the directory `docs/tickets/` does not exist, create it. Do not silently fail or write to the project root.
- This skill pairs naturally with `/complete-ticket` (implementing the ticket once it is written), `/spec-to-backlog` (for larger features, generate a full backlog first — then use create-ticket for individual items not captured there), `/debug-issue` (use debug-issue to diagnose a bug, then create-ticket to record the fix scope before implementing), and `/write-changelog` (the full build workflow: create-ticket → complete-ticket → write-changelog).
