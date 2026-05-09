---
name: context-engineering
description: Generate or audit an agent context file (CLAUDE.md or equivalent) for a codebase — extracting project conventions, commands, architecture, tool permissions, and anti-patterns from the actual code.
compatibility: Requires Read, Glob, Grep for local codebases. Best run from the repository root.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Generate or audit an agent context file grounded in what the codebase actually contains.

## Determine the mode

**Generate mode** (default) — create a new context file from scratch:
- `/context-engineering` — generate for the current repository
- `/context-engineering src/services/payments/` — generate scoped to a subdirectory

**Audit mode** — review and improve an existing context file:
- `/context-engineering audit` — audit the existing `CLAUDE.md` at the repo root
- `/context-engineering audit path/to/CLAUDE.md` — audit a specific file

In generate mode, check whether a context file already exists before writing. If one exists, switch to audit mode and note the switch.

## Context file naming

The target filename depends on the agent. Common conventions:
- Claude Code: `CLAUDE.md`
- Gemini CLI / Google agents: `GEMINI.md`
- OpenCode: `.opencode/instructions.md`
- Generic: `AGENTS.md` or `.agent/context.md`

Default to `CLAUDE.md` at the repository root unless the user specifies otherwise or another convention is detected in the repo.

## Generate mode: Discovery steps

Read the codebase systematically before writing. Do not write placeholder content — every section must be grounded in what was actually found.

### 1. Project identity
- Read `README.md` — purpose, architecture overview, key links
- Read root manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`) — name, description, language, runtime version

### 2. Commands
- Read `package.json` `scripts`, `Makefile`, `justfile`, `taskfile.yaml`, or `pyproject.toml` `[tool.poetry.scripts]` / `[project.scripts]`
- Extract the actual commands for: build, test, lint, format, run dev server, run single test file
- Note any environment variable requirements (`dotenv`, `.env.example`, `README` setup steps)

### 3. Repository structure
- Glob top-level directories and read their purpose from README or package manifests
- For monorepos, identify workspace packages (`pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`)
- Note the key directories: where source lives, where tests live, where config lives

### 4. Tech stack and architecture
- Identify: primary language, framework, test runner, bundler, ORM/database client, HTTP client, state management, CSS approach
- Note any significant architectural patterns: monorepo, microservices, layered architecture, event-driven, etc.

### 5. Code conventions
- Read 3–5 representative source files across different layers
- Identify: naming conventions (camelCase, snake_case, PascalCase per context), file naming patterns, import style (barrel files, direct imports), error handling pattern, async pattern (async/await, callbacks, promises)
- Read linting/formatting config (`.eslintrc*`, `.prettierrc*`, `pyproject.toml [tool.ruff]`, `golangci.yml`) — note any non-default rules that affect how code should be written

### 6. Testing conventions
- Glob for test files (`**/*.test.*`, `**/*.spec.*`, `**/test_*.py`)
- Read 1–2 representative tests — note framework, assertion style, file co-location vs separate directory, mocking approach, fixture patterns
- Check for test utilities or custom matchers in `test/`, `__tests__/`, `testutils/`

### 7. CI/CD and tooling
- Glob `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`
- Note: what runs on PR (lint, test, build), what runs on merge, any required checks
- Note any pre-commit hooks (`.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`)

### 8. Existing agent context
- Check for existing `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.claude/`, `.opencode/`
- If found, switch to audit mode

## Generate mode: Output format

Write to `CLAUDE.md` (or the detected/specified filename) at the repository root.

```markdown
# {Project Name}

{1–2 sentence description of what this project is and does.}

## Architecture

{2–4 sentences on the high-level architecture: what type of system it is, the major components, and how they relate. Include the tech stack.}

## Repository Structure

```
{annotated directory tree, 2 levels deep, with one-line descriptions of key directories}
```

## Commands

```bash
# Development
{dev server command}

# Build
{build command}

# Test
{test command}
{single test file command}

# Lint / Format
{lint command}
{format command}
```

