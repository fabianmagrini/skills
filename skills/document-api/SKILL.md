---
name: document-api
description: Reverse-engineer an existing API from source code — routes, controllers, models, and middleware — and produce a complete OpenAPI 3.x specification for what is actually implemented.
compatibility: Requires Read, Glob, Grep for local codebases. Requires a local path — this skill cannot operate on a running service without source access.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Read the codebase and produce an OpenAPI specification that accurately reflects what the API actually does — not what it was intended to do.

This is the brownfield counterpart to `/design-api`. Use this skill when the code exists but the spec does not (or is stale). Use `/design-api` when designing a new API from requirements.

## Determine the target

Accept any of:
- A service directory: `services/payments/`, `src/api/`
- A specific router or controller file: `src/routes/orders.ts`, `app/controllers/users_controller.rb`
- A service name: `orders API`, `auth service`

If a directory is given, discover all route and controller files within it. If a file is given, read it and trace outward to find related models and middleware. If only a name is given, search the codebase for matching route files before proceeding.

Also accept:
- `--update path/to/spec.yaml` — update an existing partial or stale OpenAPI spec rather than generating from scratch

If an existing OpenAPI spec is found for the target, switch to update mode automatically and flag it.

## Discovery steps

Read the following before writing any YAML. Every endpoint, schema, and security definition in the output must be grounded in what was found — do not invent endpoints or fields.

### 1. Find all routes

Glob and grep for route registration patterns:

- **Express/Node**: `router.get`, `router.post`, `app.get`, `.route(`, `@Controller`, `@Get`, `@Post`
- **FastAPI/Flask**: `@app.route`, `@router.get`, `@app.get`, `Blueprint`
- **Rails**: `routes.rb`, `resources :`, `get '`, `post '`
- **Go**: `mux.Handle`, `r.GET`, `http.HandleFunc`, `chi.Route`
- **Spring**: `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@RestController`

For each route, record: HTTP method, path pattern, handler function name, and source file location.

### 2. Read each handler

For every route found, read the handler function to extract:
- **Path parameters** — variables in the URL pattern (`:id`, `{id}`, `<int:id>`)
- **Query parameters** — `req.query.*`, `request.args`, `ctx.Query()`, `@RequestParam`
- **Request body** — what schema is read from the body; look for validation schemas (`zod`, `joi`, `pydantic`, `class-validator`, `@Body`)
- **Response body** — what the handler returns; read the return statements and response serializers
- **Status codes** — every `res.status(N)`, `return Response(status=N)`, `c.JSON(N,`, `ResponseEntity<>(HttpStatus.N)`
- **Error responses** — explicit error returns and thrown exceptions that map to HTTP responses

### 3. Read data models

Glob for model, entity, and schema files:
- `**/models/**`, `**/entities/**`, `**/*.model.ts`, `**/*.entity.ts`
- `**/schemas/**`, `**/types/**`, `**/dto/**`, `**/*.dto.ts`
- ORM models: `sequelize.define`, `mongoose.Schema`, `@Entity`, `class *Model`

For each model referenced by a handler, read its field definitions — names, types, nullability, and relationships. The OpenAPI schema must use the actual field names from the model, not invented names.

### 4. Read validation schemas

Grep for validation libraries and read the schemas applied to request bodies:
- `zod`: `z.object({`, `z.string()`, `z.number()`
- `joi`: `Joi.object({`
- `pydantic`: `class *Request(BaseModel)`, field types and `Field()`
- `class-validator`: `@IsString()`, `@IsNotEmpty()`, `@IsOptional()`
- `express-validator`: `body('field')`

Validation schemas are the authoritative source for request body shape and required fields — prefer them over what the handler reads from the body directly.

### 5. Read authentication middleware

Grep for auth middleware applied to routes:
- `authenticate`, `requireAuth`, `verifyToken`, `@UseGuards`, `@login_required`, `authMiddleware`
- Check both route-level and router-level middleware application

For each route, determine: is it authenticated? What mechanism (Bearer token, API key, session cookie, OAuth2 scope)? Note unauthenticated routes explicitly — they may be intentional (health checks, public endpoints) or gaps.

### 6. Check for existing specs

