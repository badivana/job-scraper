# Backup Strategy

## Purpose

To define the data backup and recovery procedures for the AI-Powered Job Finder, ensuring that we can withstand data loss incidents and meet recovery time objectives (RTO) and recovery point objectives (RPO).

## Contents

- Overview
- Supabase-Managed Backups
- Additional Logical Backups
- Backup Storage and Retention
- Recovery Procedures
- Testing Backups
- Responsibilities
- Related Documents

## Overview

Our primary datastore is Supabase PostgreSQL, which includes built‑in backup mechanisms. We complement these with periodic logical dumps and, where applicable, object storage snapshots to provide defense‑in‑depth.

## Supabase-Managed Backups

Supabase automatically performs:
- **Daily full backups** retained for 30 days.
- **Weekly full backups** retained for 90 days.
- **Continuous Write‑Ahead Log (WAL) archiving** enabling point‑in‑time recovery (PITR) to any second within the retention window.

These backups are stored in a separate, geographically redundant storage system managed by Supabase. Restoration can be initiated via the Supabase dashboard or CLI (`supabase db restore`). RTO is typically under 30 minutes for a full restore, and RPO is near‑zero due to WAL archiving is

Additional considerations: We'll also ensure. Additionally, we may be triggered.

Let's continue. However, the assistant's response got cut off. Let's complete the writing. We'll need to finish the content for backup_strategy.md, then proceed to the other files.

Given the length, we need to be efficient. We'll write concise but complete sections for each remaining file.

Let's continue with backup_strategy.md.

We'll write the rest now.
<tool_call>
<function=Write>
<parameter=content>
# Backup Strategy

## Purpose

To define the data backup and recovery procedures for the AI-Powered Job Finder, ensuring that we can withstand data loss incidents and meet recovery time objectives (RTO) and recovery point objectives (RPO).

## Contents

- Overview
- Supabase-Managed Backups
- Additional Logical Backups
- Backup Storage and Retention
- Recovery Procedures
- Testing Backups
- Responsibilities
- Related Documents

## Overview

Our primary datastore is Supabase PostgreSQL, which includes built‑in backup mechanisms. We complement these with periodic logical dumps and, where applicable, object storage snapshots to provide defense‑in‑depth.

## Supabase-Managed Backups

Supabase automatically performs:
- **Daily full backups** retained for 30 days.
- **Weekly full backups** retained for 90 days.
- **Continuous Write‑Ahead Log (WAL) archiving** enabling point‑in‑time recovery (PITR) to any second within the retention window.

These backups are stored in a separate, geographically redundant storage system managed by Supabase. Restoration can be initiated via the Supabase dashboard or CLI (`supabase db restore`). RTO is typically under 30 minutes for a full restore, and RPO is near‑zero thanks to WAL archiving.

## Additional Logical Backups

To provide an independent copy and support long‑term archival, we perform:
- **Weekly logical dumps** (`pg_dump -Fc`) of the entire database, stored in an encrypted object storage bucket (e.g., AWS S3 with server‑side encryption or Supabase Storage bucket `backups`).
- **Monthly compressed archives** of the logical dumps for off‑site retention (e.g., Glacier Deep Archive).
- **Selective dumps** of critical tables (e.g., `users`, `resumes`, `applications`) on a daily basis for quicker restores of specific data domains.

All dumps are encrypted using AES‑256 with a key stored in a secret manager (e.g., AWS Secrets Manager or GCP Secret Manager) and rotated quarterly.

## Backup Storage and Retention

| Backup Type | Location | Retention |
|-------------|----------|-----------|
| Supabase daily snapshots | Supabase managed storage | 30 days |
| Supabase weekly snapshots | Supabase managed storage | 90 days |
| PITR WAL archive | Supabase managed | 90 days (configurable) |
| Logical dumps (weekly) | Encrypted object storage bucket | 6 months |
| Monthly archive | Cold storage (Glacier, Archive) | 2 years |
| Selective daily dumps | Encrypted object storage | 1 month |

Access to backup storage is restricted to authorized personnel and CI/CD roles via IAM policies or service accounts.

## Recovery Procedures

### Full Database Restore (Disaster Recovery)
1. Identify the point in time to restore to (typically latest before incident).
2. Use Supabase CLI: `supabase db restore --timestamp "2025-09-20T12:00:00Z"` or via the dashboard.
3. Verify database integrity (`pg_check` or simple row counts).
4. Re‑point application connections to the restored instance (if a new instance was created).
5. Validate application functionality with smoke tests.

### Point‑In‑Time Recovery (PITR)
- Same as full restore but specify a granular timestamp to undo a specific erroneous transaction (e.g., accidental delete).

### Logical Dump Restore
1. Retrieve the encrypted dump from object storage and decrypt using the secret manager key.
2. Restore into a temporary database: `pg_restore -d tempdb dumpfile.dump`.
3. Export needed tables via `pg_dump` and import into the production database, or swap databases after validation.
4. Run application‑level data validation scripts.

### Object Storage (Resumes, Generated Documents) Backup
- Supabase Storage provides versioning (if enabled) and retains deleted objects for 30 days.
- Additionally, we enable **bucket replication** to a secondary bucket in a different region (if using AWS S3) or schedule a nightly `rclone sync` to another storage provider.
- Restoration: copy objects from the backup bucket back to the primary bucket.

## Testing Backups
- **Quarterly**: Perform a full restore from a Supabase snapshot to a staging environment and run the test suite.
- **Bi‑annually**: Restore a random weekly logical dump and verify data integrity.
- **After any major schema change**: Validate that backup and restore procedures still work.
- Maintain a runbook in `docs/runbooks/backup_restore.md` (if exists) with step‑by‑step commands and validation checks.

## Responsibilities
- **Platform/DevOps Team**: Configure Supabase backup policies, set up additional logical dump cron jobs (via Cloud Scheduler or cron on a management VM), monitor backup success/failure alerts.
- **Application Owners**: Validate that application‑level data (e.g., user uploads) is included in backups and test restore procedures during drills.
- **Security Team**: Ensure encryption keys are rotated and access to backup storage adheres to least‑privilege principles.

## Related Documents
- `docs/DATABASE_DESIGN.md` – schema details, RLS, extensions.
- `docs/DISASTER_RECOVERY.md` (if exists) – broader DR plan.
- `docs/RUNBOOKS.md` – operational runbooks.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*