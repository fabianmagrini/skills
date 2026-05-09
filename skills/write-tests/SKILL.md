---
name: write-tests
description: Generate tests for a specified file, function, or class. Matches the project's existing test framework, style, and conventions.
compatibility: Requires Read, Glob, Grep tools for local paths.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-04-06
---

Write tests for the target code that fit naturally into the existing test suite.

## Determine the target

Accept any of:
- A file path: `src/utils/format.ts`
- A function or class name: `parseDate`
- A description: `the payment processor module`

Locate the target using Grep or Glob as needed, then read it fully.

## Understand the project's test conventions

Before writing anything, gather context:

1. Glob for existing test files (`**/*.test.*`, `**/*.spec.*`, `**/*_test.*`, `tests/**/*`)
2. Read 1–2 representative test files to learn:
   - Test framework (Jest, Vitest, pytest, Go testing, etc.)
   - Assertion style (`expect`, `assert`, `should`)
   - File naming and location convention (`src/__tests__/`, co-located, `tests/`)
   - Mocking approach (jest.mock, unittest.mock, etc.)
   - Any test helpers or fixtures used
3. Read the project manifest (`package.json`, `pyproject.toml`, etc.) to confirm the test runner and any relevant config

## What to generate

Cover these cases in order of priority:

1. **Happy path** — expected inputs produce expected outputs
2. **Edge cases** — null/undefined/empty, boundary values, zero, empty collections
3. **Error cases** — invalid inputs, thrown exceptions, rejected promises
4. **Integration points** — if the code calls external services or the database, write tests with appropriate mocks/stubs matching the project's style

Do not generate tests for private/internal helpers unless they are the explicit target.

## Output format

Write the test file to the location that matches the project's convention (co-located, `__tests__/`, `tests/`, etc.).

After writing, print:
- The file path written
- A bullet list of what each test group covers
- Any assumptions made (e.g. "assumed Jest based on package.json")
- Any cases that could not be tested without additional context

## Gotchas

- Match the existing style exactly — do not introduce a new framework or assertion style.
- Do not add tests that only verify implementation details (testing private state, exact call counts for internal calls).
- If the target has no existing tests, note this but still write tests based on the code's behaviour.
- If the code is untestable as-is (e.g. tight coupling, no dependency injection), note what refactoring would enable testing rather than writing poor tests.
