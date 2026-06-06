---
name: reverse-engineer
description: Perform a deep architectural reverse-engineering of an existing web application — explaining WHY decisions were made, identifying named architectural patterns, assessing engineering maturity, and inferring how the system evolved over time. Use when asked to understand architectural intent, not just what the code does.
compatibility: Requires Read, Glob, Grep for local paths. Requires internet access for GitHub URLs. Agent subagent used for large codebases.
allowed-tools: Read Glob Grep WebFetch Write Agent
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-06-06
---

Reverse-engineer the target application and produce an architectural analysis explaining **why** the system was built the way it was — the decisions, tradeoffs, named patterns, maturity signals, and evolutionary history that the code reveals. This is the "why" complement to `/research-codebase` (which answers "what") and `/onboard-codebase` (which answers "how do I work here").

## Determine the target

Accept any of:
- A local path: `.`, `services/api`, `packages/auth`
- A GitHub URL or `owner/repo` shorthand
- A service name — glob for a matching directory

Also accept:
- `--save` — write output to `{project-name}-architecture.md` (default when run without `--inline`)
- `--inline` — respond inline without writing a file

If a `{project-name}-docs.md` from `/research-codebase` exists in the current directory, read it first — use it as foundational context rather than re-discovering the tech stack from scratch.

## Discovery steps

Work through each step before writing the analysis. Every claim must be grounded in evidence from the code — do not speculate without flagging it explicitly.

### 1. Gather foundational context

If a `/research-codebase` output file exists, read it and skip to step 2.

Otherwise, gather the minimum needed:
- Read `README.md`, root manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.), and `docker-compose.yml` or `compose.yaml`
- List top-level directories 2 levels deep
- Read `.github/workflows/` to understand the CI/CD pipeline
- Read infrastructure definitions: `terraform/`, `k8s/`, `infra/`, `Dockerfile`

Extract: what the system does, primary language and runtime, key frameworks, infrastructure footprint.

### 2. Identify the architectural style

From the project structure and entry points, determine which style best fits:

| Style | Evidence to look for |
|---|---|
| Monolith | Single deployable, shared DB, one service folder |
| Modular monolith | Single deployable with enforced module boundaries (barrel files, explicit internal/public split) |
| Microservices | Multiple independently deployable services, separate manifests, inter-service communication |
| SPA + API | Separate frontend app, REST or GraphQL API, no SSR |
| SSR / hybrid | Framework with server rendering (Next.js, Nuxt, SvelteKit, Remix, Rails, Django) |
| Event-driven | Message broker present (Kafka, RabbitMQ, SQS, Pub/Sub), async consumers |
| Microfrontend | Multiple frontend apps composed at runtime (Module Federation, single-spa, Bit) |

Explain which style applies, why the team likely chose it, its tradeoffs at this scale, and what a modern team might choose today.

### 3. Map named architectural patterns

Read source files in `src/`, `lib/`, `internal/`, `app/`, or equivalent. Look for structural evidence of:

- **Layered architecture** — controller → service → repository stacking
- **Clean / Hexagonal architecture** — inward-facing domain core, ports and adapters at the boundary
- **DDD** — aggregates, value objects, domain events, bounded contexts, ubiquitous language in naming
- **Feature-based / vertical slices** — each feature owns its own controller, service, and data access
- **CQRS** — separate read and write models or handlers
- **Event sourcing** — append-only event store, event replay

For each pattern found: name it, cite the file paths that demonstrate it, explain why the team likely applied it, explain where it breaks down or is applied inconsistently.

### 4. Frontend architecture deep dive

Skip if the target is a backend-only service.

Determine and explain:
- **Rendering strategy** — CSR, SSR, SSG, ISR, or hybrid. Which pages use which strategy and why.
- **Routing** — file-based, config-based, or code-based. Nested layouts.
- **State management** — server state (React Query, SWR, Apollo), client state (Redux, Zustand, Jotai, Pinia, signals). Where the boundary is drawn.
- **Data fetching pattern** — where fetches live (component, hook, store, server component), how loading and error states are handled.
- **Authentication flow** — where tokens are stored, how refresh works, how protected routes are guarded.
- **Component organization** — atomic design, feature folders, co-location, or ad hoc.
- **Design system** — custom, third-party (shadcn/ui, MUI, Tailwind), or missing.
- **Code splitting / lazy loading** — route-based, component-based, or absent.

