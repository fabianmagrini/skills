---
name: platform-readiness
description: Evaluate the production readiness of a service or platform across observability, security, CI/CD, scalability, and SLOs. Produces a RAG-scored checklist, findings with evidence, and a prioritised remediation list.
compatibility: Requires Read, Glob, Grep for local codebases. Accepts a service name or technology description without file access.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-09
---

Evaluate the production readiness of the target service or platform and produce a scored assessment with prioritised remediation.

## Determine the target

Accept any of:
- A service or component name: `BFF`, `payments-service`, `auth-gateway`
- A technology description: `Kubernetes service`, `Lambda function`, `Next.js app`
- A local path: `services/api/`, `k8s/`, `infra/`
- A combination: `services/checkout — Kubernetes deployment`

If a local path is given, read the relevant source, config, and infrastructure files before assessing. Every finding must cite specific evidence — a file, a missing file, or a specific pattern. Do not make generic recommendations that are not grounded in what the code or config actually shows.

If only a name or description is given, derive what can be inferred, flag each item as `Not assessed — no local files provided`, and note what files the team should review to complete the assessment.

## Discovery steps

Work through each pillar in order, reading relevant files before scoring.

### 1. Observability

- **Health endpoints** — Grep for `/health`, `/readiness`, `/liveness`, `/ping`. Check that liveness and readiness probes are distinct (liveness restarts the pod; readiness gates traffic).
- **Metrics** — Grep for `prometheus`, `prom-client`, `statsd`, `micrometer`, `opentelemetry`. Check that a metrics endpoint is exported and that key business and technical metrics are instrumented (request rate, error rate, latency).
- **Distributed tracing** — Grep for `opentelemetry`, `jaeger`, `zipkin`, `datadog`, `@opentelemetry/sdk`. Check that trace context is propagated across service boundaries.
- **Structured logging** — Grep for `pino`, `winston`, `structlog`, `zap`, `logrus`, `slog`. Check that logs include trace IDs, request IDs, and are in JSON format. Grep for `console.log` or `print(` used in production paths — unstructured logging is a gap.
- **Alerting** — Glob for alert rule files (`**/alerts/*.yaml`, `**/rules/*.yaml`, `**/*alert*.yaml`). Check that alerts exist for the golden signals: error rate, latency, saturation, and traffic.

### 2. Security

- **Authentication enforcement** — Grep for auth middleware application at the route level. Check that no routes are unauthenticated that should not be. Note: deep security analysis should use `/threat-model`.
- **Secrets management** — Grep for hardcoded secrets (`password =`, `secret =`, `api_key =`, `API_KEY`). Check for use of a secrets manager (`vault`, `aws-secretsmanager`, `k8s secret`, `doppler`).
- **TLS** — Check that external endpoints are served over HTTPS. Look for TLS configuration in ingress or reverse proxy config.
- **Dependency vulnerabilities** — Check for a lockfile (`package-lock.json`, `yarn.lock`, `go.sum`, `Pipfile.lock`). Look for a dependency scanning step in the CI pipeline (`npm audit`, `snyk`, `trivy`, `dependabot`).
- **Network policy** — For Kubernetes targets, glob for `NetworkPolicy` manifests. Absence means all pods can communicate with all other pods.

### 3. CI/CD

