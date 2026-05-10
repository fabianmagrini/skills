---
name: design-system
description: Convert a requirement or business goal into a reference architecture with C4 diagrams, component boundaries, trade-offs, NFRs, and risks.
compatibility: Accepts natural language descriptions. Optionally reads local code or infrastructure files to ground the design in an existing system.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Produce a reference architecture for the given system or feature.

## Determine the target

Accept any of:
- A system or platform description: `auth platform`, `multi-tenant SaaS`, `real-time notifications`
- A feature within an existing codebase: `checkout flow`, `data ingestion pipeline`
- A migration goal: `monolith to microservices`, `on-prem to cloud`

If a local path is given, read the existing codebase to understand the current architecture before designing. Use this as the baseline — the output should extend or replace it, not ignore it.

If only a description is given, state your assumptions about scale, team size, and technology constraints before proceeding. Ask the user to confirm or correct them if the assumptions are significant.

## Discovery steps (for local targets)

1. **Entry points and APIs** — Glob for route/controller files, OpenAPI specs (`**/openapi.yaml`, `**/swagger.json`), and GraphQL schemas. Identify the public surface.

2. **Existing services and boundaries** — Look for service directories, Docker Compose files, Kubernetes manifests, Terraform/CDK definitions. Map what already exists.

3. **Data stores** — Grep for database clients, ORM configuration, and migration files. Note each distinct store and what it owns.

4. **External dependencies** — Identify third-party APIs, queues, CDNs, and identity providers from config files and environment variable references.

5. **Non-functional signals** — Look for rate limiting, caching, observability setup (metrics, tracing, logging), and CI/CD pipeline definitions. These reveal existing NFR coverage.

## Design process

Work through the following in order before producing output:

### 1. Clarify the problem
State in 2–3 sentences: what the system must do, who the principal actors are, and what the most important quality attribute is (consistency, availability, latency, cost, security). If there is tension between quality attributes, name it.

### 2. Identify components
Define the major components. For each:
- **Name**: short, noun-phrase label
- **Responsibility**: one sentence — what it owns, what it does not own
- **Technology**: the runtime, framework, or managed service (be specific, not generic)
- **Interfaces**: what it exposes and what it consumes

Aim for 5–10 components. More than 10 usually means the scope is too broad; fewer than 4 usually means important boundaries are missing.

### 3. Define data flows
For each significant user journey or system event, trace the path through components. Identify:
- Synchronous vs. asynchronous interactions
- Where data is written vs. read
- Where the source of truth lives for each entity

### 4. Identify NFRs
For each quality attribute below, state the target and how the design addresses it:

| Attribute | Target | How addressed |
|-----------|--------|---------------|
| Availability | e.g. 99.9% | ... |
| Latency | e.g. p99 < 200ms | ... |
| Scalability | e.g. 10× current load | ... |
| Security | e.g. zero-trust internal | ... |
| Observability | e.g. distributed tracing | ... |
| Cost | e.g. serverless to reduce idle | ... |

Only include rows relevant to the target system.

### 5. Evaluate trade-offs
For each significant design decision, name the alternative and the reason for the choice. Use a table. Aim for 3–5 decisions.

### 6. Identify risks
List 3–5 risks with likelihood, impact, and mitigation. Focus on risks specific to this design, not generic software risks.

## Output format

By default respond inline. If the user passes `--save`, write the output to `docs/architecture/{kebab-case-title}.md`.

### System Design: `{target}`

**Problem Statement**

2–3 sentences: what the system must do, who the actors are, the primary quality attribute, and any key constraints.

**Assumptions**

Bullet list of assumptions made about scale, team, technology, or constraints. If the user provided these, confirm them here.

**C4 Diagrams**

Produce diagrams at two levels using Mermaid `graph TD`:

*Level 1 — System Context*: show the system as a single box, with external actors (users, external systems) around it. Label each relationship with the interaction type.

*Level 2 — Container*: expand the system into its major runtime components (services, databases, queues, frontends). Show interactions between containers with protocol/mechanism labels.

Use `subgraph` blocks to group containers by zone (e.g. `Browser`, `Backend`, `Data`, `External`).

```mermaid
graph TD
  subgraph ...
  end
```

**Component Inventory**

| Component | Responsibility | Technology | Exposes | Consumes |
|-----------|---------------|------------|---------|----------|

**Key Data Flows**

For each principal user journey or system event, one bullet:
- **{Flow name}**: `Actor` → `Component A` → `Component B` → `Store` — note sync/async and source of truth

**Non-Functional Requirements**

| Attribute | Target | How addressed |
|-----------|--------|---------------|

**Trade-offs**

| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|

**Risks**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

**Open Questions**

Bullet list of decisions deferred or questions the team must answer before implementation. Each item should be actionable: name who should decide and what information is needed.

## Gotchas

- Do not design for hypothetical scale. Anchor NFR targets to what the user stated or to reasonable inference from the context. A CRUD app for 500 users does not need Kafka.
- Component responsibilities must be exclusive — if two components share ownership of the same data, name the conflict and resolve it.
- C4 Level 2 should show containers, not classes or functions. If you find yourself naming individual files, you are too deep.
- Trade-offs must be honest. If a choice has a real cost (operational complexity, vendor lock-in, learning curve), name it.
- If the target is a migration, produce a phased approach in Open Questions rather than designing the end state only.
- For greenfield systems with no local codebase, be explicit that the output is a starting point and link to relevant ADR skills for capturing individual decisions.
- This skill pairs naturally with `/draft-rfc` (capturing the system design as an RFC for team review) and `/write-adr` (recording the individual architectural decisions made during design).