Trace one real feature end-to-end: pick a representative page, follow it from component render through state, API call, and back.

### 5. Backend architecture deep dive

Skip if the target is a frontend-only app.

Determine and explain:
- **API design style** — REST, GraphQL, tRPC, gRPC, or mixed. Versioning strategy.
- **Service boundaries** — how responsibilities are divided. Whether boundaries map to domain concepts or are accidental.
- **Persistence strategy** — ORM or raw queries, repository pattern or direct DB access, migration tooling.
- **Caching strategy** — where caching lives (in-process, Redis, CDN, HTTP headers), what is cached, TTL approach.
- **Async / event patterns** — background jobs, queues, pub/sub, webhooks. What triggers async work.
- **Auth and security** — where auth is enforced (middleware, decorator, gateway), token validation, RBAC/ABAC.
- **Configuration management** — environment variables, secrets management, feature flags.
- **Resilience patterns** — retries, circuit breakers, timeouts, graceful degradation. What is missing.

Trace one request from ingress to persistence: pick a representative write endpoint, follow it through middleware, handler, service, and DB.

### 6. Build and deployment analysis

Determine and explain:
- **Local development** — how the service starts, what `docker-compose` runs, what `.env` setup is required.
- **Build pipeline** — what steps CI runs on PR, what runs on merge to main.
- **Environment configuration** — how dev/staging/prod differ, whether configuration is code or external.
- **Containerization** — Dockerfile structure, base image choices, multi-stage build or not.
- **Infrastructure model** — managed platform (Vercel, Railway, Fly.io), container orchestration (ECS, Kubernetes), or VM-based.
- **Release strategy** — versioning approach, deployment frequency signals from git history, feature flags.

### 7. Engineering maturity assessment

Score each dimension as **Green / Amber / Red**:

| Dimension | Signal to look for |
|---|---|
| Code quality | Consistent style, linting config, type coverage |
| Architectural consistency | Patterns applied uniformly vs. patchwork |
| Test strategy | Coverage of unit / integration / e2e, test-to-code ratio |
| Observability | Structured logging, metrics, tracing, alerting config |
| Security posture | Auth enforcement, secrets handling, dependency scanning |
| Developer experience | Local setup friction, CI speed signals, documentation |
| Scalability | Stateless services, horizontal scaling affordances, DB bottlenecks |
| Operational maturity | Runbooks, health checks, graceful shutdown, rollback plan |

After the table, list:
- **Strengths** — 3–5 bullets of what is done well
- **Risks** — 3–5 bullets of the highest-priority concerns
- **Technical debt** — patterns or decisions that will constrain future work

### 8. Historical evolution inference

From git history (most recent 50 commits via `git log --oneline -50` if accessible), file naming, dead code, and migration files, infer:

- What the system likely looked like 1–2 years ago
- What migrations have occurred (framework upgrades, DB migrations, auth rewrites)
- Where scaling pressure has left marks (caching bolted on, DB sharding hints, read replicas)
- What patterns were introduced late vs. present from the start
- Where modernization is in progress vs. stalled

Flag every inference explicitly with **(inferred)** — do not present speculation as fact.

## Output format

Write to `{project-name}-architecture.md` by default. If `--inline` is passed, respond inline.

---

**Architectural Analysis: {Project Name}**

> Generated: {YYYY-MM-DD} · Based on: {commit SHA or "local snapshot"} · Run `/reverse-engineer` again after major structural changes.

---

### Executive Summary

2–3 paragraphs: what this system is, how it is structured at the highest level, and the single most important thing to understand about its architecture. Write for a senior engineer unfamiliar with the project.

---

### Architectural Style

**Style:** {name}

**Evidence:**
- {file or pattern that demonstrates this}

**Why this was likely chosen:** {reasoning}

**Tradeoffs at this scale:** {what works, what strains}

**What a modern team might choose today:** {alternative + when it makes sense}

**Request lifecycle overview:**

```mermaid
sequenceDiagram
  autonumber
  {trace a single representative request end-to-end}
```

---

### Named Patterns

