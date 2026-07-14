# 002D-profile-bootstrap.md

## Objective
Create the database objects required to store additional user profile data linked to Supabase Auth users: a `public.profiles` table with columns for `role`, `onboarding_completed`, timestamps, and a trigger that automatically creates a profile row when a new user appears in `auth.users`.

## Scope
- SQL DDL to create the `public.profiles` table with a foreign key to `auth.users(id)`.
- Enable Row Level Security (optional; can rely on application‑level checks).
- Trigger function `handle_new_user()` that inserts a default profile for each new auth user.
- Trigger on `auth.users` (AFTER INSERT) to invoke the function.
- Helper function to update `updated_at` on profile changes.
- Alembic migration script that creates the above objects.
- Documentation of how the backend (or Supabase) will use this table (e.g., after successful registration, the backend may also explicitly insert a profile for portability).

## Deliverables
1. SQL file (or Alembic migration) containing:
   - `CREATE TABLE public.profiles ( id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE, role TEXT NOT NULL DEFAULT 'user', onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() );`
   - `ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;`
   - Function `update_updated_at_column()` and trigger on `public.profiles`.
   - Function `handle_new_user()` that inserts a row into `public.profiles` on `auth.users` insert.
   - Trigger `on_auth_user_created` AFTER INSERT ON `auth.users` FOR EACH ROW EXECUTE FUNCTION `handle_new_user()`.
2. Alembic revision script (`alembic/versions/<timestamp>_create_profiles_table.py`) that runs the SQL via `op.execute()`.
3. Update `alembic.ini` if needed (already exists from Phase 0).
4. Optional: a note in `LOCAL_SETUP.md` on how to apply migrations (`docker compose exec backend alembic upgrade head`).
5. No runtime code changes required beyond ensuring the migration is applied.

## Acceptance Criteria
- [ ] After running the migration, the `public.profiles` table exists with the specified columns and constraints.
- [ ] Inserting a new row into `auth.users` (via Supabase Auth sign‑up) automatically creates a corresponding row in `public.profiles` with default values (`role='user'`, `onboarding_completed=false`).
- [ ] Updating a profile row updates the `updated_at` column via the trigger.
- [ ] Deleting a user from `auth.users` cascades deletes the profile row (due to `ON DELETE CASCADE`).
- [ ] The migration can be applied and reverted cleanly (`alembic downgrade base` then `upgrade head`).

## Estimated Effort
2‑3 hours (writing SQL, Alembic script, testing locally via Docker Compose).

## Dependencies
- Phase 0 (PostgreSQL with pgvector already running via Docker Compose, Alembic configured).
- No other auth components required; this is purely a schema change.

---