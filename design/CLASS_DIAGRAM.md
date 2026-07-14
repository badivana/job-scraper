# Class Diagram

## Purpose

To depict the static structure of the core domain model of the AI-Powered Job Finder, showing the key classes (entities), their attributes, and relationships (associations, inheritance, dependencies) as implemented in the SQLAlchemy ORM layer.

## Contents

- Overview of Classes
- Relationships
- Notes on Inheritance and Mixins
- How the Diagram Relates to the Physical Schema

## Overview

The class diagram includes the principal domain concepts that persist in the database:

- **User** (extends `auth.users` via foreign key) – profile information.
- **Resume** – uploaded file, parsed text, skills, embedding vector.
- **Job** – scraped posting, normalized fields, deduplication hash.
- **Application** – tracks a user’s job application status over time.
- **SavedJob** – many‑to‑many link between a user and a job they have bookmarked.
- **GeneratedDocument** – cover letters, cold emails, skill‑gap analyses linked to a user and a job.
- **Notification** – records of emails or in‑app notices sent to users.
- **SearchHistory** – keeps a log of user search queries and filters.
- **AuditLog** – immutable trail of security‑relevant actions.
- **ScheduledTask** – definitions of recurring jobs (scraping, maintenance) driven by APScheduler or Celery Beat.

## Relationships

- `User` ↔ `Resume` (one‑to‑many): a user may have multiple resume versions.
- `User` ↔ `GeneratedDocument` (one‑to‑many): each generated document belongs to a user.
- `User` ↔ `SavedJob` (many‑to‑many via the `saved_jobs` association table).
- `User` ↔ `Application` (one‑to‑many): a user can apply to many jobs.
- `User` ↔ `Notification` (one‑to‑many).
- `User` ↔ `SearchHistory` (one‑to‑many).
- `User` ↔ `AuditLog` (one‑to‑many, via `actor_user_id` nullable).
- `Job` ↔ `SavedJob` (many‑to‑many via `saved_jobs`).
- `Job` ↔ `Application` (one‑to‑many): many users can apply to the same job.
- `Job` ↔ `GeneratedDocument` (one‑to‑many): documents are tied to a specific job.
- `Job` may have a many‑to‑many relationship with a `Skill` lookup table (if we store normalized job skills).

## Inheritance & Mixins

- Several models inherit from abstract mixins:
  - `TimestampMixin` adds `created_at` and `updated_at`.
  - `SoftDeleteMixin` adds `deleted_at` for logical deletion.
  - `UUIDMixin` provides a mixin may add a UUID primary key (we use explicit `uuid` columns with `uuid_generate_v4()`).
- The `User` model does **not** duplicate the entire `auth.users` table; instead it stores a foreign key `id` → `auth.users.id` and keeps only profile‑specific columns.

## Relation to Physical Schema

The classes map directly to tables in the Supabase PostgreSQL schema (see `DATABASE_DESIGN.md`). Column types, constraints (primary key, foreign key, unique, check), and indexes are derived from the ORM‑the Alembic` used as a reference for developers when extending the object model or writing raw SQL queries.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*