---
name: review-code
description: Perform a structured code review of a file or function, covering correctness, security, readability, edge cases, and test coverage.
compatibility: Requires Read, Glob, Grep tools for local paths.
allowed-tools: Read Glob Grep
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-04-06
---

Review the target code and produce a structured, actionable report.

## Determine the target

Accept any of:
- A file path: `src/auth/middleware.ts`
- A function or class name: `UserService.createUser`
- A directory: `src/payments/`

For a file path, read the file directly.
For a function/class name, use Grep to locate it, then read the containing file.
For a directory, Glob for source files and read the most significant ones.

Also read related files where relevant: tests, types, callers, schema definitions.

## What to evaluate

Work through each dimension in order:

1. **Correctness** — Does the code do what it appears to intend? Look for logic errors, off-by-one errors, incorrect conditionals, broken error handling.

2. **Security** — Check for OWASP Top 10 issues: injection (SQL, command, XSS), broken auth, insecure direct object references, sensitive data exposure, missing input validation at system boundaries.

3. **Edge cases** — What happens with null/undefined/empty inputs, empty collections, concurrent access, unexpected types, or large inputs?

4. **Readability** — Are names clear? Is complexity justified? Are there long functions that should be split? Is control flow easy to follow?

5. **Test coverage** — Are there tests? Do they cover the happy path and key failure modes? Are there obvious gaps?

6. **Performance** — Any obvious N+1 queries, unnecessary re-computation, or missing indexes? Only flag real concerns, not speculative ones.

## Output format

Respond inline — do NOT write a file.

### Code Review: `{target}`

**Summary**
One paragraph overall assessment — severity, main themes, whether the code is safe to merge/use.

**Findings**

Use this format for each finding:

> **[SEVERITY] Category — Short title**
> Description of the issue and why it matters.
> ```
> // Problematic code snippet (if short)
> ```
> Suggested fix or approach.

Severity levels: `CRITICAL` (must fix before use), `MAJOR` (should fix), `MINOR` (worth improving), `NIT` (optional polish).

**What looks good**
Brief bullet list of things done well — this anchors the review and is not filler.

**Suggested next steps**
Ordered list of the most important actions to take.

## Gotchas

- Do not invent findings. If the code looks correct, say so.
- Do not flag style issues as MAJOR — they are NITs unless the project has a linter that enforces them.
- Read tests before flagging missing coverage — they may exist in a separate file.
- Do not recommend adding comments to self-evident code.
