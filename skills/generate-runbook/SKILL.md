---
name: generate-runbook
description: Generate or update an operational runbook for a service — covering deployment, rollback, health checks, on-call escalation, common failure modes with diagnosis steps, alert procedures, and routine maintenance.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts a service name or path.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Generate or update an operational runbook grounded in the service's actual deployment config, alerts, and dependencies.

## Determine the target

Accept any of:
- A service name: `payments-service`, `BFF`, `auth-gateway`
- A local path: `services/payments/`, `k8s/payments/`
- A combination: `services/checkout — include database migration steps`

Also accept a mode flag:
- `--update path/to/runbook.md` — update an existing runbook, checking for stale content

If no path is given, search the repo for the service by name. If the service cannot be located, state what was searched and ask for clarification.

## Discovery steps

Read the following before generating. Every runbook section must be grounded in what was actually found — do not write placeholder procedures.

### 1. Deployment configuration
- Glob for Kubernetes manifests: `**/k8s/**/*.yaml`, `**/kubernetes/**/*.yaml`, `**/deploy/**/*.yaml`
- Glob for Docker Compose: `**/docker-compose*.yml`, `**/compose*.yaml`
- Glob for infrastructure-as-code: `**/*.tf`, `**/cdk/**`, `**/pulumi/**`
- Read deployment manifests for: image name, replicas, resource limits, environment variables, volumes, config maps, secrets references

