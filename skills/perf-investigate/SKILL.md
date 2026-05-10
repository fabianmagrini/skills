---
name: perf-investigate
description: Diagnose performance bottlenecks in a system or codebase — latency, CPU, memory, or throughput — and produce a latency tree, suspect list, cache opportunities, and a concrete profiling plan.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts natural language descriptions of symptoms without file access.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Diagnose the performance problem and produce an actionable investigation plan.

## Determine the target

Accept any of:
- A symptom description: `checkout latency`, `node memory leak`, `slow search queries`
- A file or directory: `src/payments/processor.ts`, `services/search/`
- A flow: `user login`, `order submission`
- A combination: `src/api/orders — high p99 latency`

If a local path is given, read the relevant source files before diagnosing. Ground every finding in what the code actually does — do not speculate about code you have not read.

If only a symptom is given, derive likely causes from the description, state your assumptions, and structure the profiling plan around confirming or ruling them out.

## Discovery steps (for local targets)

### 1. Read the hot path
Trace the execution path for the target flow from entry point to response. Read each file in the chain: route handler → middleware → service → data layer. Note every I/O operation, external call, and computation-heavy step.

### 2. Identify I/O operations
Grep for database queries (`findOne`, `findAll`, `query`, `execute`, `SELECT`, `cursor`), HTTP client calls (`fetch`, `axios`, `got`, `requests.get`, `http.Get`), and filesystem access (`fs.read`, `open`, `readFile`). For each:
- Is it inside a loop? (N+1 risk)
- Is it sequential where it could be parallel?
- Is there a cache in front of it?

### 3. Check for N+1 patterns
Grep for ORM calls inside loops or `.map()` / `.forEach()` / list comprehensions. Look for `findOne` called per item in a collection result. N+1 is the single most common source of latency regression.

### 4. Assess caching
Grep for cache usage (`redis`, `memcached`, `lru-cache`, `@Cacheable`, `cache.get`, `staleTime`, `Cache-Control`). For each cacheable resource not already cached, note the read frequency and data volatility.

### 5. Check indexes and queries
Grep for raw SQL or ORM query builders. Look for:
- Queries without `WHERE` clauses on large tables
- `SELECT *` instead of projected columns
- Missing `LIMIT` on list queries
- Sort operations on unindexed columns (`ORDER BY` without an index)
- Missing eager loading (`.include`, `JOIN`, `.prefetch_related`) causing N+1

### 6. Identify memory suspects (for memory issues)
Grep for unbounded collections (`push` inside loops without eviction, growing maps/sets, event listeners without `removeListener`). Look for large object retention across requests (module-level caches, closures over large data, circular references).

### 7. Check concurrency and blocking
Grep for synchronous I/O in async contexts (`readFileSync`, `execSync`, blocking loops on the event loop). Look for missing `Promise.all` where sequential `await` is used on independent operations.

### 8. Review existing observability
Look for metrics, tracing, and logging setup (`opentelemetry`, `datadog`, `prometheus`, `pino`, `winston`). Note what instrumentation already exists and what is missing from the hot path.

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/perf/{kebab-case-target}.md`.

### Performance Investigation: `{target}`

**Symptom Summary**

1–2 sentences: what the reported problem is, what metric is affected (latency, memory, CPU, throughput), and any known reproduction conditions.

**Latency Tree** (for latency / throughput problems)

Decompose the end-to-end time budget for the target flow. Use an ASCII tree or Mermaid `graph TD`. For each node, estimate or note where timing data would come from:

```
Request (total: ~Xms)
├── Middleware (auth, validation): ~Xms
├── Service layer
│   ├── DB query 1 (users): ~Xms
│   ├── DB query 2 (orders): ~Xms  ← N+1 risk
│   └── External API call: ~Xms
└── Serialization: ~Xms
```

Mark unknowns explicitly as `~?ms (unmeasured)` — do not invent numbers.

**Suspects**

Ordered by likely impact. For each:

> **[HIGH/MEDIUM/LOW] Category — Short title**
> What the issue is, where it appears in the code (file:line or pattern), and why it causes the symptom.
> *Fix:* Concrete, specific change — query optimization, batching, caching, parallelization, index addition.

Categories: `N+1 Query`, `Missing Index`, `Unbounded Query`, `Sequential I/O`, `Missing Cache`, `Memory Leak`, `Blocking Call`, `Over-fetching`, `Missing Pagination`.

**Cache Opportunities**

| Resource | Current | Read Frequency | Volatility | Recommended Cache | TTL |
|----------|---------|---------------|------------|------------------|-----|
| e.g. user profile | no cache | high | low | Redis / in-memory | 5m |

Only include resources that are genuinely cacheable — do not recommend caching mutable, user-specific, or consistency-critical data without noting the invalidation strategy.

**Profiling Plan**

Ordered steps to measure and confirm suspects before fixing. Each step should be runnable independently:

1. **{Step title}** — what to measure, how to measure it (tool, query, trace span), and what result confirms or rules out this suspect.

Suggest concrete tools appropriate to the tech stack detected: `EXPLAIN ANALYZE` for SQL, `clinic.js` / `0x` for Node.js CPU, `py-spy` for Python, `pprof` for Go, `async_profiler` for JVM, browser DevTools Performance panel for frontend.

**Quick Wins**

Bullet list of changes that are low-risk and high-confidence — fixable in a single PR without profiling data:
- e.g. Add `LIMIT` to unbounded list query in `orders.service.ts:42`
- e.g. Parallelize independent API calls with `Promise.all` in `checkout.service.ts:88`

**Observability Gaps**

What instrumentation is missing that would make this easier to diagnose in production:
- Missing trace spans around the external API call
- No slow-query logging configured
- No memory usage metric exported

## Gotchas

- Do not invent latency numbers. Mark unmeasured segments as `~?ms` and make measuring them the first step of the profiling plan.
- N+1 issues inside a single request are almost always higher impact than application-level caching. Fix data access patterns before adding cache layers.
- For memory leaks, distinguish between a one-time growth (large allocation) and a continuous leak (unbounded retention). They have different fixes.
- Synchronous I/O on the Node.js event loop is a blocking call for all concurrent requests — flag it as HIGH regardless of how fast the individual operation is.
- Do not recommend adding indexes without checking whether one already exists (`SHOW INDEXES`, `\d tablename`, `pg_indexes`). Read the schema or migration files first.
- Cache recommendations must include an invalidation strategy. A cache without invalidation is a bug waiting to happen.
- This skill pairs naturally with `/write-adr` (documenting the chosen optimization approach and the trade-offs considered) and `/refactor-strategy` (when the investigation surfaces a structural problem that requires a phased refactor rather than a targeted fix).
