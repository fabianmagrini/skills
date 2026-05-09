---
name: threat-model
description: Apply STRIDE threat modelling to a system, component, or architecture description to identify threat vectors, trust boundaries, abuse cases, and mitigations.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts natural language descriptions without file access.
allowed-tools: Read Glob Grep
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Produce a STRIDE threat model for the target system or component.

## Determine the target

Accept any of:
- A natural language description: `payments API`, `webhooks delivery system`
- A file or directory: `src/auth/`, `src/payments/processor.ts`
- An architecture component: `multi-tenant SaaS auth layer`

If a file or directory is given, read the relevant source files to infer the architecture before modelling. Focus on: entry points, authentication/authorization logic, data flows, external service calls, and persistence layers.

If only a description is given, derive the architecture from the description and state your assumptions explicitly before proceeding.

## Discovery steps (for local targets)

1. **Entry points** — Glob for route/controller files (`**/routes/**`, `**/controllers/**`, `**/handlers/**`, `**/urls.py`, `**/routes.go`). List every public-facing endpoint and its auth requirements.

2. **Authentication & authorization** — Grep for auth middleware, JWT/session handling, role checks (`authenticate`, `authorize`, `@login_required`, `requireAuth`, `verifyToken`). Note any routes that bypass auth.

3. **Data flows** — Identify where user-controlled input enters the system, how it is validated, and where it reaches persistence or external calls.

4. **External dependencies** — Note third-party APIs, queues, databases, and caches. Each is a trust boundary.

5. **Secrets & config** — Grep for secret handling (`process.env`, `os.environ`, `getenv`, `config.`). Flag any secrets that appear hardcoded or logged.

## STRIDE analysis

Work through each STRIDE category for the target. For each identified threat, rate likelihood (Low / Medium / High) and impact (Low / Medium / High), then suggest a concrete mitigation.

| Category | What to look for |
|----------|-----------------|
| **Spoofing** | Can an attacker impersonate a user, service, or identity? Missing auth, weak token validation, no mutual TLS between services. |
| **Tampering** | Can data be modified in transit or at rest? Missing input validation, lack of integrity checks, mutable shared state without access control. |
| **Repudiation** | Can actions be denied after the fact? Missing audit logs, no request signing, unauthenticated write endpoints. |
| **Information Disclosure** | Can sensitive data leak? Overly verbose error messages, missing field-level access control, unencrypted storage, stack traces in responses. |
| **Denial of Service** | Can the system be made unavailable? No rate limiting, unbounded queries, missing pagination, synchronous blocking calls. |
| **Elevation of Privilege** | Can a lower-trust actor gain higher-trust access? Missing role checks, IDOR vulnerabilities, unsafe deserialization, mass assignment. |

## Output format

Respond inline — do NOT write a file unless the user passes `--save`.

### Threat Model: `{target}`

**System Summary**

2–3 sentences describing the system as understood, including key components, trust boundaries, and the principal actors (users, services, admins). If assumptions were made, list them here.

**Trust Boundary Diagram**

```
[Actor / External System] --> [Trust Boundary] --> [Component] --> [Data Store]
```

Use ASCII or Mermaid `graph TD` to show actors, components, trust boundaries, and data stores. Mark each trust boundary with `~~`.

**STRIDE Findings**

Use this format for each finding:

> **[LIKELIHOOD/IMPACT] STRIDE-Category — Short title**
> Description of the threat and the attack scenario.
> *Mitigation:* Concrete, actionable fix — library, pattern, or configuration change.

Group findings by STRIDE category. Within each category, order by impact descending.

**Abuse Cases**

Bullet list of realistic attacker scenarios end-to-end:
- **{Scenario name}**: Actor → attack vector → exploited weakness → impact

Include at least one insider threat and one external attacker scenario.

**Attack Surface Summary**

| Entry Point | Auth? | Rate Limited? | Input Validated? | Risk |
|-------------|-------|---------------|-----------------|------|
| `METHOD /path` or component | yes/no | yes/no | yes/no | Low/Medium/High/Critical |

**Prioritised Mitigations**

Ordered list — highest impact first. Each item should be actionable in a single PR or config change:

1. **{Mitigation title}** — why it matters, what to change.

**What looks good**

Brief bullet list of security controls already in place. Not filler — only include controls that are genuinely present and effective.

## Gotchas

- Do not invent threats that have no plausible attack path for this system. Rate likelihood honestly.
- Distinguish between theoretical and exploitable — a missing audit log is Repudiation, but note whether the endpoint is authenticated before calling it Critical.
- For file targets, read the auth middleware and validation layers before concluding they are absent — they may be applied at a higher level.
- If the system uses a framework with built-in protections (Django CSRF, Rails strong parameters, parameterized queries via ORM), credit these in "What looks good" and note what they cover.
- STRIDE is a starting point, not exhaustive. For payment systems or PII-heavy targets, call out that OWASP ASVS or PCI-DSS controls should also be reviewed separately.