{Note any required environment setup, e.g. "Copy .env.example to .env before running locally."}

## Code Conventions

- **Language / runtime:** {e.g. TypeScript 5.x, strict mode, ESM}
- **Naming:** {e.g. camelCase for variables/functions, PascalCase for components/classes, kebab-case for files}
- **Imports:** {e.g. barrel imports from index.ts, no circular imports}
- **Error handling:** {e.g. throw typed errors, never swallow errors silently}
- **Async:** {e.g. async/await throughout, no raw Promise chains}
- **{Other notable convention found in the code}**

## Testing

- **Framework:** {e.g. Vitest + Testing Library}
- **Location:** {e.g. co-located with source as \`*.test.ts\`}
- **Style:** {e.g. describe/it blocks, AAA pattern, no testing implementation details}
- **Mocking:** {e.g. vi.mock for modules, MSW for HTTP}
- **Run a single test:** \`{command}\`

## CI

{What runs on PRs, what must pass before merge, any branch protection rules.}

## Anti-Patterns

Avoid these in this codebase:

- {Specific anti-pattern found or implied by conventions — e.g. "Do not use `any` type — use `unknown` and narrow"}
- {Another — e.g. "Do not import directly from internal subpaths of packages — use the public export"}
- {Another — e.g. "Do not add console.log to production code — use the structured logger at src/lib/logger.ts"}

## Key Files

| File | Purpose |
|------|---------|
| {path} | {one-line description} |

{Include: main entry point, config files, key abstractions, anything non-obvious that an agent would need to know about}
```

## Audit mode: What to evaluate

Read the existing context file in full, then read the codebase to verify each claim. Evaluate against these criteria:

**Accuracy** — Are the commands correct? Do they match what's in the manifests? Are the conventions described what's actually in the code?

**Completeness** — Are any of these missing or underspecified?
- Actual runnable commands (not generic placeholders like `npm test`)
- Repository structure with directory purposes
- Testing conventions including how to run a single test
- At least three specific anti-patterns
- Key files table

**Specificity** — Is the content generic (could apply to any project) or specific (names actual files, patterns, and tools found in this repo)? Generic content is low value.

**Freshness signals** — Are there commands, files, or conventions referenced that no longer exist? Flag these as stale.

**Missing context** — What important information about the codebase is not captured? What would an agent get wrong on their first day?

### Audit output format

Respond inline. Do not rewrite the file unless the user asks — provide a structured review and a list of suggested edits.

**Context File Audit: `{path}`**

**Overall assessment:** {one sentence — Ready / Needs work / Significant gaps}

**Findings**

> **[CRITICAL / MAJOR / MINOR] Category — Short title**
> What is wrong, missing, or stale, with evidence from the codebase.
> *Suggested fix:* Concrete replacement text or action.

**What is accurate and useful**

Bullet list of sections that are correct and specific — not filler.

**Suggested additions**

Content that is missing and should be added, with draft text where possible.

## Gotchas

- Do not write placeholder commands. If the build command cannot be determined from manifest files, say so and leave a `TODO` comment rather than writing `npm run build` speculatively.
- Anti-patterns must be specific to this codebase. Generic anti-patterns ("don't write spaghetti code") have no value. Read the code and find real conventions that an agent might violate.
- The Key Files table should include non-obvious files. `src/index.ts` being the entry point is obvious. The custom logger, the auth middleware, the database singleton — these are what an agent needs to know about.
- In audit mode, do not rewrite the file without being asked. A list of targeted fixes is more useful and less risky than a full rewrite.
- Context files go stale. If the last-updated date in the file is more than 3–6 months old, note it as a freshness risk and recommend a re-audit.
- For monorepos, a single root context file is often insufficient. Note whether per-package context files would add value.
- Agent context files are read at the start of every session. Brevity matters — a 500-line context file will be truncated or ignored. Prioritise the highest-signal content and omit what the agent can derive from reading the code.
