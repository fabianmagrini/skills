---
name: write-changelog
description: Generate a CHANGELOG entry for a release by reading git history, merged PR titles, and completed ticket files — grouped by change type and formatted to match the project's existing changelog convention.
compatibility: Requires Bash for git log access. Read, Glob, Grep for ticket files and existing CHANGELOG. Write to append to CHANGELOG.md.
allowed-tools: Read Glob Grep Bash Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Generate a structured CHANGELOG entry for a release, grounded in what actually changed.

## Determine the target

Accept any of:
- No argument — generate an entry from the latest tag to `HEAD`
- A version number: `1.3.0` — use as the new release version label
- A tag range: `v1.2.0..v1.3.0` — generate from that range
- A combination: `1.3.0 --from v1.2.0` — explicit version and base tag

Also accept:
- `--save` — append the entry to `CHANGELOG.md` (or `CHANGELOG.md`-equivalent found in the repo) rather than responding inline
- `--format keep-a-changelog|conventional|auto` — override format detection (default: `auto`)

If no version number is given, leave the version header as `[Unreleased]` and note that the user should fill it in before release.

## Discovery steps

### 1. Detect the existing CHANGELOG format

Glob for `CHANGELOG.md`, `CHANGELOG`, `HISTORY.md`, `RELEASES.md` at the repo root. Read the file if found.

Identify the format in use:

- **Keep a Changelog** — headings like `## [1.2.0] - 2026-05-01`, sections `### Added`, `### Fixed`, `### Changed`, `### Removed`, `### Deprecated`, `### Security`
- **Conventional Commits** — bullet list grouped by prefix: `feat:`, `fix:`, `refactor:`, `perf:`, `docs:`, `chore:`, breaking changes marked with `!` or `BREAKING CHANGE:`
- **Free-form** — prose paragraphs or unstructured bullet lists per release

If no existing changelog is found, default to **Keep a Changelog** format and note this.

Read the most recent 1–2 entries to understand: date format, bullet style (dash vs asterisk), link format for issue/PR references, whether commit hashes are included.

### 2. Determine the version range

```bash
# Find the most recent tag
git describe --tags --abbrev=0 2>/dev/null || echo "no-tags"

# List all tags chronologically
git tag --sort=-creatordate | head -5
```

If a `--from` tag is provided, use it. If not, use the most recent tag as the base. If there are no tags, use the initial commit:

```bash
git rev-list --max-parents=0 HEAD
```

### 3. Read git commit history

```bash
git log {base}..HEAD --oneline --no-merges
```

Also read merge commit messages, which often carry PR titles:

```bash
git log {base}..HEAD --oneline --merges
```

Collect each commit message. Note the author where available for attribution if the changelog convention includes it.

### 4. Read completed ticket files (if present)

Glob for `docs/tickets/*.md` and `docs/changes/*.md`. Read any with `status: done` and a `completed:` date within the release window.

These titles and acceptance criteria are higher-quality change descriptions than raw commit messages — prefer them when available.

### 5. Read merged PR titles (if gh is available)

```bash
gh pr list --state merged --limit 50 --json number,title,mergedAt,labels 2>/dev/null
```

If this succeeds, filter PRs merged since the base tag date. PR titles are typically better descriptions than commit messages.

## Classify changes

Map each change to one of the following categories. When in doubt, use the most user-visible category.

| Category | What belongs here |
|----------|------------------|
| **Added** | New features, new endpoints, new commands, new config options |
| **Changed** | Modifications to existing behaviour, updated dependencies with behaviour impact, UX changes |
| **Deprecated** | Features that still work but will be removed in a future release |
| **Removed** | Features, endpoints, config, or commands that no longer exist |
| **Fixed** | Bug fixes — include the symptom, not just "fixed a bug" |
| **Security** | Vulnerabilities patched, auth improvements, dependency CVE fixes |

**Conventional commit prefix mapping:**

| Prefix | Category |
|--------|----------|
| `feat:` / `feat!:` | Added (breaking → Changed) |
| `fix:` | Fixed |
| `perf:` | Changed |
| `refactor:` | Changed (only if user-visible) |
| `security:` / `sec:` | Security |
| `remove:` / `deprecated:` | Removed / Deprecated |
| `docs:` / `chore:` / `test:` / `ci:` | Omit — internal changes not relevant to consumers |
| `BREAKING CHANGE:` in footer | Changed, marked **Breaking** |

Omit purely internal changes (CI config, test-only changes, formatting) unless the changelog convention includes them.

## Output format

Respond inline by default. If `--save` is passed, prepend the new entry to the existing `CHANGELOG.md` (below any `[Unreleased]` header if one exists, above the previous release).

### Keep a Changelog format

```markdown
## [1.3.0] - 2026-05-10

### Added
- {Description of new capability — user-facing, not implementation detail}

### Changed
- {Description of modified behaviour}
- **Breaking:** {Description} — {what callers need to change}

### Fixed
- {Bug description — what was wrong and what the correct behaviour is now}

### Security
- {Vulnerability or exposure that was addressed}
```

### Conventional Commits format

```markdown
## 1.3.0 (2026-05-10)

### Features
- {feat description} ([#{PR}](link))

### Bug Fixes
- {fix description} ([#{PR}](link))

### BREAKING CHANGES
- {description of breaking change}
```

### After the entry

Print:

**Entry covers:** `{base tag or commit}..HEAD` ({N} commits, {date range})
**Classified:** {n} Added, {n} Changed, {n} Fixed, {n} Security, {n} omitted (internal)
**Omitted commits:** list of commit hashes/messages excluded as internal — so the user can review and recategorize if needed

## Gotchas

- Do not include internal-only changes (CI, test fixes, formatting) in the consumer-facing changelog unless the project convention does so explicitly. Internal changes inflate the changelog and dilute signal.
- "Fixed a bug" is not a changelog entry. Describe what the user experienced before the fix and what they experience now: "Fixed login failing with 500 when email address contains a `+` character."
- Breaking changes must be explicit and prominent. A breaking change buried in `### Changed` without a **Breaking:** prefix will surprise users on upgrade.
- If the git history has squash-merged PRs, the commit messages are PR titles — typically good quality. If it has many small feature-branch commits, the messages may be low quality and ticket files or PR titles are more reliable.
- Conventional commit prefixes are only reliable if the team actually enforces them. Check a sample before trusting the classification. If commits are freeform, classify by reading the message, not the prefix.
- The `[Unreleased]` section in Keep a Changelog is a convention for accumulating changes before a version is cut. If one exists, populate it rather than creating a new dated section — then rename it when the version is decided.
- If `gh` is not authenticated or available, note this and fall back to git log only. Do not fail silently.
- This skill pairs naturally with `/complete-ticket` (completed tickets are the primary source of changelog entries in a ticket-driven workflow), `/summarise-pr` (summarise individual PRs before classifying them into changelog sections), and `/create-ticket` (the full build workflow: create-ticket → complete-ticket → write-changelog).
