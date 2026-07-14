# Database Design

## Purpose

To describe the database schema, naming conventions, indexing strategy, and usage of Supabase PostgreSQL features such as UUID primary keys, Row Level Security (RLS), pgvector, authentication integration, and storage buckets.

## Contents

- Overview
- Schema Organization
- Data Types & Identifiers
- Tables & Relationships
- Indexing Strategy
- Row Level Security (RLS)
- Extensions (pgcrypto, pgvector, uuid-ossp)
- Supabase Auth Integration
- Storage Buckets
- Naming Conventions
- Migration Strategy

## Overview

The application uses Supabase’s managed PostgreSQL database. All application data resides in a single PostgreSQL cluster provided by Supabase. We leverage Supabase’s built‑in authentication service (via `auth` schema) and storage buckets for binary objects.

## Schema Organization

We use a public schema for application tables. The `auth` schema (managed by Supabase) contains users, identities, etc. We may create additional schemas for logging or analytics if needed, but core data stays in `public`.

### Schemas

| Schema | Purpose |
|--------|---------|
| `public` | Application tables (users, jobs, resumes, matches, etc.) |
| `auth`   | Supabase authentication (users, factors, sessions) – managed by Supabase |
| `storage`| Supabase object storage metadata – managed by Supabase |
| `pg_catalog` | System catalog |
| `information_schema` | Standard information schema |

## Data Types & Identifiers

- **Primary Keys**: UUID version 4 (`uuid`), generated via `uuid_generate_v4()` (extension `uuid-ossp`). Using UUIDs avoids exposing sequential IDs and simplifies distribution.
- **Timestamps**: `timestamptz` (timezone-aware) with default `now()`.
- **JSONB**: For flexible schema fields (e.g., raw scraped data, parsed resume sections).
- **Text**: Unlimited length for descriptions, bios, etc.
- **Boolean**, **Integer**, **Numeric**, **Enum** (via lookup tables) as appropriate.
- **Vector**: `vector(1536)` for embeddings (provided by `pgvector` extension).

## Tables & Relationships

### Core Entities

| Table | Description |
|-------|-------------|
| `users` | Extension of `auth.users` (via foreign key) storing profile info: `id` UUID PK -> `auth.users(id)`, `full_name`, `avatar_url`, `bio`, `location`, `created_at`, `updated_at`. |
| `resumes` | `id` UUID PK, `user_id` UUID FK -> `users.id`, `file_name`, `storage_key` (Supabase Storage path), `raw_text`, `parsed_json` JSONB, `skill_vector` vector(1536), `created_at`, `updated_at`. |
| `jobs` | `id` UUID PK, `source` (enum), `source_id` text (external ID), `title`, `company`, `location` JSONB, `description_text`, `salary_min` numeric, `salary_max` numeric, `currency` text, `employment_type` text, `remote_flag` boolean, `posted_date` timestamptz, `apply_url` text, `hash_dedup` text (unique), `created_at`. |
| `job_skills` | (optional) Many‑to‑many linking `jobs` to `skills` (if we store normalized skills). |
| `skills` | `id` UUID PK, `name` text unique, `taxonomy` (ESCO/O*NET). |
| `user_skills` | Many‑to‑many `users` ↔ `skills` with proficiency level. |
| `saved_jobs` | `id` UUID PK, `user_id` FK -> `users.id`, `job_id` FK -> `jobs.id`, `saved_at` timestamptz, `note` text. Unique (`user_id`, `job_id`). |
| `applications` | `id` UUID PK, `user_id` FK, `job_id` FK, `status` enum (saved, applied, oa, interview, offer, rejected, withdrawn), `applied_at` timestamptz, `updated_at` timestamptz, `notes` text. |
| `generated_documents` | `id` UUID PK, `user_id` FK, `job_id` FK, `doc_type` enum (cover_letter, cold_email, skill_gap), `content_text`, `storage_key` (PDF/DOCX), `created_at`. |
| `notifications` | `id` UUID PK, `user_id` FK, `type` enum (email, inapp), `channel` enum, `subject` text, `body_text` text, `sent_at` timestamptz, `status` enum (pending, sent, failed). |
| `search_history` | `id` UUID PK, `user_id` FK, `query_text`, `filters_json` JSONB, `timestamp` timestamptz. |
| `audit_log` | `id` UUID PK, `actor_user_id` FK (nullable), `action` text, `target_table` text, `target_id` UUID, `changes_json` JSONB, `timestamp` timestamptz. |

### Relationships

- `users.id` → `auth.users.id` (one‑to‑one, enforced via foreign key).
- `resumes.user_id` → `users.id`.
- `jobs` independent (no user FK).
- `saved_jobs` links a user to a saved job (many‑to‑many via junction table).
- `applications` links a user to a job (one application per user‑job; unique constraint).
- `generated_documents` links a user and a job.
- `notifications` per user.
- `search_history` per user.
- `audit_log` optional actor.

## Indexing Strategy

