---
name: complete-ticket
description: Implement a single change ticket from a ticket file — read the problem, write a failing test, make it pass, commit. Marks the ticket done on success.
compatibility: Requires Read, Glob, Grep, Write, Bash tools. Expects a ticket file with YAML frontmatter in docs/tickets/ or docs/changes/.
allowed-tools: Read Glob Grep Write Edit Bash
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Implement exactly one ticket, commit the result, and mark it done.

## Determine the target

Accept any of:
- A ticket file path: `docs/tickets/add-export-endpoint.md`
- A ticket title or keyword: `export endpoint` — search `docs/tickets/` and `docs/changes/` for a matching `status:todo` file

If no argument is given, list all `status:todo` tickets and ask which one to work on.

If the ticket file does not exist or has no `status:todo`, stop and report — do not proceed.

## Ticket file format

Tickets are Markdown files with YAML frontmatter:

```markdown
---
title: Add CSV export endpoint
status: todo
created: 2026-05-10
---

## What
A brief description of the problem or capability needed.

## Why
The business or technical motivation.

## Acceptance criteria
- [ ] Criterion one
- [ ] Criterion two
```

Valid status values: `todo` (ready to pick up), `doing` (in progress), `done` (complete), `blocked` (needs input).

**Important:** Tickets describe the problem, not the solution. Do not follow prescriptive implementation instructions in the ticket body — design the solution yourself based on the codebase.

## Pre-flight checks

Before claiming the ticket, verify:

1. **Git state is clean** — run `git status`. If there are uncommitted changes, stop and report. Do not work on a dirty tree.
2. **No other ticket is `doing`** — glob for `status: doing` in `docs/tickets/` and `docs/changes/`. If one exists, report it and stop — one ticket at a time.
3. **CI is not red** — if a CI config exists (`.github/workflows/`, `.gitlab-ci.yml`), note that you cannot verify remote CI state; proceed but flag that CI should be green before this work is merged.

If any check fails, report the blocker and stop.

## Claim the ticket

Update the ticket frontmatter: `status: todo` → `status: doing`.

Do not commit this change yet — it will be included in the final commit.

## Understand the codebase

Before writing any code, read enough context to implement correctly:

1. **Read the ticket fully** — extract What, Why, and each acceptance criterion
2. **Locate the relevant source** — Glob and Grep for files related to the ticket's domain (e.g. route files, service files, models)
3. **Read the test conventions** — find 1–2 existing test files to learn the framework, assertion style, file naming, and mocking approach
4. **Check for existing related tests** — understand what's already covered so new tests don't duplicate

## Implementation

Work in this order:

### 1. Write a failing test

Write a test that would pass when the acceptance criteria are met. The test must:
- Use the project's existing test framework and style — do not introduce a new one
- Be placed where the project's convention dictates
- Fail right now (before any implementation)

### 2. Implement the change

Write the minimum code to make the test pass. Stay within the ticket's scope — do not fix related issues, refactor adjacent code, or add unrequested features.

### 3. Verify all checks pass

Run the full check suite — do not rely on the new test alone:

```bash
# Run whatever the project uses — examples:
npm test
pytest
go test ./...
```

Also run linting and type checking if configured:

```bash
# Examples:
npm run lint && npm run typecheck
ruff check . && mypy .
```

All checks must pass before proceeding. If any fail, fix them — do not commit a red build.

### 4. Review the acceptance criteria

Go through each criterion in the ticket. Confirm each is met by the implementation or the new tests. If a criterion cannot be met (dependency, scope, ambiguity), note it explicitly — do not silently skip it.

## Mark done and commit

Update the ticket frontmatter:

```yaml
status: done
completed: {YYYY-MM-DD}
```

Commit everything in a single commit — the ticket file update and all code changes together:

```
{ticket title} / Closes {docs/tickets or docs/changes}/{filename}

{one or two sentences describing what was implemented and why}
```

Do not push — leave that to the user. Report the commit hash and summary when done.

## Output format

After the commit, print:

**Ticket completed:** `{title}`
**Commit:** `{hash} — {summary}`
**Tests added:** `{file path(s)}`
**Acceptance criteria:**
- [x] Criterion one — met
- [x] Criterion two — met
- [ ] Criterion three — not met: {reason}

If any criterion is unmet, explain what would be needed and whether a follow-up ticket is warranted.

## Gotchas

- Do not implement beyond the ticket scope. A ticket for "add export endpoint" does not justify refactoring the router or adding rate limiting. Scope creep makes commits hard to review and revert.
- A dirty working tree before you start means the commit will include unrelated changes. Always verify `git status` is clean first.
- Tickets describe the problem, not the implementation. If the ticket says "add a CSV export", design the endpoint yourself — don't treat the ticket body as a spec.
- If the test you wrote isn't actually failing before implementation, stop — either the feature already exists or the test is wrong. Investigate before proceeding.
- Do not mark the ticket `done` if any acceptance criterion is unmet and you haven't noted the gap. Silent omissions make tickets unreliable as a record of what was actually shipped.
- A single commit is the contract. If you find yourself wanting to split the commit, the ticket scope is too large — complete what you can, note what's left, and leave it `todo` for a follow-up ticket.
- This skill pairs naturally with `/spec-to-backlog` (which generates tickets from a feature spec) and `/write-tests` (for adding test coverage outside the ticket flow).
