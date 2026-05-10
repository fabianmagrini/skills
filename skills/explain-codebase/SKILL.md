---
name: explain-codebase
description: Answer "what does this do?" for a codebase, directory, or file. Produces a concise inline explanation without writing a documentation file.
compatibility: Requires internet access for GitHub URLs. Requires Read, Glob, Grep tools for local paths.
allowed-tools: Read Glob Grep WebFetch
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-04-06
---

Explain the target codebase, directory, or file clearly and concisely. Respond inline — do NOT write a file. This is a lightweight alternative to `research-codebase` when the user just wants to understand something quickly.

## Determine the target

Accept any of:
- A GitHub URL or `owner/repo` shorthand → fetch README and root manifest
- A local directory path → list top-level structure, read README and manifest
- A local file path → read the file directly
- A function or class name → locate with Grep, read the containing file

## Scope of explanation

Match the depth to the target:

| Target | Explain |
|--------|---------|
| Full repo | Purpose, architecture in one paragraph, key technologies, how to run |
| Directory | What this directory is responsible for, how it fits into the larger project |
| File | What the file does, its main exports/functions, where it's used |
| Function/class | What it does, its parameters and return value, any important side effects |

## Output format

**For a repo or directory:**

### {Name}

**What it does**
1–2 paragraphs.

**Key components**
Bullet list of the most important files/directories and what each does.

**Tech stack**
One-liner: e.g. "Python 3.12 · FastAPI · PostgreSQL · deployed on AWS Lambda"

**How to run**
The minimal steps to get it running locally, if discoverable.

---

**For a file:**

### `{path/to/file}`

What this file does in 1–3 sentences. What it exports and how it's used.

---

**For a function or class:**

### `{FunctionName}` in `{path/to/file}`

What it does, its signature, and any non-obvious behaviour or side effects.

## Gotchas

- Keep it short. If the user wants comprehensive docs, they should use `/research-codebase`.
- Do not speculate about intent — describe what the code actually does.
- For GitHub targets, try `main` then `master` for raw content URLs.
- This skill pairs naturally with `/research-codebase` (when a full documentation file is needed rather than an inline explanation) and `/map-api-flow` (when the user needs to visualize how API calls flow through the code).
