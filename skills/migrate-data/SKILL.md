---
name: migrate-data
description: Plan and scaffold a database migration — schema change or data transformation — with a rollback strategy, zero-downtime sequencing, pre/post deployment steps, and validation queries grounded in the project's actual migration tooling.
compatibility: Requires Read, Glob, Grep for local codebases. Requires a local path to discover migration tooling and existing schema.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Produce a complete, safe migration plan grounded in the project's actual schema, migration tooling, and deployment constraints.

## Determine the target

Accept any of:
- A schema change description: `add nullable phone_number column to users`, `rename orders.state to orders.status`, `drop legacy_payments table`
- A data transformation: `backfill user.full_name from first_name + last_name`, `migrate JSON config column to normalised config_items table`
- A migration file path: `db/migrations/20260510_add_phone.sql` — review and improve an existing migration
- A model or table name: `users table`, `src/models/order.ts` — discover what change is needed from context

If the change description is ambiguous (e.g. "migrate the users table"), ask for the specific before/after state before proceeding.

Also accept:
- `--zero-downtime` — explicitly flag that the migration must not lock the table or cause downtime (default assumption for production)
- `--allow-lock` — the deployment has a maintenance window; table locks are acceptable

## Discovery steps

Read the following before writing any migration code. Every script, command, and rollback step must be grounded in what was actually found.

### 1. Identify migration tooling

Grep for migration framework signatures:

- **Flyway**: `flyway.conf`, `V*.sql` files, `flyway migrate` in CI
- **Liquibase**: `liquibase.properties`, `changelog.xml`, `changelog.yaml`
- **Alembic** (Python/SQLAlchemy): `alembic.ini`, `env.py`, `versions/`
- **golang-migrate**: `*.up.sql`, `*.down.sql`, `migrate -path`
- **Prisma**: `schema.prisma`, `prisma migrate dev`, `migrations/*/migration.sql`
- **Knex**: `knexfile.js`, `knex migrate:make`, `migrations/*.js`
- **TypeORM**: `ormconfig`, `@Migration()`, `typeorm migration:create`
- **Rails ActiveRecord**: `db/migrate/*.rb`, `rails db:migrate`
- **Django**: `*/migrations/*.py`, `manage.py migrate`
- **Liquibase**: `changelog.xml`, `liquibase update`

Read the migration config file and 2–3 recent migration files to understand: naming convention, file format, rollback pattern (separate down file vs inline), and whether migrations are run before or after deploy in the CI/CD pipeline.

### 2. Read the current schema

Glob for schema definition files:
- `schema.prisma`, `schema.sql`, `db/schema.rb`, `structure.sql`
- ORM model files for the affected table: `**/models/**`, `**/entities/**`, `**/*.model.ts`, `**/*.entity.ts`

Read the current definition of the affected table(s). Understand: existing columns, types, constraints, indexes, and foreign keys. The migration must start from the actual current state, not an assumed one.

### 3. Find all code that touches the affected table

Grep for references to the affected table name, column names, and model class in:
- Service and repository files
- API handlers and controllers
- Background jobs and workers
- Seed and fixture files

For each reference, determine whether the migration will break it (column rename, type change, column removal) or require a code change to be deployed alongside the migration.

### 4. Check for existing migrations on the same table

Glob for migration files and grep for the affected table name. Read any recent migrations on the same table — a migration that conflicts with or duplicates a pending one is a production incident waiting to happen.

### 5. Read CI/CD pipeline for migration sequencing

Glob for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`. Find where migrations are run relative to the deployment step:
- **Before deploy**: new code must be backwards-compatible with the old schema during the migration window
- **After deploy**: new code is deployed first; schema must be backwards-compatible with the old code until migration completes

Note the migration command used in CI — the plan's run instructions must match it exactly.

## Migration type classification

Before writing, classify the migration:

| Type | Risk | Zero-downtime approach |
|------|------|----------------------|
| Add nullable column | Low | Safe — add column, backfill separately if needed |
| Add non-null column with default | Low | Add with default, remove default later if needed |
| Add non-null column without default | HIGH | Must backfill first, then add constraint |
| Rename column | HIGH | Expand/contract: add new, dual-write, backfill, remove old |
| Change column type | HIGH | Expand/contract or maintenance window |
| Remove column | MEDIUM | Deploy code to stop using it first, then drop |
| Add index | Low (concurrent) | `CREATE INDEX CONCURRENTLY` (Postgres) or equivalent |
| Add index | HIGH (non-concurrent) | Locks table — requires maintenance window |
| Rename/drop table | HIGH | Expand/contract across multiple releases |
| Backfill data | MEDIUM | Batch in chunks; never update all rows in one transaction |

For HIGH risk migrations, the plan must include an expand/contract strategy unless `--allow-lock` is passed.

## Output format

Write to `docs/migrations/{YYYY-MM-DD}-{kebab-description}.md` by default. If the user passes `--inline`, respond inline instead.

```markdown
# Migration Plan: {description}

