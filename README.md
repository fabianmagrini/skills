# skills

A collection of custom skills for coding agents that support the [Agent Skills](https://agentskills.io/home) standard, including [Claude Code](https://claude.ai/code).

Skills extend your coding agent with reusable, invocable prompts. Each skill lives in its own directory and is activated via a slash command. For information about the Agent Skills standard, see [agentskills.io](https://agentskills.io/home). For more examples of skills see <https://github.com/anthropics/skills>.

## Skills

| Skill | Description |
|-------|-------------|
| [design-system](skills/design-system/SKILL.md) | Convert a requirement or business goal into a reference architecture with C4 diagrams, component boundaries, trade-offs, NFRs, and risks |
| [explain-codebase](skills/explain-codebase/SKILL.md) | Quick inline explanation of a repo, directory, file, or function |
| [map-api-flow](skills/map-api-flow/SKILL.md) | Map the full API call chain from frontend to backend, with a Mermaid diagram and critical path summary |
| [perf-investigate](skills/perf-investigate/SKILL.md) | Diagnose performance bottlenecks — latency, CPU, memory, or throughput — with a latency tree, suspect list, cache opportunities, and profiling plan |
| [refactor-strategy](skills/refactor-strategy/SKILL.md) | Produce a large-scale refactoring roadmap with incremental phases, blast radius analysis, rollback plan, and risk register |
| [research-codebase](skills/research-codebase/SKILL.md) | Comprehensive documentation for a codebase, written to a file |
| [review-code](skills/review-code/SKILL.md) | Structured code review covering correctness, security, edge cases, and tests |
| [summarise-pr](skills/summarise-pr/SKILL.md) | Summarise a GitHub PR — purpose, key changes, and review considerations |
| [threat-model](skills/threat-model/SKILL.md) | Apply STRIDE threat modelling to identify threat vectors, trust boundaries, abuse cases, and mitigations |
| [write-adr](skills/write-adr/SKILL.md) | Generate an Architecture Decision Record capturing context, decision, alternatives, and consequences |
| [write-tests](skills/write-tests/SKILL.md) | Generate tests that match the project's existing framework and conventions |

## Installation

Copy or symlink individual skill directories from `skills/` into your agent's skills folder. See [agentskills.io](https://agentskills.io/home) for the installation path and setup instructions for your agent and platform.

## Usage

Invoke any skill with its slash command (exact syntax may vary by agent):

```
# Explain a codebase, file, or function inline
/explain-codebase https://github.com/owner/repo
/explain-codebase src/auth/middleware.ts

# Map an API flow
/map-api-flow
/map-api-flow user authentication
/map-api-flow src/features/checkout

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

## Community Skills

Skills from people worth following:

| Author | Repository | Highlights |
|--------|------------|------------|
| [Addy Osmani](https://github.com/addyosmani) | <https://github.com/addyosmani/agent-skills> | Production-grade skills covering code review, security, TDD, debugging, performance, CI/CD, spec-driven development, and more |
| [Matt Pocock](https://github.com/mattpocock) | <https://github.com/mattpocock/skills> | Practical engineering skills including TDD, architecture review, issue triage, prototyping, and diagnosis |

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
