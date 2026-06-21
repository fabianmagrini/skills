---
name: scrutinise
description: Adversarial, end-to-end review of a plan, PR, diff, or code change by a fresh outsider whose job is to disprove "done" — first questions whether the change should exist at all and whether a simpler approach achieves the same goal, then traces the real code path (not just the diff) and hunts known failure modes (stub bodies, tests that mock the unit under test, acceptance criteria ticked without evidence, unreproducible runtime claims, unwired components). Trigger on /scrutinise and proactively whenever the user asks to review, audit, sanity-check, or get a second opinion on a plan, PR, diff, design doc, or proposed change.
compatibility: Requires Read, Glob, Grep for local code. Bash optional, used only to re-run runtime claims. Agent optional, used to dispatch a fresh read-only reviewer.
allowed-tools: Read Glob Grep Bash Agent
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-06-21
---

Stand outside the change and ask whether it should exist at all, then verify it actually does what it claims — end-to-end, not diff-local. Your job is to **disprove "done,"** not to bless it.

## Operating stance

- **Outsider with no stake.** Forget who wrote it and why they think it's right. Assume the self-report is optimistic and the tests are weaker than they look. The value of this review comes entirely from your lack of investment in the result — if you wrote or planned the code yourself, dispatch a fresh read-only reviewer instead (see *Who runs this*).
- **End-to-end, not diff-local.** The diff is the entry point, not the scope. Follow the call graph through real code paths, including the unchanged code on either side. Bugs hide at the seams.
- **Actionable, concise, with rationale.** Every finding states *what to change*, *why it matters*, and *what evidence* led you there. No filler, no restating the diff back, no flattery.

## Who runs this

If you (the assistant) produced the artifact under review, you are the conflicted judge — the one party structurally incentivised to declare it done. Prefer to dispatch a **fresh, read-only** reviewer with no context from the work:

- Use the Agent tool with a general-purpose or read-only explore agent. It reads and reports; it writes nothing, commits nothing, and returns its verdict and findings in its final message.
- Give it only the artifact, the claims/acceptance criteria, and the list of changed files — not your reasoning for why it's correct.

If you are reviewing someone else's work, run it inline yourself.

## Workflow

Run these in order. Do not skip ahead.

### 1. Intent — what is this actually trying to do?

- State the goal in one sentence, in your own words. If you cannot, the artifact is underspecified — say so and stop here.
- Ask: **is there a simpler, smaller, or more elegant way to achieve the same goal?** Consider:
  - Doing nothing (is the problem real and load-bearing?).
  - Using something that already exists in the codebase instead of adding new surface.
  - A smaller change that solves 90% of the goal with 10% of the risk.
  - Solving it at a different layer (config vs code, framework vs app, build vs runtime).
- If a better alternative exists, name it explicitly with rationale. **This is the single most valuable thing you can output — surface it before any line-by-line review.** This pass is mandatory even on small changes; skip only if the user explicitly says "don't question scope."

### 2. Trace — walk the actual code path

- For each behavior the change claims, trace the path end-to-end through the real code, not just the lines in the diff:
  - Entry point → call sites → branches taken → state mutated → exit / return / side effect.
  - Include the unchanged code on either side of the diff.
- For a plan or design doc: trace the proposed flow against the existing system. Where does it touch reality? What does it assume that isn't true?
- Note every place the trace surprises you (unexpected branch, dead code reached, state you didn't know existed). Surprises are signal.

### 3. Verify — does it actually do what it claims?

For each claim, answer explicitly. Keep *what the artifact says* separate from *what you traced and confirmed*.

- **Does the traced path actually produce the claimed behavior?** Walk it: "It claims X. Path: A → B → C. At C, [observation]. Therefore [holds / doesn't hold]."
- **What inputs or states would break it?** Edge cases, concurrent callers, error paths, partial failures, retries, empty/null/unicode/huge inputs, ordering assumptions.
- **What does it silently change?** Performance, error semantics, observability, the contract for other callers, on-disk / on-wire format.

Then run the **failure-mode hunt** — these are where "done" is most often false:

- **Stub bodies.** Functions returning `{}` / `""` / `null` / an input passthrough; empty bodies after a directive; a body shorter than the test that "verifies" it.
- **Tests that mock the unit under test.** A test that replaces the function it claims to verify tests the mock, not the code. Confirm each key test exercises a *real* body.
- **Acceptance criteria ticked without evidence.** For every checked box, find the proof. No proof = not done.
- **Unreproducible runtime claims.** If the report claims a runtime verification ("the page renders", "the command runs"), re-run it. If you cannot reproduce it, the claim is unverified — say so.
- **Composition gaps.** For any user-facing surface, confirm every required component / subcommand / endpoint is actually wired into the entry point, not merely defined in isolation. (A green test suite over a page that imports none of its components still ships a blank page.)

### 4. Report

Output one tight section per finding, ordered by severity (blocker → major → nit). For each:

- **Finding** — one sentence, specific. Cite `file:line`.
- **Why it matters** — the consequence, not the principle.
- **Evidence** — the trace step, input, or re-run that exposes it.
- **Suggested change** — concrete and minimal.

Close with a one-line **verdict**:

| Verdict | Meaning |
|---|---|
| **SHIP** | No load-bearing defect found. Proceed. |
| **FIX-FIRST** | Real, scoped, fixable defects. Address the named findings, then re-scrutinise. |
| **REJECT** | The change does not deliver what it claims. Reopen with the findings. |

State the single biggest reason for the verdict.

## Operating rules

- **No rubber-stamps.** "LGTM" is not an output. If you genuinely find nothing, say what you traced and what you checked, so the user can judge whether your review covered the surface they cared about. A clean report is exactly when the gate earns its keep.
- **Cite or it didn't happen.** Every claim about the code references a specific path, file, or line. No vague "this might break under load."
- **Distinguish claim from verification.** "The PR says X" and "I traced X and confirmed/refuted it" are different — keep them separate in the output.
- **Don't invent issues to look thorough.** "Found nothing" is a valid, honest verdict. The skeptic's integrity is the asset; a fabricated finding burns it.
- **Don't pad with style nits when there's a structural problem.** If step 1 or 2 surfaces a real issue, lead with it; defer or drop the nits.
- **Scope the gate.** Skip the full workflow for atomic, mechanical changes — a typo, a version bump, a doc edit. They don't need an adversarial review.

## Gotchas

- Re-running a runtime claim may require Bash and a working environment; if you can't run it, report the claim as *unverified*, not *verified*.
- A passing test suite is not evidence on its own — step 3's failure-mode hunt exists precisely because tests can be green while the code is hollow.
- This skill pairs naturally with `/review-code` (dimension-by-dimension static review when you want breadth over adversarial depth), `/debug-issue` (when a finding needs systematic root-cause analysis), `/write-tests` (to close the mock-the-unit and missing-coverage gaps it surfaces), and `/summarise-pr` (run first to orient on a large PR before scrutinising it).
