---
name: map-api-flow
description: Map the full API call chain from frontend UI components through the API layer, across the network boundary, to backend controllers and services. Produces a Mermaid.js diagram and a bullet-point summary of critical data flow paths.
compatibility: Requires Read, Glob, Grep tools for local paths.
allowed-tools: Read Glob Grep Agent
metadata:
  author: fabianmagrini
  version: "2.0"
  last-updated: 2026-05-10
---

Scan the codebase and produce a Mermaid.js diagram that traces every API call chain end-to-end, then summarise the critical paths in bullet points.

## Determine the target

Accept any of:
- A directory (default: entire repo): `src/`
- A specific feature or flow: `user authentication`, `checkout`
- A specific frontend component or backend route: `UserProfile.tsx`, `/api/v1/orders`

If no target is given, scan the full codebase. However, if the codebase has more than ~50 component files, recommend scoping to a single feature or route prefix first rather than producing an unreadable mega-diagram.

For monorepos, detect workspace packages (look for `pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`, or `packages/` directories) and ask the user which app to scope to before scanning.

For large or deep codebases, use an Agent subagent (`subagent_type: Explore`) for traversal rather than exhaustive Glob/Grep in a single pass.

## Discovery steps

Work through each layer in order, reading representative files:

### 1. Frontend components
- Glob for component files: `**/*.{tsx,jsx,vue,svelte}`
- Identify user actions that trigger API calls (button clicks, form submits, page loads, hooks like `useEffect`)
- Note the component name and the action that initiates the call
- For **Next.js App Router**: identify Server Components that call the backend directly (no network boundary), Server Actions (`"use server"` functions), and Route Handlers (`app/api/**/route.ts`)

### 2. State management layer (if present)
- Glob for store files: `**/store/**`, `**/stores/**`, `**/*.store.{ts,js}`, `**/slices/**`
- Identify async dispatches that sit between UI and API calls:
  - Redux: `createAsyncThunk`, `createApi` (RTK Query)
  - Zustand / Jotai / Pinia action functions
- Include these as intermediate nodes between the component and the API layer

### 3. Frontend API layer
- Glob for API utility files: `**/api/**`, `**/services/**`, `**/lib/**`, `**/utils/**`
- Look for HTTP client usage: `axios`, `fetch`, `ky`, `got`, `$http`, `useSWR`, `useQuery`, `createAsyncThunk`
- For **tRPC**: trace from the client router call site (e.g. `trpc.user.getById.query()`) to the procedure definition — do not trace into generated files
- For **GraphQL**: identify queries, mutations, and subscriptions separately; note the operation name and variables shape
- For **WebSockets / SSE**: look for `new WebSocket(`, `socket.io`, `EventSource`, `useWebSocket` — these need separate sequence diagrams from REST flows
- Note where the bearer token / auth header is injected (interceptor, header function, wrapper) — mark this as an `AuthInterceptor` node
- Extract: HTTP method, URL/path template, request payload shape, response handling

### 4. Network boundary
- Identify base URLs and path prefixes from config files, `.env` examples, or constants
- Note each unique route: method + path (e.g. `POST /api/v1/users`)
- Identify any **BFF (Backend for Frontend)** proxy layer (Next.js rewrites, Express proxy, API gateway) — if present, add a BFF node between the browser and the true backend

### 5. Middleware chain
- Glob for middleware files: `**/middleware/**`, `**/*.middleware.{ts,js,py}`, `**/app.{ts,js,py}`
- Identify auth, validation, rate-limiting, and logging middleware that runs before the controller
- Include these as intermediate nodes on the relevant routes; note if any routes are missing auth middleware

### 6. Backend routing
- Glob for route definition files: `**/routes/**`, `**/router/**`, `**/*.router.{ts,js}`, `**/app.{ts,js,py}`, `**/urls.py`, `**/routes.go`
- Map each route to its handler function and file

### 7. Backend controllers / handlers
- Read the handler files identified above
- Trace calls to services, repositories, or database clients
- Note any external service calls (third-party APIs, queues, caches)
- Look for queue/job dispatch patterns: Bull/BullMQ (`queue.add`), Celery (`.delay`, `.apply_async`), Sidekiq — include these as side-effect nodes

### 8. Backend services / data layer
- Read service and repository files
- Identify database queries (ORM calls, raw SQL, NoSQL operations)
- Note the entity or table being read or mutated

### 9. Caching layer
- Look for Redis/Memcached usage in backend services (`ioredis`, `redis-py`, `node-cache`)
- Check for HTTP cache headers (`Cache-Control`, `ETag`) and CDN configuration
- Note frontend cache settings (`staleTime`, `dedupingInterval`) in query clients
- Include cache nodes in the diagram where a cache hit short-circuits the backend call

