---
name: skill-generator
description: Generate a new SKILL.md from a description of a repeated workflow. Elicits trigger conditions, discovery steps, output format, and gotchas before writing — producing a schema-compliant first draft ready for review.
compatibility: Requires Read to load SKILL-SCHEMA.md and reference skills. Requires Write to create the new skill file.
allowed-tools: Read Glob Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Generate a new skill from a workflow description. Do not write anything until the elicitation steps are complete.

## Step 1: Load the quality bar

Before generating anything, read the following to internalise the schema and format conventions:

1. Read `SKILL-SCHEMA.md` — understand all required and optional frontmatter fields, allowed-tools options, and versioning policy.
2. Glob for `skills/*/SKILL.md` and read 2–3 of the most structurally complete skills as format references. Prefer skills that have: a Determine the target section, numbered discovery steps, a detailed output format, and a Gotchas section.

Do not proceed to elicitation until both reads are complete.

## Step 2: Elicit the workflow

A one-line description is not enough to produce a good skill. Work through the following questions, either by asking the user interactively or by extracting answers from a detailed description they have already provided.

For each question, if the answer is not in the user's input, ask before proceeding. Do not invent answers.

**Trigger and invocation**
- What is the skill's name (kebab-case, becomes the slash command)?
- In one sentence: what does this skill do and when should it be invoked?
- What are 2–3 realistic example invocations with arguments?

**Input**
- What does the user pass in? (file path, URL, natural language description, combination)
- Are there multiple valid input forms? What does each one mean?
- What local files should the skill read before acting? (source code, config, schemas, existing docs)

**Discovery**
- What does the skill need to find or derive before producing output?
- What Glob patterns or Grep terms locate the relevant files?
- What should it do if the expected files are not found?

**Output**
- What does the output look like? (tables, diagrams, bullet lists, prose, structured sections)
- Where does it go? (inline by default, or write to a file — what path?)
- Is there a `--save` or `--inline` flag pattern?
- What is the format for individual findings or entries?

**Boundaries and gotchas**
- What should this skill never do? (common failure modes to guard against)
- What inputs or situations require special handling?
- What assumptions does the skill make that the user should know about?
- What is out of scope — things the user might expect but the skill deliberately does not cover?

**Tools**
- Which tools does the skill actually need? Be as restrictive as possible.
- Available: `Read`, `Glob`, `Grep`, `Write`, `Edit`, `Bash`, `WebFetch`, `WebSearch`, `Agent`

## Step 3: Draft the skill

Once all elicitation questions are answered, generate the `SKILL.md` using this structure:

```markdown
---
name: {name}
description: {one sentence — what it does and when to invoke it}
compatibility: {prerequisites or limitations, if any}
allowed-tools: {space-separated list — only what the skill actually needs}
metadata:
  author: {github username if known, else omit}
  version: "1.0"
  last-updated: {today's date YYYY-MM-DD}
---

{One sentence summary of what the skill does.}

## Determine the target

{Enumerate all valid input forms. For each, describe what it means and how it is handled. Include a note on what to do when input is ambiguous or missing.}

## Discovery steps

{Numbered steps — what to read and find before producing output. Each step should include specific Glob patterns or Grep terms. Include what to do when expected files are not found.}

## Output format

{Describe the output structure in detail. Include section headings, table formats, and example snippets. State where output goes by default and any flag that changes the destination.}

## Gotchas

{Bullet list — one per failure mode. Each gotcha should be specific enough to prevent a real mistake, not generic advice.}
```

## Step 4: Evaluate the draft

Before writing the file, review the draft against this checklist. Fix any failures before proceeding:

- [ ] `name` matches the intended slash command in kebab-case
- [ ] `description` is one sentence, action-oriented, and specific enough to distinguish this skill from similar ones
- [ ] `allowed-tools` is as restrictive as possible — no tools included speculatively
- [ ] `Determine the target` covers all valid input forms and handles ambiguous input
- [ ] `Discovery steps` are numbered, include specific Glob/Grep patterns, and handle missing files
- [ ] `Output format` specifies every section, table, and destination — a reader could implement it without guessing
- [ ] `Gotchas` has at least three entries, each specific to this skill's failure modes
- [ ] The skill does not tell the agent to "help the user" or "assist with" — it gives precise instructions

If any item fails, fix it in the draft before writing.

## Step 5: Write and register

1. Write the skill to `skills/{name}/SKILL.md`. Create the directory if it does not exist.

2. Print the following for the user to add to `README.md` and `skills.json`:

**README row** (add to the appropriate category table):
```
| [{name}](skills/{name}/SKILL.md) | {description} |
```

**skills.json entry**:
```json
{
  "name": "{name}",
  "description": "{description}",
  "path": "skills/{name}/SKILL.md",
  "category": "{category}",
  "allowed-tools": [{tools as JSON array}],
  "version": "1.0",
  "author": "{author}"
}
```

3. Tell the user:
   - The file path written
   - That this is a **first draft** — test it against at least two real inputs before committing
   - Which sections are most likely to need refinement based on the elicitation (flag any questions that were answered with uncertainty)

## Gotchas

- Do not write the skill until all elicitation questions are answered. A skill generated from a vague description will produce vague output — this makes more work, not less.
- Do not invent discovery steps. If the user has not described what files the skill should read, ask. A skill without discovery steps is a prompt, not a skill.
- Do not include tools speculatively. `Agent` and `Bash` in particular should only be included if the elicitation explicitly requires subagent delegation or shell execution.
- The generated skill is a first draft. Flag this clearly — do not present it as production-ready without the user testing it against real inputs.
- If the workflow the user describes is too broad (e.g. "help with code quality"), narrow it to a single, specific output before generating. A skill that tries to do everything does nothing well.
- Do not generate a skill that duplicates an existing one. Run `Glob skills/*/SKILL.md` and read descriptions to check for overlap before writing. If overlap exists, suggest extending the existing skill instead.
- This skill pairs naturally with `/context-engineering` (register the new skill in the agent context file after generating it) and `/agent-loop-design` (new skills often become the discrete work units dispatched by an autonomous loop).