### 2. CI/CD pipeline
- Glob for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`
- Read the deployment job(s) — extract the actual deployment command, environment promotion order (dev → staging → prod), required approvals, and any smoke test steps run after deployment

### 3. Health and readiness
- Grep for health endpoint definitions (`/health`, `/readiness`, `/liveness`, `/ping`, `healthz`)
- Check Kubernetes liveness/readiness probe configuration
- Note what a healthy response looks like (status code, response body shape)

### 4. Alert rules
- Glob for alert rule files: `**/alerts/*.yaml`, `**/rules/*.yaml`, `**/*alert*.yaml`, `**/prometheus/**`
- Read alert definitions — extract: alert name, condition, severity, and any existing `runbook_url` annotation
- Each alert found becomes a required entry in the Alert Runbook section

### 5. Service dependencies
- Grep for external service calls (HTTP clients, SDK instantiation, queue consumers)
- Grep for database connection configuration
- Grep for feature flag clients (`LaunchDarkly`, `Unleash`, `Split`)
- For each dependency, note: what it does for this service and what happens if it is unavailable

### 6. Environment variables and secrets
- Read `.env.example`, `docker-compose.yml` env sections, or Kubernetes ConfigMap/Secret references
- List required environment variables — these are needed for incident diagnosis and environment setup

### 7. Database and migration tooling
- Grep for migration tooling (`flyway`, `liquibase`, `alembic`, `golang-migrate`, `prisma migrate`, `knex migrate`, `typeorm migration`)
- Read migration config or recent migration files to understand the migration pattern

### 8. Existing runbooks
- Glob for `docs/runbooks/*.md`, `runbooks/*.md`, `*.runbook.md`
- If an existing runbook is found for this service, switch to update mode and flag stale sections

## Update mode

If updating an existing runbook (`--update`):
1. Read the existing runbook in full
2. Run the full discovery steps above
3. For each section, check whether the content matches current reality:
   - Commands that no longer exist → flag as stale
   - Endpoints that have changed → flag as stale
   - Alert names that don't match current rules → flag as stale
   - Missing alerts with no runbook entry → flag as gap
4. Produce a diff-style review: **Stale**, **Gap**, or **Current** per section
5. Rewrite only the stale and gap sections — preserve accurate content

## Output format

Write to `docs/runbooks/{kebab-case-service}.md` by default. If the user passes `--inline`, respond inline instead.

```markdown
# Runbook: {Service Name}

**Owner:** {team or on-call rotation — state "unknown" if not found}
**Repository:** {path or URL}
**Last updated:** {YYYY-MM-DD}

---

## Service Overview

{2–3 sentences: what the service does, its role in the system, and its criticality (customer-facing, internal, batch).}

**Key contacts:**
- On-call: {rotation name or team}
- Escalation: {senior engineer or team lead — state "unknown" if not found}
- Slack channel: {if found in README or config}

---

## Quick Reference

| What | Where / How |
|------|------------|
| Logs | {log query or dashboard link placeholder} |
| Metrics | {metrics dashboard placeholder} |
| Traces | {tracing dashboard placeholder} |
| Deployment pipeline | {CI/CD link or pipeline name} |
| Health endpoint | `{URL or path}` |

---

## Deployment

### Pre-deployment checklist
- [ ] Confirm staging deployment succeeded and smoke tests passed
- [ ] Check for pending database migrations — run before or after deploy?
- [ ] Notify {team} if this is a breaking change

### Deploy procedure

```bash
{actual deployment command from CI/CD — e.g. `kubectl set image deployment/payments payments={image}:{tag}`}
```

### Verify deployment

```bash
{command to check rollout status — e.g. `kubectl rollout status deployment/payments`}
```

Expected: {what a successful deployment looks like — pod count, health endpoint response}

### Post-deployment smoke tests
{specific endpoints or checks to run, derived from CI/CD smoke test steps if found}

---

## Rollback

**When to roll back:** Rollback if {specific conditions — error rate spike, health check failures, customer reports}.

### Rollback procedure

```bash
{actual rollback command — e.g. `kubectl rollout undo deployment/payments`}
```

**Data considerations:** {note if the deployment included a database migration and whether rollback requires a compensating migration}

---

## Health Checks

| Check | Endpoint / Command | Expected response |
|-------|--------------------|------------------|
| Liveness | `GET {path}` | `200 OK` |
| Readiness | `GET {path}` | `200 OK` |
| {Other} | {command} | {expected} |

---

## On-Call Escalation

| Severity | Response time | Action |
|----------|--------------|--------|
| SEV1 (service down) | 15 min | Page on-call → escalate to {lead} after 30 min |
| SEV2 (degraded) | 30 min | Page on-call |
| SEV3 (minor) | Next business day | Create ticket |

---

## Common Failure Modes

For each known failure, follow this format:

### {Failure name}

**Symptoms:** {what the user or alert sees}

**Diagnosis:**
1. {Specific command or query to run first}
2. {What to look for in logs — include log query pattern}
3. {Next step depending on what is found}

**Remediation:**
- {Specific action to take}

**Escalate if:** {condition under which to escalate rather than self-resolve}

---

## Alert Runbook

One entry per alert found in alert rule files.

### Alert: `{AlertName}`

**Severity:** {critical / warning}
**Condition:** {what triggers this alert — from the alert rule}
**Meaning:** {what this alert indicates is wrong}

**Immediate actions:**
1. {First thing to check}
2. {Second thing to check}

**Resolution:** {how to resolve}
**If unresolved after {N} minutes:** escalate to {team}

---

## Dependencies

| Dependency | Purpose | Impact if unavailable | Fallback |
|-----------|---------|----------------------|---------|
| {name} | {what it does} | {degraded / total outage / no impact} | {fallback or "none"} |

---

## Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| {NAME} | {what it configures} | yes / no |

---

## Database and Migrations

**Database:** {type and connection — from config}
**Migration tool:** {tool name and command}

### Run migrations
```bash
{migration command}
```

**Before or after deploy?** {before / after — derived from pipeline order if found}

---

## Routine Maintenance

### {Task name} — {frequency}
{Step-by-step procedure for the routine task}

---

## References

- Architecture: {link to design doc or ADR if found}
- API spec: {link to OpenAPI/GraphQL spec if found}
- Incident history: {link to incident tracker if known}
```

## Gotchas

- Every diagnosis step must be specific: name the log field, the query, the command. "Check the logs" is not a diagnosis step.
- Rollback procedures must address data migration implications. A rollback that ignores a completed database migration will cause data corruption.
- Alert runbook entries must use the exact alert name from the alert rule file — do not paraphrase. Alert routing depends on the name matching.
- The Quick Reference table link placeholders must be clearly marked as placeholders — do not invent dashboard URLs.
- If the deployment command cannot be found in the CI/CD pipeline, say so and leave a `TODO` rather than guessing.
- Runbooks go stale quickly. If the discovery steps find a large delta between the runbook and the current config, recommend adding a last-updated date and scheduling a quarterly review.
- This skill pairs naturally with `/platform-readiness` (which checks whether a runbook exists as part of its CI/CD pillar), `/incident-review` (which references runbook procedures during postmortems), `/test-strategy` (smoke tests and health checks documented in the runbook should align with the test suite), and `/migrate-data` (the runbook's Database and Migrations section should reference the migration plan for any schema changes in the deployment).
