# Skill Schema

Defines the required and optional frontmatter fields for every `SKILL.md` file in this repo.

## Frontmatter reference

```yaml
---
name: skill-name                  # required
description: One sentence.        # required
compatibility: Notes on limits.   # optional
allowed-tools: Read Glob Grep     # required
metadata:
  author: github-username         # optional
  version: "1.0"                  # optional, semver string
  last-updated: YYYY-MM-DD        # optional, ISO date
---
```

### Field definitions

#### `name` (required)
`kebab-case` identifier. Must match the directory name. Becomes the slash command (`/skill-name`).

#### `description` (required)
One sentence explaining what the skill does and when Claude should invoke it. This is used by Claude to decide relevance — be specific and action-oriented.

Good: `Research and produce comprehensive documentation for a codebase from a GitHub URL or local path.`
Bad: `Helps with codebases.`

#### `compatibility` (optional)
Document any prerequisites or limitations that affect whether the skill can run. Examples:
- `Requires internet access for GitHub URLs.`
- `Requires Read, Glob, Grep tools for local paths.`
- `Only works with Node.js projects.`

#### `allowed-tools` (required)
Space-separated list of tools the skill is permitted to use. Be as restrictive as possible — only include tools the skill actually needs.

Available tools: `Read`, `Glob`, `Grep`, `Write`, `Edit`, `Bash`, `WebFetch`, `WebSearch`, `Agent`

#### `metadata.author` (optional)
GitHub username of the skill's author.

#### `metadata.version` (optional)
Two-part version string (`"MAJOR.MINOR"`), e.g. `"1.0"`, `"1.2"`, `"2.0"`. Not full semver — patch releases are not tracked separately.

#### `metadata.last-updated` (optional)
ISO 8601 date (`YYYY-MM-DD`) of the last meaningful update to the skill.

## Versioning policy

- Start at `"1.0"`.
- Bump `MINOR` (e.g. `"1.0"` → `"1.1"`) for backwards-compatible changes: new behaviour, improved output, bug fixes.
- Bump `MAJOR` (e.g. `"1.1"` → `"2.0"`) when the skill's invocation interface or output structure changes in a way that could break existing workflows.
