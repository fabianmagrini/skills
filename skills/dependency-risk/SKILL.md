---
name: dependency-risk
description: Analyze package, vendor, or architecture dependency risk — covering supply chain exposure, license compatibility, vendor lock-in, coupling depth, and sustainability — and produce a risk table with prioritised remediation.
compatibility: Requires Read, Glob, Grep for local codebases. Cannot run live CVE scanners — recommends appropriate tooling for vulnerability data.
allowed-tools: Read Glob Grep
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Analyze dependency risk and produce a prioritised risk assessment with remediation recommendations.

## Determine the target

Accept any of:
- A dependency manifest: `package.json`, `go.mod`, `requirements.txt`, `Gemfile`, `pom.xml`, `Cargo.toml`
- A vendor or service name: `auth0`, `stripe`, `datadog`, `twilio`
- A local path: `services/payments/` — scans all manifests and vendor references found
- A combination: `package.json + auth0` — analyzes both package dependencies and the auth0 vendor relationship

Automatically detect the mode from the input:
- **Package mode** — input is a manifest file or contains package names
- **Vendor mode** — input is a service/vendor name with no manifest file
- **Combined mode** — multiple targets or a directory containing both

## Package Mode: Dependency File Analysis

Read the manifest file and any associated lockfile (`package-lock.json`, `yarn.lock`, `go.sum`, `Pipfile.lock`, `Gemfile.lock`). The lockfile is authoritative — the manifest shows intent, the lockfile shows what is actually installed.

### What to assess

**1. Version pinning**

Read the manifest and classify each dependency's pinning strategy:
- **Exact pin** (`"1.2.3"`, `==1.2.3`) — safest; reproducible builds
- **Patch-floating** (`"~1.2.0"`, `~=1.2.3`) — low risk; patch updates only
- **Minor-floating** (`"^1.2.0"`, `>=1.2,<2`) — moderate risk; minor updates may introduce breaking changes or malicious patches
- **Unconstrained** (`"*"`, `>=1.0`, `latest`) — high risk; any version including malicious ones

Flag every unconstrained or broadly floating direct dependency.

**2. Abandonment signals**

Identify packages likely to be abandoned or unmaintained by looking for:
- No lockfile entry update in over 12 months (compare lockfile timestamps where available)
- Very low version numbers still in use (e.g. `0.x`) for a package that has reached `1.x` or higher
- Known deprecated packages by name — common examples: `request` (Node.js), `moment` (replaced by `date-fns`/`dayjs`), `left-pad`, `node-uuid` (replaced by `uuid`), `istanbul` (replaced by `nyc`/`c8`), `tslint` (replaced by `eslint`)

**3. License risk**

Grep for `license` fields in the manifest. Flag:
- **GPL / AGPL** in a proprietary or commercial codebase — copyleft may require source disclosure
- **LGPL** — permissible for dynamic linking but requires care with static linking
- **Unknown / missing license** — treat as high risk; cannot be used safely without clarification
- **Multiple licenses** — flag for legal review

**4. Supply chain structure**

- Count direct vs. transitive dependencies (lockfile line count is a proxy)
- Identify single points of failure: widely imported packages deep in the tree where a compromise would affect many dependents
- Flag dev dependencies that appear in production build output (e.g. `devDependencies` in a bundled artifact)

**5. Existing scanning coverage**

