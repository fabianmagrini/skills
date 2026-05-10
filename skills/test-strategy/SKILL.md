---
name: test-strategy
description: Audit the current test pyramid, identify imbalances and coverage gaps, and produce a recommended test strategy with tooling, coverage targets, and a prioritised improvement plan.
compatibility: Requires Read, Glob, Grep for local codebases.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Audit the existing tests and produce a recommended test strategy with an actionable improvement plan.

## Determine the target

Accept any of:
- No argument — audit the full repository
- A directory: `src/services/payments/`, `packages/api/`
- A layer or concern: `integration tests`, `e2e coverage`

If a path is given, scope the audit to that directory. Note that a scoped audit cannot assess the full pyramid balance — flag this limitation.

## Discovery steps

### 1. Test framework and runner
- Read `package.json`, `pyproject.toml`, `go.mod`, `pom.xml` — identify the test runner (`jest`, `vitest`, `pytest`, `go test`, `junit`) and any testing libraries (`testing-library`, `supertest`, `playwright`, `cypress`, `testcontainers`)
- Glob for test config files: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `conftest.py`, `playwright.config.*`, `cypress.config.*`
- Read the config to understand: test file patterns, coverage reporter, timeout settings, setup files

### 2. Test inventory
Glob for test files using the patterns found in config, or defaults:
- Unit/component: `**/*.test.{ts,tsx,js,jsx}`, `**/*.spec.{ts,tsx,js,jsx}`, `**/test_*.py`, `**/*_test.go`
- Integration: `**/integration/**`, `**/int/**`, `**/*.integration.test.*`
- E2E: `**/e2e/**`, `**/cypress/**`, `**/playwright/**`, `**/*.e2e.test.*`
- Contract: `**/pacts/**`, `**/*.pact.*`, `**/consumer/**`, `**/provider/**`
- Performance/load: `**/k6/**`, `**/artillery/**`, `**/locust/**`, `**/*.perf.*`

Count files at each level. For large repos, count is sufficient — do not read every test file.

### 3. Source coverage
- Glob for all source files (excluding tests, node_modules, dist)
- For each significant source directory, check whether a corresponding test file exists
- Identify source files with no test coverage at all — these are the highest-priority gaps

### 4. Coverage tooling
- Grep for coverage configuration: `istanbul`, `nyc`, `c8`, `coverage-v8`, `coverage.py`, `go cover`
- Check whether a coverage threshold is configured (enforced minimum %)
- Check whether coverage runs in CI (look for `--coverage` flag in CI pipeline commands)

### 5. CI test configuration
- Glob for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`
- Identify: what test levels run on PR, what runs on merge/nightly, whether tests are parallelised, whether flaky test retry is configured
- Note: if only unit tests run on PR and integration tests are nightly, integration failures are discovered late

### 6. Test quality signals
Read 3–5 representative test files across different levels. Look for:
- **Test isolation** — do unit tests mock I/O (database, HTTP)? Integration tests should not mock external services — they should use real dependencies (test containers, local stubs)
- **Assert specificity** — are assertions specific (`expect(result.id).toBe(42)`) or vague (`expect(result).toBeTruthy()`)
- **Test naming** — do test names describe behaviour or just method names?
- **Flakiness signals** — `sleep`, `setTimeout`, `retry`, `waitFor` without deterministic conditions, date/time dependencies
- **Test data management** — is test data hardcoded, factory-generated, or seeded? Is cleanup handled?

## Pyramid classification

Based on the inventory, classify the current test distribution:

**Test Pyramid** (ideal for most server-side systems)
```
        /\
       /E2E\        ← few, slow, expensive
      /------\
     / Integr \     ← moderate
    /----------\
   /    Unit    \   ← many, fast, cheap
  /--------------\
```

**Test Trophy** (ideal for UI-heavy or frontend systems)
```
     [  E2E   ]      ← few
   [ Integration ]   ← most
     [  Unit  ]      ← some
   [ Static/Types ]  ← free
