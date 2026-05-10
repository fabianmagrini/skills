# skills

A collection of custom skills for coding agents that support the [Agent Skills](https://agentskills.io/home) standard, including [Claude Code](https://claude.ai/code).

Skills extend your coding agent with reusable, invocable prompts. Each skill lives in its own directory and is activated via a slash command. For information about the Agent Skills standard, see [agentskills.io](https://agentskills.io/home). For more examples of skills see <https://github.com/anthropics/skills>.

## Skills

### Build

| Skill | Description |
|-------|-------------|
| [complete-ticket](skills/complete-ticket/SKILL.md) | Implement a single change ticket — read the problem, write a failing test, make it pass, commit, and mark done |
| [create-ticket](skills/create-ticket/SKILL.md) | Create a well-formed change ticket from a description, bug report, or feature request — extracting problem statement, acceptance criteria, and technical context |
| [spec-to-backlog](skills/spec-to-backlog/SKILL.md) | Convert a product spec or feature description into a sequenced backlog of epics, user stories, technical stories, and spikes |

### Understand

| Skill | Description |
|-------|-------------|
| [explain-codebase](skills/explain-codebase/SKILL.md) | Quick inline explanation of a repo, directory, file, or function |
| [map-api-flow](skills/map-api-flow/SKILL.md) | Map the full API call chain from frontend to backend, with a Mermaid diagram and critical path summary |
| [research-codebase](skills/research-codebase/SKILL.md) | Comprehensive documentation for a codebase, written to a file |

### Review & Test

| Skill | Description |
|-------|-------------|
| [review-code](skills/review-code/SKILL.md) | Structured code review covering correctness, security, edge cases, and tests |
| [summarise-pr](skills/summarise-pr/SKILL.md) | Summarise a GitHub PR — purpose, key changes, and review considerations |
| [test-strategy](skills/test-strategy/SKILL.md) | Audit the current test pyramid, identify gaps and imbalances, and produce a recommended strategy with tooling, coverage targets, and an improvement plan |
| [write-tests](skills/write-tests/SKILL.md) | Generate tests that match the project's existing framework and conventions |

### Design

| Skill | Description |
|-------|-------------|
| [design-api](skills/design-api/SKILL.md) | Design a REST (OpenAPI 3.x) or GraphQL API — resources, operations, schemas, error states, pagination, auth, and versioning |
| [design-system](skills/design-system/SKILL.md) | Convert a requirement or business goal into a reference architecture with C4 diagrams, component boundaries, trade-offs, NFRs, and risks |
| [document-api](skills/document-api/SKILL.md) | Reverse-engineer an existing API from source code into a complete OpenAPI 3.x specification — routes, schemas, auth, and a coverage report |
| [draft-rfc](skills/draft-rfc/SKILL.md) | Scaffold a technical RFC covering goals, non-goals, proposed solution, architecture, security, rollout, and alternatives |
| [write-adr](skills/write-adr/SKILL.md) | Generate an Architecture Decision Record capturing context, decision, alternatives, and consequences |

### Improve

| Skill | Description |
|-------|-------------|
| [debug-issue](skills/debug-issue/SKILL.md) | Diagnose a bug, error, or unexpected behaviour — from symptom or stack trace to ranked suspects, root cause, and specific fix recommendation |
| [perf-investigate](skills/perf-investigate/SKILL.md) | Diagnose performance bottlenecks — latency, CPU, memory, or throughput — with a latency tree, suspect list, cache opportunities, and profiling plan |
| [refactor-strategy](skills/refactor-strategy/SKILL.md) | Produce a large-scale refactoring roadmap with incremental phases, blast radius analysis, rollback plan, and risk register |

### Secure

| Skill | Description |
|-------|-------------|
| [dependency-risk](skills/dependency-risk/SKILL.md) | Analyze package, vendor, or architecture dependency risk — supply chain exposure, license compatibility, vendor lock-in, and coupling depth |
| [security-audit](skills/security-audit/SKILL.md) | Audit source code for OWASP Top 10 vulnerabilities — injection, broken auth, sensitive data exposure, and misconfiguration — with severity-ranked findings and specific remediations |
| [threat-model](skills/threat-model/SKILL.md) | Apply STRIDE threat modelling to identify threat vectors, trust boundaries, abuse cases, and mitigations |

### Operate

| Skill | Description |
|-------|-------------|
| [generate-runbook](skills/generate-runbook/SKILL.md) | Generate or update an operational runbook — deployment, rollback, health checks, on-call escalation, failure modes with diagnosis steps, and alert procedures |
| [incident-review](skills/incident-review/SKILL.md) | Produce a blameless postmortem with structured timeline, 5 Whys root cause analysis, contributing factors, and actionable CAPAs |
| [migrate-data](skills/migrate-data/SKILL.md) | Plan and scaffold a database migration — schema change or data transformation — with rollback strategy, zero-downtime sequencing, and validation queries |
| [platform-readiness](skills/platform-readiness/SKILL.md) | Evaluate production readiness across observability, security, CI/CD, scalability, and SLOs with a RAG-scored checklist and prioritised remediation |

### Agentic

| Skill | Description |
|-------|-------------|
| [agent-loop-design](skills/agent-loop-design/SKILL.md) | Design an autonomous agent loop — loop pattern, phases, guardrails, HITL checkpoints, tool contracts, and observability — for a given workflow or governance objective |
| [context-engineering](skills/context-engineering/SKILL.md) | Generate or audit an agent context file (CLAUDE.md or equivalent) by extracting project conventions, commands, architecture, and anti-patterns from the codebase |
| [skill-generator](skills/skill-generator/SKILL.md) | Generate a new skill from a repeated workflow description — elicits trigger, discovery, output format, and gotchas before writing a schema-compliant first draft |

## Installation

Copy or symlink individual skill directories from `skills/` into your agent's skills folder. See [agentskills.io](https://agentskills.io/home) for the installation path and setup instructions for your agent and platform.

## Usage

Invoke any skill with its slash command (exact syntax may vary by agent):

```
# Design an autonomous agent loop
/agent-loop-design PR governance
/agent-loop-design code remediation

# Generate or audit an agent context file
/context-engineering
/context-engineering audit
/context-engineering audit path/to/CLAUDE.md

# Generate a new skill from a workflow description
/skill-generator
/skill-generator summarise Slack threads into action items

# Create a ticket from a description or bug report
/create-ticket add a CSV export endpoint to the orders API
/create-ticket login fails with 500 when email contains a plus sign
/create-ticket docs/notes/export-idea.md

# Implement a single ticket
/complete-ticket docs/tickets/add-export-endpoint.md
/complete-ticket export endpoint

# Convert a spec to a backlog
/spec-to-backlog passkey auth
/spec-to-backlog docs/specs/semantic-layer.md

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

# Audit and design a test strategy
/test-strategy
/test-strategy src/services/payments/

# Summarise a pull request
/summarise-pr owner/repo#123

# Generate tests
/write-tests src/utils/format.ts

# Design an API (REST or GraphQL)
/design-api subscription and billing management
/design-api passkey authentication --graphql
/design-api src/orders/ --rest

# Document an existing API from source code
/document-api services/payments/
/document-api src/routes/orders.ts
/document-api orders API --update docs/api/orders.openapi.yaml

# Design a system architecture
/design-system auth platform
/design-system multi-tenant SaaS

# Draft a technical RFC
/draft-rfc global rate limiting
/draft-rfc passkey authentication
/draft-rfc docs/notes/semantic-search.md

# Write an Architecture Decision Record
/write-adr use GraphQL federation
/write-adr Redis for authorization cache

# Diagnose a bug or error
/debug-issue "TypeError: Cannot read properties of undefined"
/debug-issue checkout fails after adding a coupon
/debug-issue src/auth/session.ts

# Investigate a performance problem
/perf-investigate checkout latency
/perf-investigate src/search/

# Plan a large-scale refactor
/refactor-strategy monolith to microservices
/refactor-strategy src/legacy/

# Analyze dependency and vendor risk
/dependency-risk package.json
/dependency-risk auth0
/dependency-risk services/payments/

# Audit source code for security vulnerabilities
/security-audit src/api/
/security-audit authentication
/security-audit src/auth/session.ts

# Threat model a system or component
/threat-model payments API
/threat-model src/auth/

# Produce a postmortem and RCA
/incident-review outage-timeline.md
/incident-review incidents/2026-05-09/

# Plan a database migration
/migrate-data "add nullable phone_number column to users"
/migrate-data "rename orders.state to orders.status" --zero-downtime
/migrate-data db/migrations/20260510_add_phone.sql

# Generate or update an operational runbook
/generate-runbook payments-service
/generate-runbook services/checkout/
/generate-runbook --update docs/runbooks/payments.md

# Evaluate production readiness
/platform-readiness BFF
/platform-readiness services/checkout/
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
