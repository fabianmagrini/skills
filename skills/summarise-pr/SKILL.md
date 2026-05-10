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

Summarise the target GitHub pull request clearly and concisely.

## Determine the target

Accept any of these formats:
- Full URL: `https://github.com/owner/repo/pull/123`
- Shorthand: `owner/repo#123`

Derive:
- API endpoint: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}`
- Files endpoint: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files`
- Comments endpoint: `https://api.github.com/repos/{owner}/{repo}/pulls/{number}/comments`

## What to fetch

Fetch in parallel:
- PR metadata (title, body, author, base/head branches, labels, status)
- Changed files list (filename, status, additions, deletions)
- Review comments (for context on open questions)

## Output format

Respond inline — do NOT write a file.

### {PR title} — {owner/repo}#{number}

**Author:** {author} | **Status:** {state} | **Branch:** `{head}` → `{base}`

**Purpose**
One paragraph describing what this PR does and why, synthesised from the title and description.

**Key changes**
Bullet list of the most significant changes, grouped by area (e.g. API, UI, tests, config). Skip trivial changes like formatting or lock file updates unless they are the point.

**Files changed**
Summary table:

| File | Change |
|------|--------|
| path/to/file.ts | Added X, modified Y |

Limit to the most impactful files if there are more than 15.

**Review considerations**
Bullet list of things a reviewer should pay attention to: edge cases, missing tests, breaking changes, security implications, performance concerns. If none are apparent, say so.

**Open questions**
Any unresolved discussion threads from review comments, if present.

## Gotchas

- GitHub API returns 403 for unauthenticated requests on private repos — note this and ask the user to provide a token or use the GitHub CLI.
- Large PRs (100+ files) may hit API pagination; summarize from the first page and note that the PR is large.
- If the PR body is empty, rely on commit messages and file changes to infer purpose.
- This skill pairs naturally with `/review-code` (for a thorough code review after the summary identifies the key files to focus on) and `/write-changelog` (summarise individual PRs to produce better-quality changelog entries than raw commit messages alone).