- Primary key indexes automatically on UUID columns.
- Foreign key columns indexed for join performance.
- `jobs.hash_dedup` unique index to prevent duplicates.
- `jobs.posted_date` index for recent‑job queries.
- `jobs.location` (JSONB) indexed via GIN for location‑based filtering.
- `resumes.skill_vector` indexed with `ivfflat` (pgvector) for ANN search.
  ```sql
  CREATE INDEX ON resumes USING ivfflat (skill_vector vector_cosine_ops) WITH (lists = 100);
  ```
- `users.email` (via auth) already unique; we may create a redundant index on `users` if we store email copy.
- `search_history.timestamp` index for recent searches.
- Composite indexes on frequent query patterns:
  - `saved_jobs (user_id, created_at DESC)`.
  - `applications (user_id, status, applied_at DESC)`.

## Row Level Security (RLS)

Enable RLS on all tables containing user‑specific data. Policies ensure users can only access their own rows.

### Example Policies

- **users**: `SELECT` allowed only for own record (`auth.uid() = id`). `UPDATE` only for own record.
- **resumes**: `SELECT`, `UPDATE`, `DELETE` only where `user_id = auth.uid()`.
- **saved_jobs**: `INSERT` allowed for own user; `SELECT`/`DELETE` where `user_id = auth.uid()`.
- **applications**: `INSERT` allowed for own user; `SELECT`/`UPDATE`/`DELETE` where `user_id = auth.uid()`.
- **generated_documents**: Similar to resumes.
- **notifications**: `SELECT` where `user_id = auth.uid()`.
- **search_history**: `SELECT` where `user_id = auth.uid()`.
- **jobs**: No RLS (public read‑only for authenticated users; optional admin-only write).

Enable RLS via:
```sql
ALTER TABLE ENABLE ROW LEVEL SECURITY;
```

### Admin / Service Role

Supabase provides a `service_role` key that bypasses RLS for backend server‑side operations (used by FastAPI). The frontend uses `anon` key with RLS enforced.

## Extensions

Enable required extensions (via Supabase UI or SQL):

- `uuid-ossp` – UUID generation.
- `pgcrypto` – cryptographic functions (if needed).
- `pgvector` – vector similarity search.
- `btree_gin` – for indexing JSONB and other types.
- `citext` – case‑insensitive text (optional for email lookups).

## Supabase Auth Integration

- Users sign up / log in via Supabase Auth (email/password, OAuth providers: Google, GitHub, etc.).
- Access tokens (JWT) are issued by Supabase and include claims: `sub` (user ID), `email`, `role` (anon/authenticated), `aud`, `exp`.
- The FastAPI backend validates the JWT using Supabase’s published JWKS (`https://<project>.supabase.co/auth/v1/keys`).
- Authorization: endpoints check `role` claim and, where needed, compare `sub` (user ID) with resource ownership.

## Storage Buckets

We create the following buckets (private, with signed URLs for download):

| Bucket | Purpose |
|--------|---------|
| `resumes` | Original uploaded resume files (PDF/DOCX). |
| `documents` | Generated cover letters, CVs, PDF exports. |
| `avatars` | User profile images (optional). |
| `assets` | Static assets (logos, icons) if needed. |

Each bucket has:
- **File size limit**: 10 MB (resumes), 5 MB (documents).
- **Allowed MIME types**: `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `image/png`, `image/jpeg`.
- **Row Level Security**: Not applicable; storage policies mimic bucket‑level access (private, authenticated upload/download).

## Naming Conventions

- **Tables**: snake_case, plural (e.g., `users`, `resumes`, `jobs`).
- **Columns**: snake_case.
- **Primary Keys**: `id` (uuid).
- **Foreign Keys**: `{referenced_table}_id` (e.g., `user_id`, `job_id`).
- **Timestamps**: `created_at`, `updated_at` (timestamptz).
- **Enum Types**: Created as PostgreSQL `enum` types, singular, snake_case, prefixed with `enum_` if needed (e.g., `employment_type`).
- **Indexes**: `idx_{table}_{columns}`.
- **Constraints**: `fk_{table}_{referenced_table}`, `uq_{table}_{columns}`.

## Migration Strategy

Supabase provides a migration system via the Supabase CLI (`supabase db push`) or via the dashboard’s SQL editor. We will:

1. Keep all DDL in version‑controlled `.sql` files under `database/migrations/`.
2. Use `supabase migration up` to apply new migrations to each environment (dev, staging, prod).
3. For breaking changes, write migration scripts that preserve data (e.g., `ALTER TABLE ... ADD COLUMN`, `RENAME`, `BACKUP TABLE`).
4. Run `supabase db dump` periodically for backup verification.
5. Leverage Supabase’s point‑in‑time recovery (PITR) for disaster recovery.

## Diagram (Optional)

An entity‑relationship diagram can be generated from the schema using tools like `schemaspy` or directly exported from Supabase.

## Summary

- **UUID primary keys** guarantee uniqueness and hide internal sequencing.
- **Row Level Security** ensures data isolation per user, enforced at the database level.
- **pgvector** enables efficient similarity search for resumes/jobs without an external vector store.
- **Supabase Auth** offloads user management, MFA, OAuth, and email flows.
- **Storage buckets** keep binaries out of the DB while retaining access control via signed URLs.
- This design satisfies scalability, security, and maintainability requirements for a SaaS product.