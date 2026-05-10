---
name: design-api
description: Design a REST (OpenAPI 3.x) or GraphQL API for a feature or service — covering resources, operations, request/response schemas, error states, pagination, auth, and versioning.
compatibility: Accepts natural language descriptions. Optionally reads existing API specs, data models, and auth middleware to ground the design in the current system.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Design a complete, production-quality API specification for the given feature or service.

## Determine the target

Accept any of:
- A feature or service description: `subscription and billing management`, `passkey authentication`, `semantic search`
- A local path for context: `src/services/payments/`, `src/models/`
- A combination: `src/orders/ — add a returns and refunds API`

Also accept an explicit style flag:
- `--rest` — produce an OpenAPI 3.x YAML specification
- `--graphql` — produce a GraphQL SDL schema
- `--both` — produce both

If no style flag is given, infer from the codebase (detect existing specs or schemas) or default to REST.

## Discovery steps (for local targets)

### 1. Existing API contracts
- Glob for `**/openapi.yaml`, `**/openapi.yml`, `**/swagger.json`, `**/swagger.yaml` — read to understand the current API surface, versioning strategy, and schema conventions
- Glob for `**/*.graphql`, `**/schema.graphql`, `**/typeDefs.ts` — read to understand existing GraphQL types and conventions
- The new design must extend, not conflict with, the existing surface

### 2. Data models
- Glob for ORM model files (`**/models/**`, `**/entities/**`, `**/*.model.ts`, `**/*.entity.ts`, `**/schemas/**`)
- Read to understand the actual data shapes, field names, types, and relationships
- The API schema must align with the underlying data model — do not invent field names that differ from the model

### 3. Authentication
- Grep for auth middleware (`authenticate`, `requireAuth`, `verifyToken`, `@login_required`, `authMiddleware`)
- Identify the auth mechanism: Bearer token, API key, session cookie, OAuth2
- Every endpoint in the design must declare its security requirement explicitly

### 4. Existing routes
- Glob for route files (`**/routes/**`, `**/controllers/**`, `**/handlers/**`, `**/urls.py`, `**/routes.go`)
- Check for conflicts with existing endpoints before proposing new paths

## Design process

Work through the following before writing the specification:

### 1. Identify resources
What are the primary entities this API exposes? For each resource:
- Name (noun, plural for REST: `subscriptions`, `invoices`)
- Ownership (who can access it, is it user-scoped or global)
- Lifecycle (what states can it be in)
- Relationships (what other resources does it relate to)

### 2. Identify operations
For each resource, determine which operations are needed:
- Standard CRUD: List, Get, Create, Update (full/partial), Delete
- Domain-specific: `POST /subscriptions/{id}/cancel`, `POST /payments/{id}/refund`
- Avoid verbs in REST paths — model domain actions as sub-resources or state transitions

### 3. Identify cross-cutting concerns
Before writing schemas, decide:
- **Pagination**: cursor-based (for large/real-time datasets) or offset-based (for simple cases). Define the request params and response envelope.
- **Versioning**: URL prefix (`/v1/`), header (`API-Version`), or content negotiation. Match existing convention if present.
- **Idempotency**: POST operations that create resources should support an `Idempotency-Key` header where repeat requests are safe.
- **Rate limiting**: Decide whether to document `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` response headers.
- **Error format**: Define a consistent error response schema used across all 4xx/5xx responses.

## REST output: OpenAPI 3.x

Produce a complete, valid OpenAPI 3.x YAML specification.

**Required elements:**
- `openapi: "3.1.0"` (prefer 3.1 for JSON Schema alignment)
- `info` block with title, version, and description
- `servers` block with at least one entry
- `components.securitySchemes` defining the auth mechanism
- `components.schemas` for every request body, response body, and error type — use `$ref` throughout, never inline complex schemas
- Every path operation must declare: `summary`, `operationId` (camelCase), `tags`, `security`, `parameters`, `requestBody` (if applicable), and `responses`
- Every response must include a schema — no empty responses except `204 No Content`
- Error responses: `400` (validation), `401` (unauthenticated), `403` (unauthorized), `404` (not found), `409` (conflict), `422` (unprocessable), `429` (rate limited), `500` (server error) — include only those relevant to each operation

