---
name: debug-issue
description: Diagnose a bug, error, or unexpected behaviour — given a symptom, stack trace, or error message — by reading relevant source, checking recent changes, and producing a ranked suspect list with specific fix recommendations.
compatibility: Requires Read, Glob, Grep, Bash for local codebases. Accepts a symptom description alone without file access.
allowed-tools: Read Glob Grep Bash
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Narrow from symptom to root cause and produce a specific, actionable fix recommendation.

## Determine the target

Accept any of:
- An error message or stack trace: `TypeError: Cannot read properties of undefined (reading 'id')`, `panic: runtime error: index out of range`
- A symptom description: `checkout fails after adding a coupon`, `users are being logged out randomly`, `emails not sending in staging`
- A file or function: `src/payments/processor.ts`, `OrderService.submit()`
- A combination: `src/auth/session.ts — users logged out after 5 minutes despite active sessions`

If a stack trace is provided, extract the top frame file and line number as the starting point for source reads.

If no local path can be inferred, work from the symptom description alone — state assumptions explicitly and structure the investigation around confirming or ruling them out.

## Discovery steps

### 1. Parse the error

From the symptom or stack trace, extract:
- **Error type** — what kind of failure: null dereference, assertion failure, network error, validation error, race condition, configuration mismatch
- **Entry point** — where in the stack did control enter the failing path (route, job, event handler)
- **Failure point** — the specific file and line that threw or produced the wrong result
- **Reproduction conditions** — when does this happen: always, intermittently, under specific input, in a specific environment

### 2. Read the failing path

Starting from the failure point, read up and down the call stack:
- Read the file and function that threw the error
- Read the callers of that function — trace back to the entry point (route handler, job trigger, event listener)
- Read any data transformations between the entry point and the failure — look for where a value could become null, undefined, incorrect, or missing

### 3. Check recent changes

Run `git log --oneline -20` on the relevant files to find changes made recently:

```bash
git log --oneline -20 -- {file-path}
```

For the most recent changes to suspect files, run `git show {hash}` to read the diff. A regression is most often caused by the last change to the affected code.

### 4. Search for related patterns

Grep for the failing symbol, function, or error string across the codebase:

```bash
# Find all callers of the failing function
grep -rn "{functionName}" src/

# Find all places the error message is produced
grep -rn "{error string}" .
```

Check whether similar patterns exist elsewhere — if the bug is present in one place, it may exist in analogous code paths.

### 5. Check environment and configuration

If the bug is environment-specific (staging, production, one user's machine):
- Read `.env.example`, `docker-compose.yml` env sections, or Kubernetes ConfigMap references
- Grep for feature flag checks near the failure point (`if (flags.featureName)`, `LaunchDarkly`, `Unleash`)
- Grep for environment conditionals (`process.env.NODE_ENV`, `os.environ`, `os.Getenv`) in the failing path
- Check whether the issue could be a missing or differently-valued environment variable

### 6. Read the tests

Glob for test files covering the failing code:
- Read existing tests to understand the expected behaviour — the bug may be a missing edge case
- Check whether a test for the exact failure scenario exists and is passing — if so, the bug is a runtime condition not covered by tests

### 7. Check dependencies and contracts

If the failure is at a boundary (external API, database, queue, imported library):
- Read the integration point — what does the code expect the external system to return?
- Grep for recent version changes in the manifest (`package.json`, `go.mod`, `requirements.txt`) — a dependency update may have changed a contract
- Check whether the error occurs in a retry path, a callback, or an async handler where errors are swallowed

## Output format

Respond inline — do NOT write a file unless the user passes `--save`.

### Debug Report: `{symptom or file}`

**Error Summary**

1–2 sentences: what is failing, where it fails, and under what conditions.

**Reproduction path**

The sequence of events that leads to the failure:
1. {Entry point — e.g. `POST /api/checkout` called with coupon code}
2. {Intermediate step — e.g. `OrderService.applyDiscount()` fetches coupon}
3. {Failure — e.g. `coupon.discount` is undefined when coupon is expired}

**Suspects**

Ordered by likelihood. For each:

> **[HIGH/MEDIUM/LOW] Category — Short title**
> What the issue is, where it appears in the code (`file:line`), and why it causes the symptom.
> *Evidence:* Specific line, grep result, or git diff that supports this suspicion.
> *Fix:* Concrete, specific change — guard clause, null check, config value, query fix, dependency pin.

Categories: `Null/undefined`, `Race condition`, `Configuration`, `Dependency change`, `Missing guard`, `Contract violation`, `Environment mismatch`, `Logic error`, `Missing error handling`, `State mutation`.

**Root cause confidence**

| Suspect | Confidence | Evidence strength |
|---------|-----------|------------------|
| {Short title} | HIGH / MEDIUM / LOW | {What was found vs what is assumed} |

**Recommended fix**

The single most likely fix, with the specific file and change:

```{language}
// file: {path}:{line}
// Before:
{current code}

// After:
{fixed code}
```

If the fix cannot be determined from static analysis alone, state what runtime information is needed (log output, specific input value, environment variable dump) and how to capture it.

**Verification steps**

How to confirm the fix works:
1. {Specific test to run or assertion to check}
2. {Edge case to verify — e.g. expired coupon, null user, empty cart}
3. {Regression check — what existing tests cover adjacent behaviour}

**If unresolved**

What to collect next if the root cause is still unclear:
- Specific log statements to add and what to look for
- Specific breakpoint location and what variable to inspect
- Reproduction script or minimal repro case to isolate the issue

## Gotchas

- Do not guess at the root cause without reading the code. "It might be a race condition" without reading the async path is speculation, not diagnosis.
- The most recent git change to a file is the most likely cause of a regression. Always check `git log` on the affected files before exploring further.
- Null/undefined errors are almost never caused by the line that threw — they are caused by where the null was introduced upstream. Read the callers, not just the failure point.
- Environment-specific bugs are almost always configuration, feature flags, or data differences — not code differences. Rule these out before reading source.
- If the bug is intermittent, suspect: race conditions, uninitialized state, external service timeouts, or time/date dependencies. These require different investigation strategies than deterministic bugs.
- Do not recommend adding a null check as the fix if the null represents a genuine unexpected state — a null check would hide a bug, not fix it. Find why the null exists and fix that.
- A fix that is not verified by a test will regress. Always include a verification step that either uses an existing test or identifies a specific test to write.
- This skill pairs naturally with `/review-code` (reviewing the fix before merging), `/write-tests` (adding a regression test for the bug), and `/incident-review` (when the bug caused a production incident and a postmortem is warranted).