```

**Testing Honeycomb** (ideal for microservices)
```
   [  E2E  ]         ← few cross-service
[ Component/Service ] ← most (within service boundary)
   [ Unit ]           ← targeted, for complex logic only
```

**Anti-patterns to flag:**
- **Ice cream cone**: many E2E, few unit — slow, brittle CI
- **Cupcake**: all unit, no integration — fast but misses integration bugs
- **No tests**: self-explanatory

Recommend the most appropriate pattern for the architecture and note why.

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/test-strategy.md`.

### Test Strategy: `{target}`

**Current State**

| Level | Files | Est. tests | Framework |
|-------|-------|------------|-----------|
| Unit | {n} | ~{n} | {framework} |
| Integration | {n} | ~{n} | {framework} |
| E2E | {n} | ~{n} | {framework} |
| Contract | {n} | ~{n} | {framework or "none"} |
| Performance | {n} | ~{n} | {framework or "none"} |

**Current pyramid:** {Pyramid / Trophy / Honeycomb / Ice cream cone / Cupcake / No tests}

**Coverage tooling:** {configured / not configured} — threshold: {enforced % or "none"}

**CI test gates:** {what runs on PR vs nightly}

---

**Coverage Gaps**

Source paths with no test coverage:
- `{path}` — {why this is high priority}

---

**Test Quality Findings**

> **[HIGH/MEDIUM/LOW] Category — Short title**
> What was observed and why it is a problem.
> *Recommendation:* Specific fix.

Categories: `Isolation`, `Assertion quality`, `Test naming`, `Flakiness`, `Test data`, `Missing level`.

---

**Recommended Strategy**

**Target pattern:** {Pyramid / Trophy / Honeycomb} — {one sentence rationale}

**Target distribution:**

| Level | Current | Target | Notes |
|-------|---------|--------|-------|
| Unit | {n} files | {n} files | {what to add or remove} |
| Integration | {n} files | {n} files | {what to add or remove} |
| E2E | {n} files | {n} files | {what to add or remove} |

**Coverage targets:**

| Scope | Target | Enforcement |
|-------|--------|-------------|
| Overall | {e.g. 80%} | CI threshold |
| Critical paths | {e.g. 95%} | Manual review |
| New code | {e.g. 90%} | CI threshold on diff |

**Tooling recommendations:**

| Gap | Recommended tool | Why |
|-----|-----------------|-----|
| {e.g. Integration DB tests} | {e.g. Testcontainers} | {reason} |
| {e.g. Contract testing} | {e.g. Pact} | {reason} |

---

**Prioritised Improvement Plan**

Ordered by risk reduction value:

1. **{Action}** — level, specific gap, why it matters most.

**Quick wins** (low effort, high confidence):
- {Specific test file or module to add tests to, and what to cover}

## Gotchas

- Do not recommend 100% coverage as a target. High coverage with low-quality assertions is worse than lower coverage with specific, meaningful tests. Coverage is a floor, not a goal.
- Integration tests should test the real integration — mocking the database in an "integration test" is just a slow unit test. Flag this pattern when found.
- E2E tests are not a substitute for integration tests. If the pyramid is inverted, recommend moving coverage down the stack, not removing E2E tests.
- Flaky tests are a strategy problem, not just a technical one. A flaky test that is retried rather than fixed trains the team to ignore failures.
- Test naming matters for diagnosis. A test named `test_user` that fails tells you nothing. A test named `test_user_cannot_access_admin_endpoint_without_role` tells you everything.
- Performance testing absence is worth flagging but should not block other priorities unless the system has known latency requirements.
- If no tests exist at all, the improvement plan must start with characterization tests for the highest-risk paths — not a greenfield test suite.
- This skill pairs naturally with `/write-tests` to implement specific gaps identified in the strategy, and `/platform-readiness` which includes test coverage as part of its CI/CD pillar assessment.
