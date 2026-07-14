# Migration Plan

## Purpose

To outline the process for managing database schema changes in a safe, version‑controlled, and reversible manner, ensuring minimal downtime and data integrity during evolution of the AI-Powered Job Finder’s data model.

## Contents

- Overview
- Migration Tools
- Migration Principles
- Branching and Versioning
- Migration Workflow
- Backward Compatibility
- Handling Breaking Changes
- Testing Migrations
- Deployment Integration
- Rollback Procedures
- Monitoring and Validation
- Responsibilities

## Overview

We treat the database schema as code. All structural changes (CREATE, ALTER, DROP, etc.) are captured as migration scripts that can be applied in order to any environment (local, staging, production). This enables reproducibility, auditability, and the ability to roll forward or back as needed.

## Migration Tools

- **Primary**: Alembic (integrated with SQLAlchemy) – generates upgrade/downgrade scripts from model changes.
- **Alternative**: Supabase Migration Interface (via the Supabase dashboard or CLI) – allows uploading SQL scripts directly; useful for ad‑hoc changes or when Alembic is not configured.
- **Supplementary**: Raw SQL scripts for data migrations or complex transformations that are harder to express via Alembic autogenerate.

## Migration Principles

1. **Atomicity**: Each migration should be as atomic as possible; if it fails, the database should be left unchanged (use transactions where supported).
2. **Idempotency where possible**: Design scripts so they can be re‑applied without adverse effects (e.g., use `IF NOT EXISTS`, `IF EXISTS`).
3. **Backward Compatibility**: Prefer changes that allow old and new code to coexist (add columns with defaults, make columns nullable, create new tables).
4. **Data Safety**: Avoid destructive operations (DROP COLUMN, TABLE) without a backup and a clear rollback path.
5. **Performance**: Avoid long‑running locks; batch large data updates, use `CONCURRENTLY` for index creation when possible, and consider performing heavy data migrations during off‑peak windows.
6. **Documentation**: Each migration file includes a clear comment describing its purpose and any special instructions.

## Branching and Versioning

- Migration scripts reside in `alembic/versions/` and are named `<rev_id>_<description>.alembic.py` (or `.sql` for raw SQL).
- The `alembic_version` table tracks the current revision.
- We follow **semantic versioning** for the application; migration versions are independent but we align major schema changes with major/minor releases when they involve breaking changes.
- Feature branches should include any necessary migrations; they are merged into `main` only after review and successful CI testing.

## Migration Workflow

1. **Change Model** (if using ORM): Update the SQLAlchemy model in `app/models/`.
2. **Generate Migration**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "brief description"
   ```
3. **Review Generated Script**: Check the output in `alembic/versions/`. Adjust as needed (e.g., add data migration steps, adjust defaults, ensure constraints are named).
4. **Unit Test Migration** (optional): Use a temporary database to apply the migration and verify the schema.
5. **Commit**: Add the migration file and any model changes to the same PR.
6. **CI Validation**: The CI pipeline runs `alembic upgrade head` on a test database and runs the test suite.
7. **Merge**: After approval, merge to `main`.
8. **Deploy**: As part of the deployment pipeline, the step `alembic upgrade head` is executed against the target database (staging, then production).
9. **Post‑Deploy Validation**: Run health checks and, if needed, data validation scripts.

## Backward Compatibility

- **Adding a Column**: Add as nullable with a server default if appropriate; backfill later via a separate data migration if needed.
- **Making a Column Non‑Nullable**: First add the column as nullable, populate data, then alter to NOT NULL in a subsequent migration.
- **Renaming a Column/Table**: Use the `ALTER TABLE ... RENAME TO` approach; keep the old name temporarily via a view or rename in two steps (add new column, copy data, drop old) to allow rollback.
- **Changing Column Type**: Use a temporary column, copy data with conversion, drop old column, rename temporary column.

## Handling Breaking Changes

When a breaking change is unavoidable (e.g., removing a deprecated column that is no longer used by any service):
1. **Deprecation Phase**: In release N, mark the column as deprecated (still present, but ignore in code). Log warnings if accessed.
2. **Removal Phase**: In release N+2 (or after a configured deprecation period), remove the column via a migration.
3. **Communication**: Clearly document the change in release notes and inform consumers of any APIs or exports that might be affected.
4. **Backup**: Ensure a recent backup exists before performing the drop.

## Testing Migrations

- **Local**: Developers can run `alembic upgrade head` on their local PostgreSQL (via Docker Compose) and run the test suite.
- **CI**: The pipeline mounts a temporary PostgreSQL container, runs migrations, and executes the integration test suite.
- **Staging**: Before production, we apply migrations to a staging environment that mirrors production and run smoke tests.
- **Data Migration Tests**: For scripts that modify data, we create a representative dataset and verify correctness.

## Deployment Integration

- The CI/CD pipeline includes a step:
  ```
  - name: Run database migrations
    run: alembic upgrade head
    working-directory: ./backend
  ```
- This step runs after the container image is pulled but before the application starts (or as an init container in Kubernetes).
- For zero‑downtime deployments, we ensure that migrations are compatible with both the old and new code versions (backward‑compatible changes only). If a migration is not backward compatible, we schedule a brief maintenance window or use a blue/green deployment strategy.

## Rollback Procedures

- **Forward‑Only Preference**: Because migrations are designed to be applied in order, we generally **do not** downgrade the schema; instead we fix issues with forward migrations.
- **Emergency Rollback**: If a catastrophic error occurs after migration, we can restore the database from a pre‑migration backup (Supabase PITR or logical dump) and then re‑apply a corrected migration sequence.
- **Downgrade Scripts**: Alembic generates `downgrade()` functions; we keep them updated for simple structural changes (adding/dropping columns/tables) but may not maintain them for complex data migrations. In such cases, we rely on backup restore.
- **Feature Flag Kill Switch**: If a migration introduces a behavioral change that causes issues, we can disable the new feature via a Supabase `feature_flags` table without needing to rollback the schema.

## Monitoring and Validation

- After migration, we run a set of validation queries:
  - Row counts per table compared to pre‑migration snapshots.
  - Checksums of critical data (if available).
  - Application health endpoints.
  - Replication lag (if using replicas).
- Alerts are configured to notify on migration failure (non‑zero exit code from `alembic upgrade`).

## Responsibilities
- **Developers**: Write backward‑compatible models, generate and review migrations, test locally.
- **DevOps / Platform**: Ensure the CI pipeline can run migrations against a test database, provide backup/restore procedures, monitor migration jobs.
- **Database Administrator (if any)**: Review complex migrations, approve any raw SQL that bypasses ORM, oversee backup validation.

## Related Documents
- `docs/DATABASE_DESIGN.md` – target schema, extensions, RLS.
- `docs/DEPLOYMENT.md` – deployment pipeline steps.
- `docs/SCALABILITY_PLAN.md` – considerations for scaling the database layer.
- `RUNBOOKS/migration.md` – step‑by‑step guide for executing migrations manually (if needed).

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*