Glob for `**/openapi.yaml`, `**/openapi.yml`, `**/swagger.json`, `**/*api*.yaml`:
- If found, read it and compare against the routes discovered — identify endpoints in the spec that no longer exist in the code (stale) and routes in the code with no spec entry (undocumented)
- In update mode, reuse the existing spec's `info`, `servers`, and `components.securitySchemes` blocks where still accurate

### 7. Identify the API version and base path

Grep for version prefixes in route patterns (`/v1/`, `/v2/`, `/api/`) and read any version config or base URL settings. Check `package.json` `version` field or equivalent for the service version.

## Output format

Write to `docs/api/{kebab-case-service}.openapi.yaml` by default. If the user passes `--inline`, respond inline instead.

Produce a complete, valid OpenAPI 3.1.0 YAML specification:

```yaml
openapi: "3.1.0"
info:
  title: {Service Name} API
  version: "{version from package.json or 1.0.0}"
  description: |
    {1–2 sentence description of the service derived from README or package.json}

servers:
  - url: "{base path found in routes, e.g. /api/v1}"
    description: "{environment — default to 'API base'}"

components:
  securitySchemes:
    {scheme name}:
      type: {http / apiKey / oauth2}
      scheme: {bearer / basic — for http type}
      bearerFormat: {JWT — if applicable}

  schemas:
    {ResourceName}:
      type: object
      required: [{required fields from validation schema}]
      properties:
        {field}:
          type: {type}
          description: {description if inferrable}

    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string

paths:
  {/path/{param}}:
    {method}:
      summary: {inferred from handler name or route structure}
      operationId: {camelCase — verb + Resource, e.g. listOrders}
      tags: [{resource name}]
      security:
        - {schemeName}: []  # omit for unauthenticated routes
      parameters:
        - name: {param}
          in: {path / query}
          required: {true / false}
          schema:
            type: {type}
      requestBody:  # only for POST/PUT/PATCH
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/{RequestSchema}'
      responses:
        "{status}":
          description: {description}
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/{ResponseSchema}'
```

**Required for every operation:**
- `summary`, `operationId`, `tags`, `security` (or explicit note that it is public)
- All path and query parameters found in the handler
- All response status codes found in the handler — including error responses
- `$ref` for all non-trivial schemas — no inline complex schemas

**After the YAML, provide:**

### Coverage report

| Route | Method | Handler | Documented | Notes |
|-------|--------|---------|-----------|-------|
| `/path` | GET | `handlerName` | ✅ | — |
| `/path` | POST | `handlerName` | ✅ | — |
| `/path/:id` | DELETE | `handlerName` | ⚠️ | Response schema inferred — no validation found |

Mark each route:
- ✅ Fully documented — handler read, schemas grounded in models/validation
- ⚠️ Partially documented — handler read but request or response schema inferred
- ❌ Undocumented — route found but handler could not be resolved

### Gaps and assumptions

Bullet list of anything that could not be determined from static analysis:
- Response schemas that were inferred from return statements rather than a typed schema
- Status codes that may exist but were not found in explicit response calls
- Auth requirements that were unclear (middleware applied conditionally or via config)
- Routes that exist in a spec but not in the current code (stale spec entries)

## Gotchas

- Do not invent field names. If the model uses `created_at`, the schema must use `created_at` — not `createdAt`. Read the actual model files.
- Do not assume authentication. Read the middleware chain for each route. An endpoint that looks sensitive may be intentionally public; an endpoint that looks innocuous may be behind auth. State what you found.
- `operationId` must be unique across the entire spec. Check for collisions before writing — two handlers with the same name on different resources will collide.
- Inferred response schemas are a gap, not a feature. When a handler returns an ORM model directly without a serializer, flag this — the API contract is whatever the ORM model exposes, which may include sensitive fields.
- Routes registered via dynamic patterns (loop-registered routes, plugin systems, generated controllers) may not be discoverable by static analysis. Note this limitation explicitly if found.
- A stale spec is worse than no spec. If the existing spec documents endpoints that no longer exist, mark them `deprecated: true` or remove them — do not leave phantom endpoints in the output.
- Pagination is a common omission. If a list endpoint returns an array without pagination parameters, flag it in Gaps — unbounded list responses are a latency risk.
- This skill pairs naturally with `/design-api` (when documented gaps reveal missing or poorly designed endpoints that warrant a redesign), `/review-code` (reviewing the handlers that were read during discovery), and `/threat-model` (the coverage report surfaces unauthenticated endpoints that warrant security review).
