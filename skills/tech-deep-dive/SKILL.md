---
name: tech-deep-dive
description: Deep-dive into one specific technology in the codebase — how this team configured it, where and how it's used, what patterns they apply, where they deviate from defaults, and how to work with it as a new contributor. Use when you already know the system exists and want to go deep on one piece of the stack.
compatibility: Requires Read, Glob, Grep for local paths. Agent subagent used for large codebases.
allowed-tools: Read Glob Grep WebFetch Write Agent
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-06-06
---

Zoom into one specific technology and teach everything about how this project uses it — configuration choices, usage patterns, project-specific abstractions, idiomatic vs. non-idiomatic usage, and a concrete contributor guide. This is the vertical complement to `/reverse-engineer` (whole-system horizontal analysis) and `/onboard-codebase` (whole-system onboarding). Reach for this skill after you know the lay of the land and want to go deep on one piece.

## Determine the target

Required:
- `{technology}` — the technology to deep-dive (e.g. `Redis`, `Prisma`, `React Query`, `NextAuth`, `Kafka`, `Tailwind`, `Vitest`)

Optional:
- `{path}` — scope the search to a subdirectory (e.g. `services/payments`, `packages/api`)
- `--save` — write output to `{technology}-deep-dive.md` in the current directory
- `--inline` — respond inline without writing a file (default)

If no path is given, search the entire working directory.

## Discovery steps

Work through each step before writing the analysis. Every claim must be grounded in evidence — cite specific file paths and line numbers where possible.

### 1. Confirm the technology is present

Identify which package or module provides this technology:
- Search the root manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pom.xml`) for the package name
- Note the version pinned — major version constrains which features and APIs are available
- Check for peer dependencies or companion packages (e.g. `@tanstack/react-query` + `@tanstack/react-query-devtools`)

If the technology is not found in any manifest, check for:
- A vendored copy (`vendor/`, `lib/third-party/`)
- A native runtime feature used without a package (e.g. browser `fetch`, Node `fs`)
- An infrastructure-level dependency (e.g. Redis as a sidecar, not imported in code)

State clearly what was found and where before proceeding.

### 2. Find the configuration

Locate where the technology is initialized and configured:

- Glob for dedicated config files: `**/{technology}.config.*`, `**/config/{technology}.*`, `**/.{technology}rc*`
- Grep for the technology's primary constructor or setup call (e.g. `new PrismaClient`, `createClient`, `configureStore`, `RedisClientType`)
- Read provider or plugin registration files: Next.js `app/layout.tsx`, Express `app.ts`, NestJS `app.module.ts`, Django `settings.py`

For each configuration site, note:
- Which options are set and which are left at their defaults
- Any environment variables that control behaviour
- Whether configuration is split across multiple files or centralized

### 3. Map all usage sites

Grep for the technology's primary import, exported client, or singleton across the codebase:

```
grep -r "{import pattern}" --include="*.ts" --include="*.js" --include="*.py" -l
```

Group the results by layer or domain:
- How many files use it?
- Which layers (controller, service, repository, component, hook, middleware)?
- Which domains or features use it most heavily?
- Are there any files that use it in unexpected or surprising places?

For large codebases (>50 usage sites), use an Agent subagent (`subagent_type: Explore`) for traversal rather than exhaustive Grep.

### 4. Identify key usage patterns

From the usage sites found, read a representative sample — at least 3–5 files across different layers and domains. Identify recurring patterns:

- What is the most common operation performed with this technology?
- Are there wrapper functions, custom hooks, or helper classes built on top of it?
- Is the technology used directly or always through an abstraction layer?
- Are there multiple different ways the technology is used, or is usage consistent?

For each distinct pattern found, note: what it does, where it appears, and whether it matches the technology's recommended usage.

### 5. Identify project-specific abstractions

Look for custom wrappers, extensions, or conventions layered on top of the technology:

- Grep for files that re-export the technology's types or client (barrel files, wrapper modules)
- Look for factory functions, singleton patterns, or custom hooks that encapsulate the technology
- Check for custom error handling, retry logic, or instrumentation added on top

For each abstraction found: explain what it wraps, why the team likely added it, and what it hides or changes from the raw technology API.

### 6. Check the test strategy

Find how the technology is handled in tests:

- Grep for the technology name in `**/__tests__/**`, `**/*.test.*`, `**/*.spec.*`, `**/tests/**`
- Determine: is the technology mocked, stubbed, or used against a real instance in tests?
- Note the test helper or factory used to set up / tear down the technology per test
- Check if there are dedicated integration or e2e tests that exercise the technology end-to-end

### 7. Infer evolution from git history

If git is accessible, run `git log --oneline --all -- "**/*{technology}*" | head -30` to find commits touching technology-related files.

Look for:
- Version bumps (major upgrades that changed the API)
- Configuration changes that hint at past pain points
- Files that were added as abstractions over time (bolted on rather than planned)
- Migration files that reveal a technology swap (e.g. switching from one ORM to another)

Flag every inference with **(inferred)**.

## Output format

Respond inline by default. Write to `{technology}-deep-dive.md` if `--save` is passed.

---

**Tech Deep-Dive: {Technology} in {Project Name}**

> Generated: {YYYY-MM-DD} · Version in use: `{version from manifest}`