**Pagination envelope** (for list operations):
```yaml
components:
  schemas:
    PaginatedResponse:
      type: object
      required: [data, meta]
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/{Resource}'
        meta:
          $ref: '#/components/schemas/PaginationMeta'
    PaginationMeta:
      type: object
      required: [total, page, per_page, next_cursor]
      properties:
        total:
          type: integer
        page:
          type: integer
        per_page:
          type: integer
        next_cursor:
          type: string
          nullable: true
```

**Error schema**:
```yaml
components:
  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          description: Machine-readable error code
        message:
          type: string
          description: Human-readable description
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
```

## GraphQL output: SDL schema

Produce a complete GraphQL SDL schema.

**Required elements:**
- `Query` type with all read operations
- `Mutation` type with all write operations
- `Subscription` type if real-time updates are needed
- Input types for all mutations (suffix with `Input`: `CreateSubscriptionInput`)
- Payload types for mutations (suffix with `Payload`: `CreateSubscriptionPayload`) — include `errors` field for operation-level errors
- Connection pattern for paginated lists (following Relay spec):
  ```graphql
  type SubscriptionConnection {
    edges: [SubscriptionEdge!]!
    pageInfo: PageInfo!
  }
  type SubscriptionEdge {
    cursor: String!
    node: Subscription!
  }
  type PageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }
  ```
- Every field that can be null must be nullable; fields that are always present must be non-null (`!`)
- Use enums for fields with a fixed set of values
- Add `"""docstring"""` to every type, field, query, and mutation

## Output format

By default respond inline. If the user passes `--save`, write to:
- REST: `docs/api/{kebab-case-name}.openapi.yaml`
- GraphQL: `docs/api/{kebab-case-name}.graphql`

After the specification, provide:

**Design decisions**

Bullet list of non-obvious choices made and why:
- Why cursor vs offset pagination
- Why a specific error format
- Any deviations from REST conventions and their justification

**Open questions**

Decisions that require product or team input before the spec can be finalized:
- Fields whose nullability is uncertain
- Operations whose authorization rules need clarification
- Rate limit values that depend on infrastructure capacity

**Implementation notes**

What a backend engineer needs to know to implement this spec:
- Which endpoints are idempotent and how
- Auth validation requirements per endpoint
- Any async operations that should return `202 Accepted` with a polling pattern

## Gotchas

- Do not produce a spec that only covers the happy path. Every operation must define its error responses. An API spec without error definitions is incomplete.
- List endpoints must have pagination. An unbounded list endpoint is a latency and memory time bomb — never design one without a `limit` parameter at minimum.
- `operationId` values must be unique across the entire spec. Use the pattern `{verb}{Resource}` (e.g. `listSubscriptions`, `createSubscription`, `cancelSubscription`).
- Do not use `additionalProperties: false` on request bodies without considering forward-compatibility — it breaks clients that send fields the server doesn't yet know about.
- GraphQL mutations must return a payload type, not the resource directly. Returning the resource makes it impossible to add errors or metadata without a breaking change.
- Nullable vs required is a contract commitment. Fields marked required and non-null cannot later become optional without a breaking change. When in doubt, make fields optional and nullable.
- If the existing codebase uses a specific error format (e.g. JSON:API errors, RFC 7807 Problem Details), match it — do not introduce a new error format.
- Document `deprecated: true` on any operations or fields being replaced, with a pointer to the replacement.
- This skill pairs naturally with `/write-adr` (documenting the API design decisions), `/threat-model` (security analysis of the API surface — auth, input validation, rate limiting), and `/draft-rfc` (for significant new APIs that warrant team review before implementation).
