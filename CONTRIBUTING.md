# Contributing

## Adding a new skill

### 1. Create the skill directory

```
skills/
  your-skill-name/
    SKILL.md
    references/       # optional — templates and supporting files
```

### 2. Write `SKILL.md`

Every skill requires a frontmatter header followed by the prompt body.

```markdown
---
name: your-skill-name
description: One sentence describing what this skill does and when to use it.
compatibility: Any runtime requirements (e.g. internet access, specific tools).
allowed-tools: Read Glob Grep Write WebFetch
metadata:
  author: your-github-username
  version: "1.0"
  last-updated: YYYY-MM-DD
---

Skill instructions go here...
```

See [SKILL-SCHEMA.md](SKILL-SCHEMA.md) for full field definitions, required vs optional fields, and versioning policy.

### 3. Add a `references/` directory (optional)

Use `references/` for templates, example outputs, or other files the skill prompt references. Add a `README.md` explaining the purpose of each file.

### 4. Add examples to `SKILL.md`

Include a `## Examples` section showing realistic invocations and what output to expect.

### 5. Register the skill in the root `README.md` and `skills.json`

- Add a row to the Skills table in [README.md](README.md).
- Add an entry to [skills.json](skills.json) following the existing structure.

## Conventions

- Skill names use `kebab-case`.
- Keep `SKILL.md` focused — one skill per file, one purpose per skill.
- Prefer explicit `allowed-tools` lists over broad permissions.
- Test your skill against at least one real input before submitting.