## Output format

Respond inline — do NOT write a file unless the user passes `--save` or explicitly asks to write the output to a file.

### API Flow Map: `{target}`

**Mermaid Diagram**

Choose the most appropriate diagram type:
- `graph TD` — for a dependency/call graph showing the overall architecture
- `sequenceDiagram` — for a single flow showing the request/response lifecycle

Prefer `sequenceDiagram` when tracing a specific feature flow. Use `graph TD` when mapping the full system. Include both if the target warrants it.

For **real-time flows** (WebSocket, SSE, GraphQL subscriptions), produce a separate `sequenceDiagram` showing the connection lifecycle and message flow — do not mix these with request/response diagrams.

**graph TD labelling rules:**
- Use `subgraph` blocks to group nodes into visual lanes: `Frontend`, `Backend`, `DataLayer`, `Cache`, `External`
- Frontend nodes: use component/file names (e.g. `LoginForm.tsx`)
- API layer nodes: use function/hook names (e.g. `authApi.login()`)
- Network boundary: label edges with `HTTP METHOD /path` (e.g. `POST /api/v1/auth/login`)
- Backend nodes: use `filename:functionName` notation (e.g. `auth.controller.ts:login`)
- Data layer nodes: use `ServiceName → Table/Collection` (e.g. `UserService → users`)
- Auth/middleware nodes: use `[MiddlewareName]` notation (e.g. `[AuthMiddleware]`)

**sequenceDiagram rules:**
- Always include `autonumber` so step references in the bullet summary are unambiguous
- Participants: `Browser`, `Store` (if applicable), `APIClient`, `BFF` (if applicable), `[AuthMiddleware]`, `Controller`, `Service`, `DB`, `Cache`, `ExternalAPI`

```mermaid
{diagram here}
```

**Diagram Legend**

```
Nodes:  Component (Frontend)  |  fn() (API layer)  |  [Middleware]  |  controller:fn (Backend)  |  Service→Table (Data)
Edges:  HTTP METHOD /path  |  → direct call  |  -.-> async/queue
```

**Critical Data Flow Paths**

Bullet list — one bullet per distinct end-to-end path. Reference sequence diagram step numbers where applicable. Format:

- **{Flow name}**: `ComponentName` → `apiFn()` → `METHOD /route` → `[Middleware]` → `controller:fn` → `Service → DB`

Always include the error path for the network boundary edge (4xx/5xx handling) — this is the most commonly missing piece. Format:

- **{Flow name} (error)**: `apiFn()` ← `4xx/5xx` ← `controller:fn` → (error response shape)

**Route Summary Table**

| Route | Handler | Service | DB Table/Collection | Auth? | Cache? |
|-------|---------|---------|---------------------|-------|--------|
| `METHOD /path` | `file:fn` | `ServiceName` | `table` | yes/no | yes/no |

**Observations**

5–8 bullets covering:
- Missing error handling at the network boundary
- Unauthenticated routes (routes lacking auth middleware)
- N+1 query patterns
- Missing pagination on list endpoints
- Missing rate limiting
- Overly coupled layers or missing service abstractions
- Opportunities for caching (repeated identical queries, missing cache headers)
- Feature-flag-gated code paths that branch the API call (LaunchDarkly, etc.) — note these as branching edges

## Gotchas

- Dynamic route segments (e.g. `/users/:id`) should be shown as-is, not with example values.
- If the frontend uses a generated API client (OpenAPI, tRPC, gRPC), note that and trace from the generated call site, not the generated file itself.
- Some backends use middleware for auth/validation before the controller — include these as intermediate nodes (discovery step 5 above).
- Monorepos may have multiple apps; scope the diagram to one app at a time unless asked for the full picture.
- If a layer cannot be located (e.g. backend is a separate repo), note the boundary as `External API` and stop there.
- **BFF pattern**: if a Next.js or Express proxy sits between the browser and the true backend, the diagram must include a BFF node at the network boundary — the browser never calls the origin directly.
- **Feature flags**: if the code has conditional API call paths gated by feature flags, represent these as branching edges in the diagram rather than omitting the alternate path.
- **Auth token injection**: surface where the bearer token is attached (interceptor, header helper, middleware) as an `AuthInterceptor` or `AuthMiddleware` node — this is a common source of bugs.
- **Server Components (Next.js App Router)**: these call the backend in-process with no HTTP boundary — represent with a direct `→` edge, not an HTTP edge.
- This skill pairs naturally with `/design-api` (formalizing a discovered API surface into an OpenAPI or GraphQL spec), `/document-api` (if the API already exists without a spec, generate the OpenAPI definition from the mapped routes), and `/review-code` (reviewing the code within an identified call chain for correctness or security).
