# skills

A collection of custom skills for [Claude Code](https://claude.ai/code). 

Skills extend Claude Code with reusable, invocable prompts. Each skill lives in its own directory and is activated via the `/skill-name` slash command. For information about the Agent Skills standard, see [agentskills.io](https://agentskills.io/home). For more examples of skills see <https://github.com/anthropics/skills>.

## Skills

| Skill | Description |
|-------|-------------|
| [explain-codebase](skills/explain-codebase/SKILL.md) | Quick inline explanation of a repo, directory, file, or function |
| [research-codebase](skills/research-codebase/SKILL.md) | Comprehensive documentation for a codebase, written to a file |
| [review-code](skills/review-code/SKILL.md) | Structured code review covering correctness, security, edge cases, and tests |
| [summarise-pr](skills/summarise-pr/SKILL.md) | Summarise a GitHub PR — purpose, key changes, and review considerations |
| [write-tests](skills/write-tests/SKILL.md) | Generate tests that match the project's existing framework and conventions |

## Installation

Copy or symlink individual skill directories from `skills/` into your Claude Code skills folder. See [agentskills.io](https://agentskills.io/home) for the installation path and setup instructions for your platform.

## Usage

Invoke any skill in Claude Code with its slash command:

```
# Explain a codebase, file, or function inline
/explain-codebase https://github.com/owner/repo
/explain-codebase src/auth/middleware.ts

# Produce a full documentation file
/research-codebase https://github.com/owner/repo
/research-codebase /path/to/local/project

# Review code
/review-code src/payments/processor.ts

# Summarise a pull request
/summarise-pr owner/repo#123

# Generate tests
/write-tests src/utils/format.ts
```

## Structure

Each skill follows this layout:

```
skills/
  skill-name/
    SKILL.md          # Skill definition and instructions
    references/       # Templates and supporting resources (optional)
```

A machine-readable index of all skills is in [skills.json](skills.json).

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SKILL-SCHEMA.md](SKILL-SCHEMA.md) for how to add a new skill.