For each pattern found:

**{Pattern name}** · *{Consistently applied / Partially applied / Aspirational}*

Evidence: `{path/to/file.ts}`, `{path/to/other.ts}`

Why applied: {reasoning}

Where it breaks down: {specific inconsistency or violation, with file path}

---

### Frontend Architecture

**Rendering strategy:** {strategy} — {why this choice}

**State boundary:** {what lives where and why}

**Auth flow:** {how it works, where tokens live}

**Feature trace — {Feature name}:**

```
{Component} → {hook/store} → {API call} → {endpoint} → {response handling}
```

**Design decisions worth noting:**
- {decision + rationale + tradeoff}

---

### Backend Architecture

**API style:** {REST / GraphQL / tRPC / gRPC} — {versioning approach}

**Service boundary logic:** {how responsibilities are divided and whether it maps to domain concepts}

**Request trace — {Endpoint}:**

```
Ingress → [Middleware] → Handler → Service → Repository → DB
```

**Design decisions worth noting:**
- {decision + rationale + tradeoff}

---

### Infrastructure & Deployment

**Deployment model:** {platform/approach}

**CI/CD:** {what happens on PR, what happens on merge}

**Configuration:** {how environments differ, how secrets are managed}

**Developer workflow:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

---

### Engineering Maturity

| Dimension | Rating | Notes |
|---|---|---|
| Code quality | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Architectural consistency | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Test strategy | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Observability | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Security posture | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Developer experience | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Scalability | 🟢 / 🟡 / 🔴 | {one-line evidence} |
| Operational maturity | 🟢 / 🟡 / 🔴 | {one-line evidence} |

**Strengths**
- {strength with evidence}

**Risks**
- {risk with evidence and consequence}

**Technical debt**
- {debt with file path or pattern reference}

---

### Historical Evolution

- {Inference with **(inferred)** tag}
- {What changed and what evidence supports it}

---

### Key Lessons

For each major architectural decision:

**{Decision}**

*Simple explanation:* {one paragraph, no jargon}

*Senior engineer depth:* {tradeoffs, failure modes, scale concerns}

*What I would do differently today:* {specific alternative with reasoning}

---

After writing the file, print:

**Architecture analysis written:** `{path}`
**Style identified:** {style}
**Patterns found:** {list}
**Maturity summary:** {X green / Y amber / Z red}
**Top risk:** {one sentence}

## Examples

```
/reverse-engineer
```
Analyses the current working directory.

```
/reverse-engineer services/payments
```
Analyses the payments service only.

```
/reverse-engineer https://github.com/owner/repo
```
Fetches and analyses a GitHub repository.

```
/reverse-engineer --inline
```
Responds inline rather than writing a file.

## Gotchas

- **Label inferences.** Historical evolution and "why decisions were made" involve inference. Tag every inferred claim with **(inferred)** — presenting speculation as fact erodes trust in the whole analysis.
- **Evidence over intuition.** Every named pattern claim must cite a specific file path. "This looks like clean architecture" is not enough without `src/domain/`, `src/application/`, `src/infrastructure/` as evidence.
- **Don't duplicate `/research-codebase`.** If a `{project-name}-docs.md` exists, use it. Do not re-document the tech stack from scratch — the value here is the why-layer on top.
- **Skip inapplicable sections.** A backend-only service has no frontend architecture. A frontend-only app has no backend deep dive. Omit rather than fill with "N/A".
- **Maturity ratings need evidence.** A Red rating without a file path or pattern reference is not actionable. A Green rating without evidence looks made up. Always cite.
- **Large codebases need scoping.** If the repo has more than ~100 source files, use an Agent subagent (`subagent_type: Explore`) for the discovery traversal rather than exhaustive Grep in a single pass.
- **Git history may be inaccessible.** For GitHub targets, git log is unavailable — infer evolution from migration files, changelog, or naming patterns instead. Flag the limitation.
- This skill pairs naturally with `/research-codebase` (foundational docs that this skill builds on), `/map-api-flow` (trace specific flows identified during the backend deep dive), `/platform-readiness` (turn the maturity assessment into an actionable remediation checklist), and `/refactor-strategy` (turn identified technical debt into a phased modernization roadmap).