- **Pipeline definition** — Glob for pipeline files (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`, `buildkite.yml`). Check that it exists and runs on every PR.
- **Automated tests** — Check the pipeline for test steps. Distinguish unit, integration, and e2e coverage. A pipeline without tests is not a CI pipeline.
- **Deployment strategy** — Look for rolling update, canary, or blue/green configuration. A big-bang `Recreate` strategy with no traffic shifting is a high-risk gap.
- **Rollback mechanism** — Check for a defined rollback path: feature flags, deployment revision history (`kubectl rollout undo`), or a documented runbook. "Redeploy the previous image" only counts if it is documented and tested.
- **Environment parity** — Check whether staging/preview environments exist and whether they are deployed with the same pipeline as production.

### 4. Scalability

- **Resource limits and requests** — For Kubernetes targets, check that every container has `resources.requests` and `resources.limits` set. Missing limits means a noisy neighbour can consume all node resources.
- **Horizontal autoscaling** — Glob for `HorizontalPodAutoscaler` manifests or equivalent (`aws autoscaling`, `cloud run min/max instances`). Check that scale-out is automated, not manual.
- **Statelessness** — Check whether the service stores session state in memory or on local disk. Stateful services cannot scale horizontally without sticky sessions or session externalisation.
- **Database connection pooling** — Grep for connection pool configuration (`pgBouncer`, `pool_size`, `max_connections`, `connectionLimit`). A service that opens one connection per request will exhaust the database at scale.
- **Pagination** — Grep for list endpoints without `LIMIT` or pagination parameters. Unbounded list queries are a latency and memory time bomb under load.
- **Graceful shutdown** — Grep for `SIGTERM` handling, `preStop` hooks, or drain logic. Without graceful shutdown, in-flight requests are dropped on every deploy.

### 5. SLOs

- **Defined SLIs** — Check whether the service has documented SLIs (what is measured: availability, latency, error rate). SLIs without a specific query or metric definition are not actionable.
- **SLO targets** — Check whether numeric targets are defined (e.g. 99.9% availability, p99 < 200ms). A qualitative goal ("high availability") is not an SLO.
- **Error budget** — Check whether an error budget is calculated and tracked (1 - SLO target × window). Without a budget, there is no basis for release decisions.
- **Burn rate alerting** — Check for alerts based on error budget burn rate (e.g. multiwindow burn rate alerts), not just raw threshold alerts. Threshold alerts miss slow burns; burn rate alerts catch them.
- **Error budget policy** — Check whether there is a documented policy for what happens when the error budget is exhausted (freeze releases, prioritise reliability work). Without a policy, the SLO has no teeth.

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/readiness/{kebab-case-service}.md`.

### Platform Readiness: `{target}`

**Summary**

| Pillar | Status | Score |
|--------|--------|-------|
| Observability | 🟢 Ready / 🟡 Partial / 🔴 Not ready | {n}/{total} checks passed |
| Security | 🟢 / 🟡 / 🔴 | {n}/{total} |
| CI/CD | 🟢 / 🟡 / 🔴 | {n}/{total} |
| Scalability | 🟢 / 🟡 / 🔴 | {n}/{total} |
| SLOs | 🟢 / 🟡 / 🔴 | {n}/{total} |
| **Overall** | 🟢 / 🟡 / 🔴 | {n}/{total} |

**Scoring:** 🟢 Ready = ≥80% checks passed with no CRITICAL gaps. 🟡 Partial = 50–79% or has MAJOR gaps. 🔴 Not ready = <50% or has CRITICAL gaps.

**Findings**

Group by pillar. For each finding:

> **[CRITICAL / MAJOR / MINOR] Pillar — Short title**
> What is missing or misconfigured, with a specific file or pattern as evidence.
> *Remediation:* Concrete action — what to add, change, or configure.

**CRITICAL** = must fix before production traffic. **MAJOR** = should fix before launch. **MINOR** = worth improving but not a blocker.

**What is in place**

Bullet list of checks that passed, with evidence. This is not filler — it anchors the assessment and prevents re-reviewing things that are already done.

**Prioritised Remediation**

Ordered by severity and impact. Each item should be completable in a single PR or config change:

1. **{Action}** — pillar, specific change, why it matters.

**Limitations of this assessment**

Note any pillars or checks that could not be assessed due to missing files, external systems, or scope. Flag what a human reviewer should check manually to complete the picture.

## Gotchas

- Every finding must cite evidence: a file path, a missing file, or a specific grep pattern that was absent. Generic recommendations without evidence are not findings.
- Do not conflate liveness and readiness probes. A service with only a liveness probe will send traffic to a pod that is not ready — this is a MAJOR gap, not a minor one.
- SLO readiness requires all five elements: SLI definition, numeric target, error budget calculation, burn rate alerting, and an error budget policy. A target without burn rate alerting is 🟡 Partial, not 🟢 Ready.
- For security gaps beyond secrets and auth enforcement, note that `/threat-model` provides deeper STRIDE analysis and do not attempt to replicate it here.
- Resource limits without requests are incomplete — Kubernetes uses requests for scheduling. Both must be set.
- A rollback mechanism that exists only in someone's head is not a rollback mechanism. It must be documented and ideally tested.
- If no CI/CD pipeline file is found, this is CRITICAL — not a gap to note politely. A service with no pipeline cannot safely ship changes.
- This skill pairs naturally with `/generate-runbook` (runbook coverage is a CI/CD pillar requirement), `/threat-model` (deeper analysis of the security pillar), `/test-strategy` (test coverage gaps found in the CI/CD pillar), and `/incident-review` (readiness gaps often surface as CAPA items after an incident).