**Date:** {YYYY-MM-DD}
**Risk level:** {Low / Medium / High}
**Zero-downtime:** {Yes / No — requires maintenance window}
**Migration tool:** {tool and version}
**Affected table(s):** {table names}

---

## Summary

{2–3 sentences: what is changing, why, and any backwards-compatibility constraints.}

## Before and after

**Before:**
```sql
-- or equivalent in the project's schema language
{current schema for affected table}
```

**After:**
```sql
{target schema}
```

---

## Migration script

File: `{migration file path following project naming convention}`

```sql
-- or the project's migration language (Ruby, Python, JS, etc.)
{migration up script}
```

## Rollback script

```sql
{migration down script — or "No automatic rollback: {reason}" for destructive changes}
```

**Rollback considerations:** {data implications of rolling back — especially if the migration includes a data transformation that cannot be reversed automatically}

---

## Deployment sequence

**Run migrations:** {before / after} code deployment

### Step-by-step

- [ ] 1. {Pre-migration step — e.g. deploy backwards-compatible code if expand/contract}
- [ ] 2. Run migration: `{exact command from CI/CD}`
- [ ] 3. {Post-migration step — e.g. deploy code that uses new schema}
- [ ] 4. Run validation queries (see below)
- [ ] 5. {Cleanup step — e.g. remove old column after dual-write period}

---

## Zero-downtime strategy

{Only if risk is Medium or High — describe the expand/contract phases:}

**Phase 1 — Expand:** {what to add without removing anything}
**Phase 2 — Migrate:** {data backfill or transformation, run in batches}
**Phase 3 — Contract:** {what to remove once the transition is complete}

**Dual-write period:** {how long code must write to both old and new columns before the old one is safe to drop}

---

## Validation queries

Run after migration to confirm correctness:

```sql
-- Confirm row counts unchanged (for non-destructive migrations)
SELECT COUNT(*) FROM {table};

-- Confirm no nulls in non-null column
SELECT COUNT(*) FROM {table} WHERE {column} IS NULL;

-- {Other specific validation for this migration}
```

**Expected results:** {what the queries should return if the migration succeeded}

---

## Rollback trigger conditions

Roll back the migration if:
- {Specific condition — e.g. error rate increases above X% after deployment}
- {Specific condition — e.g. validation query returns unexpected null count}
- {Specific condition — e.g. application logs show column-not-found errors}

---

## Code changes required alongside this migration

| File | Change required | Deploy before or after migration? |
|------|----------------|----------------------------------|
| {path} | {what must change} | {before / after / same deploy} |

{If no code changes are required, state that explicitly.}
```

## Gotchas

- Never drop a column in the same migration that removes the code using it. The code removal must be deployed and running in production before the column is dropped — otherwise a rollback of the code will break against the dropped column.
- Backfill operations must run in batches. A single `UPDATE` statement on a table with millions of rows will hold a lock for the entire duration and cause an outage. Batch by primary key range with a configurable batch size.
- `CREATE INDEX` without `CONCURRENTLY` (Postgres) or equivalent locks the table for reads and writes. Always use the concurrent form for production tables unless the table is small or a maintenance window is scheduled.
- Adding a non-null column without a default is not safe on Postgres < 11. On older versions, a default must be set at the column level, not applied post-add. Check the database version before writing the migration.
- A rollback that undoes a migration does not undo a data backfill. If the migration included a data transformation, note explicitly that rolling back the schema does not restore the original data.
- Column renames using expand/contract span multiple deployments. Document the timeline clearly — the old column must remain writable until all consumers have been updated and verified.
- The migration command in the plan must match what CI/CD actually runs. A plan that says `alembic upgrade head` when the pipeline runs `flask db upgrade` will fail silently.
- This skill pairs naturally with `/generate-runbook` (the runbook's Database and Migrations section should reference this plan), `/write-adr` (document the migration strategy decision — especially for high-risk or multi-phase migrations), and `/refactor-strategy` (large-scale data model refactors benefit from a phased migration plan as part of the broader strategy).
