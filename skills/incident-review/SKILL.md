---
name: incident-review
description: Produce a blameless postmortem and RCA for an incident — structured timeline, proximate and root cause analysis using 5 Whys, contributing factors, and actionable CAPAs with owners and dates.
compatibility: Accepts a markdown timeline file, a raw description, or a directory of incident notes. No code access required.
allowed-tools: Read Glob Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Produce a structured, blameless postmortem for the given incident.

## Determine the target

Accept any of:
- A markdown file with an existing timeline: `outage timeline.md`, `incidents/2026-05-09.md`
- A directory of incident notes, logs, or runbook entries: `incidents/api-outage/`
- A raw description inline: `"API was down 14:00–16:30 UTC, cause unknown"`

If a file or directory is given, read all relevant content before proceeding. If multiple files exist, read them in chronological order.

If only a description is given, derive the timeline from the description and flag any gaps that the team should fill in before finalizing the postmortem.

## What to extract

Before writing the postmortem, identify the following from the input:

1. **Incident window** — start time, detection time, mitigation time, resolution time (in UTC). Note which of these are unknown and must be confirmed.

2. **Customer impact** — what was affected, how many users or systems, and for how long. Distinguish between degradation and full outage.

3. **Timeline events** — every significant event in chronological order: alerts fired, humans notified, actions taken, outcomes observed.

4. **Causal chain** — work backwards from the symptom using 5 Whys:
   - Why did the symptom occur? → proximate cause
   - Why was the proximate cause possible? → intermediate cause
   - Why was the intermediate cause possible? → ... continue until a systemic factor is reached
   - The root cause is the deepest systemic factor the team can actually fix

5. **Contributing factors** — conditions that worsened impact or delayed detection/resolution but were not the root cause. Common examples: missing alerts, unclear on-call runbook, insufficient canary coverage, inadequate load testing.

6. **What went well** — actions that limited impact, sped up detection, or made resolution easier. These are as important as the failures.

## Output format

By default, write the postmortem to a file. Infer the output path from any existing incident directory structure. If none exists, default to `docs/incidents/YYYY-MM-DD-{slug}.md`. If the user passes `--inline`, respond inline instead.

After writing the file, print the file path and a one-paragraph executive summary suitable for a status page or Slack message.

### Postmortem content

```markdown
# Incident Review: {Title}

**Date:** {YYYY-MM-DD}
**Severity:** {SEV1 / SEV2 / SEV3 — or equivalent scale if specified}
**Status:** {Draft / In Review / Finalized}
**Author:** {if known}
**Reviewers:** {if known}

---

## Executive Summary

{2–3 sentences: what happened, customer impact, and the root cause in plain language. Suitable for sharing with non-technical stakeholders.}

---

## Impact

| Metric | Value |
|--------|-------|
| Time to detect | {duration or "unknown"} |
| Time to acknowledge | {duration or "unknown"} |
| Time to mitigate | {duration or "unknown"} |
| Time to resolve | {duration or "unknown"} |
| Customer impact duration | {duration} |
| Affected users / systems | {count or description} |
| Nature of impact | {full outage / degraded / data loss / etc.} |

---

## Timeline

All times in UTC.

| Time | Event | Who |
|------|-------|-----|
| HH:MM | {What happened} | {Person or system} |

Mark the following events explicitly if present:
- 🔴 **Incident start** — when the failure began
- 📢 **First alert** — when monitoring first fired
- 👤 **First human aware** — when a person first knew
- 🛠️ **Mitigation** — when customer impact stopped
- ✅ **Resolution** — when the system was fully restored

Flag any gaps in the timeline where events are unknown or approximate.

---

## Root Cause Analysis

### Proximate Cause

{The immediate trigger — the specific action or failure that directly caused the incident.}

### 5 Whys

1. **Why did {symptom} occur?** → {answer}
2. **Why did {answer from 1} happen?** → {answer}
3. **Why did {answer from 2} happen?** → {answer}
4. **Why did {answer from 3} happen?** → {answer}
5. **Why did {answer from 4} happen?** → {root cause}

### Root Cause

{The deepest systemic factor uncovered by the 5 Whys — stated as a system or process failure, not a person. Example: "No automated rollback was configured for failed health checks after deployment."}

---

## Contributing Factors

Conditions that worsened impact or delayed detection/resolution but were not the root cause:

- {Factor 1 — what it was and how it contributed}
- {Factor 2}

---

## What Went Well

Actions that limited impact, accelerated detection, or made resolution easier:

- {Positive 1}
- {Positive 2}

---

## Corrective and Preventive Actions (CAPAs)

Each action must be specific, assigned to an owner, and have a target date. Vague actions ("improve monitoring") are not acceptable — break them down until they are a concrete, completable task.

| # | Action | Type | Owner | Target date | Status |
|---|--------|------|-------|-------------|--------|
| 1 | {Specific action} | Corrective / Preventive | {Name or team} | {YYYY-MM-DD} | Open |

**Action types:**
- **Corrective** — fixes the specific failure that caused this incident
- **Preventive** — reduces the likelihood or impact of similar incidents in future

---

## Lessons Learned

{2–3 sentences synthesizing the most important takeaways — what this incident revealed about the system, the process, or the team's practices.}
```

## Gotchas

- This is a blameless postmortem. Root causes must be systemic — a process, a tool, a missing safeguard, or a gap in knowledge — never a person. If the input names individuals as the cause, reframe it as a system failure that made the error possible.
- Proximate cause and root cause are not the same. A deploy being the trigger is a proximate cause. The absence of a canary or rollback mechanism is a root cause.
- CAPAs must be specific enough to close. "Add alerting" is not a CAPA. "Add a p99 latency alert on the payments service with a 500ms threshold, owned by the payments team, by 2026-05-30" is a CAPA.
- Flag unknown timeline gaps explicitly rather than inventing timestamps. An honest postmortem with gaps is more useful than a confident one with fabricated data.
- Time to detect is often the most revealing metric — a long detection time points to observability gaps regardless of what caused the incident.
- If the 5 Whys reaches "human error" as a stopping point, go one level deeper: why was the system designed in a way that made the human error possible or impactful?
- This skill pairs naturally with `/generate-runbook` (runbook gaps exposed by the incident should be addressed before the next on-call rotation), `/platform-readiness` (CAPAs often map directly to readiness gaps — observability, rollback, alerting), `/debug-issue` (when the root cause is still unclear after the timeline is assembled, use debug-issue to narrow to a specific code path), `/perf-investigate` (for performance incidents, use perf-investigate to profile the bottleneck after the timeline establishes when it began), and `/summarise-pr` (summarise recently merged PRs that fall within the incident window to identify contributing changes).
