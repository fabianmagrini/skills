---
name: onboard-codebase
description: Produce a structured onboarding guide for a new engineer joining a project — covering architecture, local setup, key entry points, development workflow, and testing conventions — grounded in the actual codebase.
compatibility: Requires Read, Glob, Grep, Write for local codebases. Best run from the repository root.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Produce a structured onboarding guide grounded in the actual codebase — not a generic template — so a new engineer can be productive within their first day.

## Determine the target

Accept any of:
- A local path: `.`, `services/api`, `packages/auth`
- A service name: `user-service`, `billing-api` — glob for a matching directory
- No argument — run from the current working directory

Also accept:
- `--save` — write the guide to `docs/onboarding.md` (default when `docs/` exists)
- `--inline` — respond inline without writing a file

## Discovery steps

Work through each step before writing the guide. Every section must be grounded in what was actually found — not generic advice.

### 1. Read existing documentation

Glob for and read:
- `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`, `docs/` directory
- `.env.example`, `.env.sample` — reveals required environment variables and their purpose

Extract: project purpose, setup instructions, key commands, and onboarding notes already written. Do not duplicate what is well-documented — reference it and fill the gaps. If there is no README, flag this as a documentation gap in the guide.

### 2. Identify the tech stack

Glob for package manifests and language markers:
- `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `build.gradle`, `Gemfile`, `*.csproj`

Determine: primary language(s) and version, key framework(s) (Express, FastAPI, Gin, Next.js, Rails, Spring, etc.), and package manager (npm, pnpm, yarn, uv, poetry, cargo, etc.).

### 3. Map the project structure

List top-level directories and read 1–2 key files in each to understand their purpose. Focus on:
- Source directories (`src/`, `lib/`, `app/`, `cmd/`, `pkg/`, `internal/`)
- Test directories (`tests/`, `__tests__/`, `spec/`, `test/`)
- Config and infra (`.github/`, `docker/`, `terraform/`, `k8s/`, `config/`)
- Generated or vendored code (`vendor/`, `node_modules/`, `dist/` — note but skip reading)

Produce a directory map with a one-line description of each significant directory.

### 4. Find the entry points

Grep for main files, server initialization, and router definitions:
- `main.go`, `main.py`, `index.ts`, `server.ts`, `app.py`, `Program.cs`
- Route registrations: `router.get`, `app.route`, `@app.get`, `r.Handle`, `router.add`

Identify the 3–5 files a new engineer should read first to understand how the system works.

### 5. Read the CI/CD configuration

Glob for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Makefile`, `justfile`, `scripts/`.

Extract:
- How to run tests locally
- How to lint and type-check
- How to build and start the service
- What CI does on pull request and on merge to main

If a `Makefile` or `justfile` exists, read it — it often contains the canonical commands for local development.

### 6. Understand the test conventions

Find 2–3 test files in different areas. Determine:
- Test framework and assertion library
- File naming convention (`*.test.ts`, `*_test.go`, `test_*.py`)
- Where mocks and fixtures live
- How to run a single test vs. the full suite

### 7. Identify common development tasks

From the above, infer how a developer would:
- Add a new feature (which directories and layers are touched)
- Add or modify a test
- Run the service locally end-to-end
- Debug a failing request or test

## Output format

Write to `docs/onboarding.md` by default (create `docs/` if it does not exist). If `--inline` is passed, respond inline.

The guide must contain:

---

**Onboarding: {Project or Service Name}**

> Generated: {YYYY-MM-DD} — update this guide when the project structure changes significantly.

**What this is**

{1–2 sentences on what the service does and who uses it. Source from README or infer from the codebase.}

**Tech stack**

| Layer | Technology |
|-------|-----------|
| Language | {e.g. Go 1.22} |
| Framework | {e.g. Chi router} |
| Database | {e.g. PostgreSQL via pgx} |
| Testing | {e.g. Go testing + testify} |
| Build / CI | {e.g. GitHub Actions + Makefile} |

**Local setup**

Numbered steps from a fresh clone to a running service:

1. Prerequisites: {Go 1.22+, Docker, etc.}
2. Install dependencies: `{command}`
3. Copy env vars: `cp .env.example .env` — required: `{list required vars with a one-line description of each}`
4. Start: `{command}`

**Project structure**

```
{top-level directory tree with one-line descriptions}
```

{Short prose on the main split — e.g. "Business logic lives in `internal/`, HTTP handlers in `api/`, shared types in `pkg/`."}

**Entry points**

The files to read first:

| File | Why |
|------|-----|
| `{path}` | {e.g. Server initialization — where middleware and routes are registered} |

**Development workflow**

1. Create a branch from `main`
2. Make changes — {which layer to touch for a new endpoint / feature / model}
3. Run tests: `{command}`
4. Run lint: `{command}`
5. Open a PR — CI runs `{what}`

**Testing**

- **Framework:** {name}
- **Run all tests:** `{command}`
- **Run one test:** `{command}`
- **Test files:** `{path pattern}`
- **Mocks / fixtures:** `{location, or "none found"}`

**Common tasks**

For each identified pattern (add an endpoint, add a model, debug a failing test), give concrete steps — name the specific files to copy or modify, not generic advice.

**Further reading**

{Links to architecture ADRs, RFCs, or design docs if found in the repo. Omit if none.}

---

After writing, print:

**Onboarding guide written:** `{path}`
**Tech stack:** {language} / {framework}
**Entry points identified:** {n}
**Env vars documented:** {n}

## Gotchas

- Do not duplicate what the README already covers well. Link to it and fill the gaps — two sources of truth that diverge frustrate new engineers more than no documentation.
- If `.env.example` exists, document every variable in it. Missing environment variables are the most common cause of "it doesn't work on my machine."
- Test commands that differ from framework defaults (e.g. `make test` instead of `go test ./...`) are exactly what a new engineer gets wrong. Source these from the Makefile or CI config, not from convention.
- The "Common tasks" section must name specific files and commands for this project — not generic advice like "write your code, then test it."
- Generated files (`vendor/`, `node_modules/`, `dist/`, `*.pb.go`) waste a new engineer's time if they read them. Name them in the project structure section and mark them as generated/safe to ignore.
- The guide goes stale. Include the generation date and recommend updating it when the project structure changes significantly.
- If the project has no README and no CI config, note both gaps prominently — these are signals of a project that will be hard to onboard into regardless of this guide.
- This skill pairs naturally with `/explain-codebase` (for deep dives on specific components after initial orientation), `/map-api-flow` (to trace a specific request flow end-to-end), `/research-codebase` (to answer specific questions that arise during onboarding), and `/generate-runbook` (for operational procedures once the engineer is productive).
