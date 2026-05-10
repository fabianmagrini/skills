---
name: research-codebase
description: Research and produce comprehensive documentation for a codebase from a GitHub URL or local path. Use when asked to research, explore, document, or understand a project's architecture, tech stack, data model, or setup.
compatibility: Requires internet access for GitHub URLs. Requires Read, Glob, Grep tools for local paths.
allowed-tools: Read Glob Grep WebFetch Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Research and document the target codebase, then write a `{repo-name}-docs.md`
file in the current working directory.

## Determine the target type

**GitHub URL** (`https://github.com/owner/repo` or `owner/repo` format):
1. Raw base: `https://raw.githubusercontent.com/{owner}/{repo}/main/`
2. API base: `https://api.github.com/repos/{owner}/{repo}/contents/`

Fetch in parallel:
- `README.md` (try `main` then `master`)
- Root manifest: `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / `pom.xml`
- API root listing to discover top-level directories
- API listings for `src/`, `packages/`, `services/`, `apps/`, `lib/`
- Key configs: `docker-compose.yml`, `compose.yaml`, `turbo.json`, `nx.json`, `.github/workflows/`
- Each discovered service/package's own manifest

**Local path:**
1. List directory tree 2–3 levels deep
2. Read `README.md`, root manifests, and key config files
3. For monorepos, read each sub-package manifest
4. Read representative source files from `src/`, `lib/`, or the primary entry point

## What to extract

Gather enough to answer all of these:

- **Purpose** — what the project does and why it exists
- **How it works** — architecture, major components, data flow
- **Tech stack** — languages, frameworks, runtime, key libraries
- **Project structure** — annotated 2–3 level directory tree
- **Services / packages** — for monorepos, what each piece does and its interface
- **Infrastructure** — databases, queues, storage, external services
- **Data model** — schema files, ORM models, key entities
- **How to run it** — prerequisites, setup steps, dev commands, environment variables
- **Build / test / deploy** — pipeline, test commands, CI/CD

## Output format

Write `{repo-name}-docs.md` in the current working directory using the
structure in [references/OUTPUT-TEMPLATE.md](references/OUTPUT-TEMPLATE.md).

After writing the file, print the file path and a 5–10 bullet summary of the
most important things learned.

## Examples

**Research a GitHub repo by URL:**
```
/research-codebase https://github.com/anthropics/anthropic-sdk-python
```
Produces `anthropic-sdk-python-docs.md` in the current directory.

**Research a GitHub repo by owner/repo shorthand:**
```
/research-codebase vercel/next.js
```
Produces `next.js-docs.md`.

**Research a local project:**
```
/research-codebase /path/to/my/project
```
Produces `project-docs.md` using local file reads.

**Expected output:** A single Markdown file with sections covering Overview, Architecture, Repository Structure, Tech Stack, Data Model, Development Setup, and Available Commands. Sections that don't apply are omitted.

## Gotchas

- Try `main` first, then `master` for GitHub raw content URLs — many older
  repos still use `master`.
- GitHub API returns 403 for rate-limited or certain tree endpoints; fall back
  to fetching individual known paths.
- For monorepos, always fetch sub-package manifests — the root manifest rarely
  describes the full picture.
- Omit output sections that don't apply (e.g. skip Services for single-package
  repos, skip Infrastructure if there's none).
- This skill pairs naturally with `/explain-codebase` (for a quick inline answer rather than a full documentation file) and `/context-engineering` (the research output is a good source for generating an agent context file).
