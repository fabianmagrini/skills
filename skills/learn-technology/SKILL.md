---
name: learn-technology
description: Teach a technology from first principles — what it is, why it exists, how it works internally, the full pattern surface, operational concerns, and a structured learning path. Uses the codebase as worked examples when present, but works from a technology name alone. Use when you want to learn a technology, not just understand how a specific project uses it.
compatibility: WebFetch used to retrieve official documentation for the pinned version. Codebase is optional — providing a path enriches the examples but is not required.
allowed-tools: Read Glob Grep WebFetch Write Agent
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-06-06
---

Teach the target technology from first principles — concepts, mental models, internals, patterns, operational concerns, common mistakes, and a structured learning path. When a codebase is provided, use it as the source of worked examples, grounding abstract concepts in real code. This is the technology-first complement to `/tech-deep-dive` (which is codebase-first).

## Determine the target

Required:
- `{technology}` — the technology to teach (e.g. `Redis`, `Kafka`, `Prisma`, `React Query`, `Tailwind`, `Kubernetes`, `Temporal`)

Optional:
- `{path}` — a local codebase path to mine for worked examples (`services/api`, `.`)
- `--beginner` — assume no prior knowledge; expand foundational explanations and skip nothing
- `--advanced` — assume working familiarity; skip basics, focus on internals, edge cases, and operational depth
- `--save` — write output to `{technology}-learning-guide.md`

If no path is given, teach from the technology itself — no codebase examples. If a path is given, weave real code into every section as illustration.

## Discovery steps

### 1. Confirm the version (if a codebase is present)

Read the root manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements.txt`) and find the pinned version. A major version boundary often means a different API, different mental model, or a different recommended pattern set. Note it prominently and use it to anchor all examples.

If no codebase is present, state which version the teaching targets (latest stable) and flag it.

### 2. Fetch the official documentation

Attempt to retrieve current documentation for the pinned version:

- For npm packages: fetch `https://registry.npmjs.org/{package-name}/latest` to get the `homepage` field, then fetch that URL
- For Python packages: fetch `https://pypi.org/pypi/{package}/json` for the `project_urls.Homepage` field
- For well-known technologies with stable doc URLs (Redis, Kafka, PostgreSQL, Kubernetes), fetch the official docs directly

Read the landing page and the "getting started" or "concepts" section. This grounds the teaching in the technology's own framing — particularly useful for the version-specific API surface and any recent breaking changes.

If docs are behind a login or unavailable, proceed from model knowledge and flag the limitation.

### 3. Identify worked examples in the codebase (if a path is provided)

Search for the technology's primary import or client:

```
grep -r "{import pattern}" {path} --include="*.ts" --include="*.js" --include="*.py" -l
```

Read 3–5 representative usage files. For each concept covered in the teaching, find the closest real example from this codebase. The goal is: every abstract concept should have at least one concrete code snippet from the actual project.

For large codebases (>50 usage sites), use an Agent subagent (`subagent_type: Explore`) to sample representative files without exhaustive traversal.

### 4. Identify which parts of the technology the codebase uses and which it doesn't

From the usage map, note:
- Which features and patterns this codebase uses (the teaching should cover these in depth)
- Which major features this codebase does NOT use (the teaching should still cover these — knowing what exists matters even if unused)

## Output format

Respond inline by default. Write to `{technology}-learning-guide.md` if `--save` is passed.

---

**Learning Guide: {Technology} {version}**

> Generated: {YYYY-MM-DD} · {"Examples drawn from: {path}" or "No codebase provided — examples are illustrative."}

---

### What It Is and Why It Exists

**The problem it solves:**
{1–2 paragraphs on the real-world engineering problem this technology addresses. Start with the pain — what was hard or impossible before this technology existed? What did engineers do instead, and why was that unsatisfying?}

**The core insight:**
{One sentence. The single idea that makes this technology work. E.g. for Redis: "Store data structures in memory so reads are order-of-magnitude faster than disk." For Kafka: "Treat the log as the source of truth, not the database."}

**What it is NOT:**
{1–3 bullets on common misconceptions or things people reach for this technology to solve when something else is better.}

---

### The Mental Model

{Before any API or syntax, give the reader the conceptual model they need to hold. Use an analogy if one genuinely helps — but only if it holds up under scrutiny. Diagrams strongly preferred.}

```mermaid
{diagram illustrating the core mental model — data flow, component relationships, or state machine as appropriate}
```

**What you need to hold in your head to use this well:**
- {concept 1}
- {concept 2}
- {concept 3}

---

### Core Concepts

For each fundamental concept (aim for 4–8):

**{Concept name}**

*What it is:* {1–2 sentences, plain English}

*Why it matters:* {the consequence of misunderstanding this concept}

*{If codebase provided}* — In this codebase: `{path/to/example.ts}` shows this when it {does X}.

```{language}
{short illustrative code snippet — from the codebase if available, otherwise minimal illustrative example}
```

---

### How It Works Internally

