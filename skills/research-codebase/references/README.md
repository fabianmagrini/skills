# references

Supporting resources used by the `research-codebase` skill.

| File | Purpose |
|------|---------|
| [OUTPUT-TEMPLATE.md](OUTPUT-TEMPLATE.md) | Markdown structure for the generated `{repo-name}-docs.md` output file |
| [EXAMPLE-OUTPUT.md](EXAMPLE-OUTPUT.md) | A realistic sample of a completed `*-docs.md` file for reference |

## How references are used

The skill prompt in `../SKILL.md` references these files by relative path. When Claude executes the skill, it reads the relevant template to guide its output format.

To add a new reference (e.g. a language-specific template), drop the file here and link to it from `SKILL.md`.