---

### What it is and why this team chose it

{2–3 sentences: what this technology does, and why this team likely chose it over alternatives — grounded in the codebase context, not generic marketing copy.}

**Likely alternatives considered:** {1–2 alternatives and why this technology probably won}

---

### How it's configured

**Configuration files:**

| File | Purpose |
|---|---|
| `{path}` | {what this config file controls} |

**Key options set:**

| Option | Value | Default | Why changed |
|---|---|---|---|
| `{optionName}` | `{value}` | `{default}` | {reasoning, or "unknown **(inferred)**"} |

**Environment variables:**

| Variable | Purpose | Required? |
|---|---|---|
| `{VAR_NAME}` | {what it controls} | yes / no |

**What's left at defaults:** {options that are notably NOT configured — either because the defaults are good or the team hasn't needed to change them}

---

### Where it's used

**Usage summary:** {N} files across {layers/domains}.

| Layer / Domain | Files | Primary operation |
|---|---|---|
| `{layer}` | `{file1}`, `{file2}` | {e.g. "cache reads and writes"} |

**Usage map:**

```
{Top-level directory tree annotated with where the technology appears}
```

---

### Key Patterns

For each distinct pattern found:

**Pattern: {name}**

*What it does:* {one sentence}

*Where it appears:* `{path/to/file.ts}:{line}`, `{path/to/other.ts}:{line}`

*Simple explanation:* {how a junior engineer would understand it}

*Why this approach:* {reasoning — tradeoffs accepted, constraint addressed}

*Is this idiomatic?* {Yes / Partially / No — and if not, what the idiomatic alternative is}

---

### Project-Specific Abstractions

For each custom wrapper or abstraction:

**`{AbstractionName}`** in `{path/to/file}`

Wraps: {what raw API it wraps}

Adds: {what behaviour it introduces — error handling, logging, retry, type narrowing}

Why it likely exists: {reasoning}

Watch out for: {anything surprising about how this abstraction differs from the raw API}

---

### Test Strategy

**Approach:** {mocked / real instance / both — with which framework}

**Test setup:** `{path/to/test-helper or fixture}`

**To run tests that exercise this technology:**
```
{command}
```

**Coverage gaps:** {what is not tested — e.g. "error paths from the client are not tested anywhere"}

---

### Working With It as a Contributor

Concrete steps for the most common tasks — name specific files to touch, not generic advice.

**To add a new {common operation}:**
1. {Step 1 — e.g. "Add the schema definition in `prisma/schema.prisma`"}
2. {Step 2}
3. {Step 3}

**To modify an existing {common operation}:**
1. {Step 1}
2. {Step 2}

**To add a test that exercises this technology:**
1. {Step 1 — e.g. "Copy the setup from `tests/helpers/redis.ts`"}
2. {Step 2}

---

### Failure Modes and Gotchas

Project-specific issues — not generic technology gotchas from the docs.

- **{Gotcha}:** {what happens, where in the codebase it could bite you, `path/to/relevant/file`}

---

### Alternatives and Tradeoffs

| Alternative | Advantage over current choice | Why not chosen (inferred) |
|---|---|---|
| `{alternative}` | {what it does better} | {likely reason} |

**If starting today:** {one sentence on whether the current choice is still the right one, or what you might choose instead and why}

---

After writing (if `--save` is passed), print:

**Deep-dive written:** `{path}`
**Version analysed:** `{version}`
**Usage sites found:** {N} files
**Patterns identified:** {list}
**Key gotcha:** {one sentence}

## Examples

```
/tech-deep-dive Redis
```
Deep-dives into how the project uses Redis — client setup, key patterns, caching strategy, and contributor guide.

```
/tech-deep-dive Prisma services/api
```
Scopes the analysis to the `services/api` directory only.

```
/tech-deep-dive "React Query" --save
```
Writes the analysis to `React Query-deep-dive.md`.

```
/tech-deep-dive NextAuth --inline
```
Responds inline (same as the default).

## Gotchas

- **Technology names vary.** The package name may differ from the common name — `React Query` is the package `@tanstack/react-query`, `Prisma` is `@prisma/client`. Try both forms when grepping.
- **Abstractions hide the technology.** If usage sites are sparse but the technology is confirmed in the manifest, look for a wrapper module that encapsulates it — the real usage is one level up from the raw import.
- **Version matters more than usual.** A major version difference (e.g. Prisma 4 vs. 5, React Query v4 vs. v5) can mean entirely different APIs. Always confirm the version before drawing conclusions about available features or patterns.
- **Mocking ≠ real usage.** Test files often import a mock of the technology, not the real client. Confirm which files use the real instance vs. a test double when mapping usage.
- **Configuration split across environments.** Some technologies have a base config plus per-environment overrides (`config/base.ts`, `config/production.ts`). Read all layers before drawing conclusions about the final configuration.
- **Infrastructure-level technologies** (Redis, Kafka, PostgreSQL) are used in code via a client library. Make sure to deep-dive the client library's usage in code, not just the infrastructure definition in Docker or Terraform.
- This skill pairs naturally with `/reverse-engineer` (for the whole-system context before zooming into one technology), `/map-api-flow` (to trace how the technology participates in a specific request flow), and `/write-tests` (to add test coverage to usage patterns identified as untested).