{Just enough internals to reason about behaviour under pressure — not a full implementation walkthrough. Cover: the architecture, the data path, the persistence or consistency model, and the failure behaviour. Skip implementation details that don't affect how you use it.}

```mermaid
{internal architecture or data flow diagram}
```

**What this means practically:**
- {implication 1 — e.g. "because writes go to the leader first, there is always some replication lag"}
- {implication 2}
- {implication 3}

---

### Key Patterns

For each major usage pattern — cover what the codebase uses first, then the patterns it doesn't use:

**Pattern: {name}**

*When to use it:* {the problem this pattern solves}

*How it works:* {mechanism in 2–3 sentences}

*{If codebase provided}* — This codebase uses it in `{path/to/file}`:

```{language}
{real code from the codebase, or illustrative example}
```

*What experienced engineers watch out for:* {the non-obvious gotcha}

*Alternative:* {when you'd reach for a different pattern instead}

---

### What This Codebase Uses (and Doesn't)

*{This section only appears when a codebase path is provided.}*

| Feature / Pattern | Used here? | Where |
|---|---|---|
| {feature} | Yes | `{path/to/file}` |
| {feature} | No | — |

**Features unused but worth knowing:**
- **{feature}:** {when you'd add it, what problem it solves, why this project probably doesn't need it yet}

---

### Operational Concerns

**Deployment model:** {how this technology is typically deployed — sidecar, managed service, self-hosted cluster}

**Scaling:** {how it scales, what the bottlenecks are, what "too much load" looks like}

**Persistence and durability:** {what data survives a restart, a crash, a partition}

**Failure modes:**
- {what happens when the technology is unavailable — how dependent services should handle it}
- {what happens under memory/disk/connection pressure}
- {what breaks silently vs. loudly}

**Observability:** {key metrics to watch, what a healthy instance looks like vs. a degrading one}

**Cost levers:** {what drives cost in managed offerings — connections, storage, compute, egress}

---

### Common Mistakes

For each mistake — what it looks like, why engineers fall into it, and what to do instead:

**Mistake: {name}**

*What it looks like:* {code pattern or configuration}

*Why it's wrong:* {consequence}

*What to do instead:* {correct approach with example}

---

### When NOT to Use It

{3–5 bullets. Be specific about which alternative to reach for in each case.}

- **If {condition}**, use {alternative} instead because {reason}
- **If {condition}**, you probably don't need this technology at all — {simpler solution}

---

### Alternatives and Tradeoffs

| Alternative | Better when | Worse when |
|---|---|---|
| `{alternative}` | {condition} | {condition} |

**How to decide:**
{A short decision framework — 3–4 questions to ask that lead you to the right choice.}

---

### Learning Path

**Milestone 1 — Functional (hours)**
You can use it without breaking things:
- [ ] Understand the mental model and core concepts above
- [ ] Run a local instance (link to quickstart)
- [ ] Complete one end-to-end operation: {specific operation, e.g. "set a key, read it back, observe expiry"}
- [ ] {If codebase provided} Read `{entry-point file}` and trace one operation end-to-end

**Milestone 2 — Proficient (days)**
You can design with it:
- [ ] Understand all key patterns and when to choose each
- [ ] Know the failure modes and how to handle them in application code
- [ ] Write a test that exercises {the technology} without mocking it
- [ ] {If codebase provided} Add a new {common operation} to the codebase unassisted

**Milestone 3 — Confident (weeks)**
You can operate and advise on it:
- [ ] Understand the internals well enough to diagnose degraded behaviour
- [ ] Know the scaling limits and how to push past them
- [ ] Have an opinion on the alternatives and when to switch
- [ ] Have debugged at least one production issue involving this technology

**Highest-value things to read next:**
- {Official docs section most worth reading — specific page, not just "the docs"}
- {A known architecture post, conference talk, or design doc if the technology has one worth citing — only if you are confident it exists and is accurate}
- {If codebase provided} `{specific file in the codebase}` — {why this file teaches the most}

---

## Examples

```
/learn-technology Redis
```
Teaches Redis from first principles — data structures, eviction, persistence, pub/sub, clustering — with illustrative examples.

```
/learn-technology Kafka services/events
```
Teaches Kafka concepts, using real producer/consumer code from `services/events` as examples.

```
/learn-technology Prisma --beginner
```
Assumes no ORM experience; expands explanations of schema-first design, migrations, and the query engine.

```
/learn-technology "React Query" --advanced --save
```
Skips basics; focuses on internals, cache invalidation strategies, and edge cases. Writes to `React Query-learning-guide.md`.

## Gotchas

- **Version first, always.** A major version boundary (e.g. React Query v4 → v5, Prisma 4 → 5) can invert the recommended patterns. Confirm the version before teaching anything API-specific.
- **Fetch docs for the right version.** Official docs often default to the latest version. If the codebase pins an older major, navigate to the versioned docs explicitly — otherwise you'll teach patterns the pinned version doesn't support.
- **Don't conflate general gotchas with project-specific ones.** General "Redis gotcha: key expiry is lazy" belongs here. "This project's cache helper silently swallows expiry errors" belongs in `/tech-deep-dive`. Keep the separation clean.
- **Codebase examples are illustrations, not the subject.** If the codebase uses a technology in a non-idiomatic way, show the example but label it clearly — "this project does X; the idiomatic approach is Y." The learner should leave understanding both.
- **The "When NOT to Use It" section is not optional.** Engineers learn more from understanding the boundaries of a tool than from its happy path. If you're tempted to skip this section because the technology seems universally applicable, that's exactly when it matters most.
- **Avoid citing resources you can't verify exist.** Blog posts, conference talks, and architecture docs mentioned in the learning path must be things you are confident are real and accurate — not plausible-sounding links. If uncertain, describe what to search for rather than naming a specific resource.
- This skill pairs naturally with `/tech-deep-dive` (zoom into how this specific codebase uses the technology after building general understanding), `/reverse-engineer` (whole-system architectural context before going deep on one piece), and `/write-tests` (add test coverage for the technology once you understand how it works).