Read the CI/CD pipeline to check whether a dependency scanning step exists:
- Glob for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`
- Grep for `npm audit`, `snyk`, `trivy`, `dependabot`, `renovate`, `pip-audit`, `govulncheck`, `cargo audit`

If no scanning step exists, this is a CRITICAL structural gap regardless of the individual package risks.

## Vendor Mode: Service Dependency Analysis

Read the codebase to assess how deeply the vendor is coupled into the system.

### What to assess

**1. Coupling depth**

Grep for the vendor's SDK, client library, or API identifiers:
- Import statements: `import Auth0`, `from 'auth0'`, `require('stripe')`, `import datadog`
- Direct API calls: vendor-specific endpoint patterns, client instantiation
- Configuration references: env var names referencing the vendor (`AUTH0_DOMAIN`, `STRIPE_SECRET_KEY`)

Count the number of files that directly reference the vendor. More than 10–15 files without an abstraction layer is a high coupling risk.

**2. Abstraction layer**

Check whether the codebase wraps the vendor behind an interface:
- Grep for adapter, gateway, or provider patterns (`AuthProvider`, `PaymentGateway`, `NotificationService`)
- Check whether the vendor SDK is imported only in one or a small number of files (the adapter) rather than scattered across the codebase

Absence of an abstraction layer means every callsite must change if the vendor is replaced.

**3. Data portability**

Assess whether data owned by the vendor can be recovered if the relationship ends:
- Does the vendor store the source of truth (user records, payment history, identity)?
- Is there a documented export mechanism?
- Is there a local copy or cache of critical data, or is the system entirely dependent on the vendor's API being available?

**4. Single point of failure**

Assess what happens if the vendor has an outage:
- Is there a fallback or degraded mode?
- Is the vendor on the critical path for authentication, payments, or core functionality?
- Is there a circuit breaker or timeout configured for vendor API calls?

**5. Commercial and regulatory risk**

From configuration files and environment variable names, assess:
- Is the team on a free or trial tier? (common indicator: `_TEST_` or `_SANDBOX_` in env var names)
- Does the vendor store PII? If so, what jurisdiction and compliance obligations apply?
- Is there a contractual SLA with the vendor?

**6. Migration cost estimate**

Based on coupling depth and abstraction layer assessment, estimate the migration cost:
- **Low** — abstraction layer exists, vendor is isolated to one module, data is portable
- **Medium** — some coupling exists, data is partially portable, migration would take weeks
- **High** — deep coupling across the codebase, vendor owns critical data, migration would take months

## Output format

Respond inline by default. If the user passes `--save`, write to `docs/dependency-risk/{slug}.md`.

### Dependency Risk: `{target}`

**Risk Summary**

| Dependency / Vendor | Risk Type | Severity | Evidence |
|--------------------|-----------|----------|----------|
| {name} | Supply chain / License / Lock-in / Abandonment / Coupling | CRITICAL / HIGH / MEDIUM / LOW | {file:line or pattern} |

**Package Findings** *(if package mode)*

Group by risk type. For each finding:

> **[SEVERITY] Risk type — Short title**
> What the risk is and the specific evidence (package name, version, file).
> *Remediation:* Concrete action — pin the version, replace the package, add a scanning step.

**Vendor Findings** *(if vendor mode)*

> **[SEVERITY] Risk type — Short title**
> What the risk is and the specific evidence (file count, missing abstraction, data ownership).
> *Remediation:* Concrete action — introduce an adapter, add a circuit breaker, document an export process.

**What is managed well**

Bullet list of risk controls already in place — exact pins, scanning coverage, existing abstraction layers, documented fallbacks. Not filler — only include controls that are genuinely present.

**Prioritised Remediation**

Ordered by risk reduction value:

1. **{Action}** — risk type, specific change, why it matters.

**Recommended Scanning Tools**

This assessment is based on static file analysis. For authoritative vulnerability data, run the appropriate tool for your stack:

| Stack | Tool | Command |
|-------|------|---------|
| Node.js | npm audit | `npm audit --audit-level=high` |
| Node.js | Snyk | `snyk test` |
| Python | pip-audit | `pip-audit` |
| Go | govulncheck | `govulncheck ./...` |
| Rust | cargo audit | `cargo audit` |
| Containers | Trivy | `trivy image {image}` |
| Multi-language | Dependabot | Enable in GitHub repository settings |

## Gotchas

- This skill performs static analysis only. It cannot query live CVE databases, check npm download counts, or verify whether a package is currently maintained. Always run a dedicated scanner for authoritative vulnerability data.
- Do not flag a package as abandoned based solely on its version number or age. Some stable, low-churn packages are intentionally not updated frequently.
- License risk depends on how the dependency is used (dynamic vs. static linking, internal vs. distributed). Flag GPL/AGPL and recommend legal review — do not make a definitive compliance ruling.
- Coupling depth is a proxy for migration cost, not a measure of whether the vendor is good or bad. A deeply coupled vendor with a strong SLA and data portability may be lower risk than a loosely coupled one with no export mechanism.
- If no lockfile exists alongside the manifest, flag this as HIGH risk — without a lockfile, builds are not reproducible and are vulnerable to dependency confusion attacks.
- A vendor abstraction layer only reduces lock-in risk if it genuinely encapsulates the vendor — a thin wrapper that leaks vendor-specific types or error codes does not count.
- This skill pairs naturally with `/threat-model` (supply chain threats from abandoned or compromised packages), `/refactor-strategy` (planning a migration away from high-risk or deeply coupled vendors), and `/security-audit` (dependency-risk covers OWASP A06 vulnerable components at the package level; security-audit covers A01–A10 at the source code level).
