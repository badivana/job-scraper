# 002B-backend-auth.md

## Objective
Implement the backend authentication layer: JWT verification using line of trust as a Service (JWKS) verification, authentication middleware, protected route dependency, and auth API endpoints for registration, login, logout, refresh, password reset, and email verification.

## Scope
- FastAPI utilities to fetch and cache Supabase JWKS and verify RS256 tokens.
- HTTPBearer dependency (`get_current_user`) that validates the `Authorization: Bearer <token>` header.
- Middleware (or dependency‑based protection) that attaches user info to `request.state`.
- Auth router (`/api/v1/auth/*`) exposing:
  - `POST /register` – proxies to Supabase `signUp` (via `supabase-py` or direct HTTP) then creates a profile row.
  - `POST /login` – proxies to Supabase `signInWithPassword`.
  - `POST /logout` – calls Supabase `signOut`.
  - `POST /refresh` – exchanges refresh token for new access token via Supabase `refreshSession`.
  - `POST /reset-password` – triggers Supabase password reset email.
  - `POST /verify-email` – verifies email via token (optional).
- Error handling returning consistent JSON error responses.
- Logging of authentication attempts (success/failure) without leaking secrets.
- Environment variable integration (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `JWT_ALGORITHM`, etc.).

## Deliverables
1. `app/core/security.py` – functions `get_jwks()` (cached) and `verify_supabase_jwt(token: str) -> dict | None`.
2. `app/middleware/auth_middleware.py` (or use dependency directly) – FastAPI middleware that extracts token, calls verifier, sets `request.state.user`.
3. `app/api/v1/routers/auth.py` – implements the endpoints listed above, using the Supabase Python client (`supabase-py`) with service role key for admin actions (profile creation).
4. Updates to `app/main.py` to include the auth router with prefix `/api/v1/auth`.
5. Necessary Pydantic models for request bodies (e.g., `UserRegister`, `UserLogin`, `TokenRefresh`).
6. Update `requirements.txt` (add `supabase-py` if not already present, ensure `python‑dotenv` etc.).

## Acceptance Criteria
- [ ] `POST /api/v1/auth/register` with valid email/password creates a user in Supabase auth and a matching row in `public.profiles`; returns `{id, email}`.
- [ ] `POST /api/v1/auth/login` returns an access token (and optional refresh token cookie) that is accepted by the auth middleware.
- [ ] Requests lacking a valid `Authorization` header receive `401` with `WWW-Authenticate: Bearer`.
- [ ] Expired or malformed tokens produce `401`.
- [ ] `/api/v1/auth/logout` clears the refresh token cookie and calls Supabase signOut.
- [ ] `/api/v1/auth/refresh` returns a new access token when supplied a valid refresh token.
- [ ] Password reset endpoint triggers an email (can be tested in dev with Mailhog or similar).
- [ ] All endpoints are covered by unit tests (see 002E‑auth‑testing.md).
- [ ] No hard‑coded secrets; all configuration via environment variables.

## Estimated Effort
4‑6 hours (implementation of security utils, middleware, router, and integration).

## Dependencies
- Phase 0 (FastAPI setup, Docker, environment variables).
- 002A‑supabase‑auth.md (Supabase configured).
- 002D‑profile‑bootstrap.md (database schema for profiles).

---