---
name: summarise-pr
description: Summarise a GitHub pull request — its purpose, key changes, and review considerations — given a URL or owner/repo#number reference.
compatibility: Requires internet access.
allowed-tools: WebFetch WebSearch
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Summarise the target GitHub pull request clearly and concisely — covering purpose, change type, key files, and what a reviewer should focus on.

## Determine the target

Accept any of these formats:
- Full URL: `https://github.com/owner/repo/pull/123`
- Shorthand: `owner/repo#123`
- PR number alone when the repo is known from context: `#123`

Derive the API endpoints:
- Metadata: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}`
- Files: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files`
- Comments: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}/comments`
- Commits: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}/commits`

## Discovery steps

Work through each step in order before writing the summary. The summary must be grounded in what the PR actually contains — not derived from the title alone.

### 1. Read the PR description first

Fetch PR metadata. Read the title and body before looking at the diff. The description often explains intent that the code does not make obvious — the "why" behind the "what".

If the body is empty, note this — it is a reviewer experience gap. Fall back to commit messages to infer intent.

### 2. Classify the change type

Based on the title, labels, and description, classify the primary change type:

| Type | Indicators |
|------|-----------|
| **Feature** | New capability, new endpoint, new UI component |
| **Bug fix** | Fixes a defect, restores expected behaviour |
| **Refactor** | Restructures code without changing behaviour |
| **Performance** | Optimisation, caching, query improvement |
| **Security** | Vulnerability fix, auth change, input validation |
| **Chore** | Dependency update, CI change, configuration, tooling |
| **Docs** | Documentation only |
| **Breaking change** | Changes public API, removes fields, alters contracts |

A PR may span multiple types — note the primary type and list secondary types.

### 3. Read the file list

Fetch the changed files list. Group files by area:
- **Source** — application logic files
- **Tests** — test files (presence or absence is significant)
- **Config / infra** — CI, Docker, Kubernetes, Terraform, package manifests
- **Docs** — documentation, changelogs, READMEs
- **Generated** — lock files, build artifacts (usually safe to skim)

Note: if tests are absent and the PR adds or modifies logic, flag this explicitly in Review considerations.

### 4. Identify the highest-impact files

From the file list, identify the 3–5 files that carry the most risk or represent the core of the change. These are the files a reviewer must read in depth. Prioritise:
- Files with large diff sizes (many additions/deletions)
- Files in security-sensitive paths (auth, payments, session, crypto)
- Files that change public interfaces (API routes, exported functions, schema)
- Files with no corresponding test change

### 5. Read open review comments

Fetch review comments. Identify:
- Unresolved threads (open questions that have not been addressed)
- Change requests that may not yet be satisfied
- Approvals already given (reduces review burden)

### 6. Assess review complexity

Based on the above, classify the review complexity:
- **Quick** — < 5 files, single area, tests present, clear description
- **Standard** — 5–20 files, 1–2 areas, mostly covered by tests
- **Deep** — 20+ files, cross-cutting change, or high-risk area requiring careful reading

## Output format

Respond inline — do NOT write a file.

### {PR title} — {owner/repo}#{number}

**Author:** {author} | **Status:** {Open / Merged / Closed} | **Branch:** `{head}` → `{base}`
**Type:** {Feature / Bug fix / Refactor / Performance / Security / Chore / Docs / Breaking change}
**Review complexity:** {Quick / Standard / Deep}

---

**Purpose**

{1–2 paragraphs: what this PR does and why, synthesised from the title, description, and commit messages. Focus on the user-visible or system-level impact, not the implementation details.}

**Key changes**

Bullet list of the most significant changes, grouped by area. Skip trivial changes (formatting, lock file updates, generated files) unless they are the primary point of the PR:

- **{Area}:** {what changed and why it matters}

**Files to review**

The 3–5 files that carry the most risk or represent the core of the change — a reviewer should read these in depth:

| File | Why it matters |
|------|---------------|
| `path/to/file.ts` | {e.g. Changes the auth middleware — all requests pass through this} |

**Review considerations**

Bullet list of things a reviewer should pay attention to. Be specific — a vague "check for edge cases" is not useful:

- {e.g. The pagination logic does not handle an empty result set — `items[0]` will throw if the query returns nothing}
- {e.g. No tests cover the error path when the external API call fails}
- {e.g. The new field `user.role` is returned in the API response — check whether this leaks privilege information}

If no concerns are apparent, say so explicitly: "No significant review concerns identified."

**Open questions**

Unresolved review comment threads, if any. If none, omit this section.

---

## Gotchas

- GitHub API returns 403 for unauthenticated requests on private repos — note this and ask the user to provide a token or use the GitHub CLI (`gh pr view {number}`).
- Large PRs (100+ files) may hit API pagination — summarise from the first page, note the PR is large, and recommend the reviewer use `gh pr diff` locally.
- If the PR body is empty, rely on commit messages and file changes to infer purpose — but flag the missing description as a reviewer experience gap.
- A PR that modifies logic without adding or modifying tests is almost always worth flagging in Review considerations, regardless of what the test coverage looks like overall.
- Do not summarise a PR as "minor" or "low risk" based on line count alone. A 3-line change to an auth middleware or a database migration carries more risk than a 300-line new feature with full test coverage.
- Breaking changes must be called out prominently — a reviewer who misses a breaking change will not catch it until users are affected.
- This skill pairs naturally with `/review-code` (for a thorough code review after the summary identifies the key files to focus on) and `/write-changelog` (summarise individual PRs to produce better-quality changelog entries than raw commit messages alone).
