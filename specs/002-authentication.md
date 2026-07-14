# 002-authentication.md

## 1. Objective
Implement a secure, production‑ready authentication system for the AI‑Powered Job Finder SaaS that allows users to sign up, log in, manage sessions, and protect routes using Supabase Auth and JSON Web Tokens (JWT). The system must support email/password sign‑up, email/password login, optional OAuth providers (Google, GitHub), password reset, email verification, and logout while maintaining stateless API security via JWTs issued by Supabase and validated by the FastAPI backend.

## 2. Scope
- **In‑scope**:
  - Supabase Auth configuration (email/password, OAuth providers).
  - FastAPI middleware for JWT verification and role‑based access.
  - Next.js middleware (via `getServerSideProps` / `middleware.ts`) for protecting client routes and attaching user context.
  - Authentication API endpoints (`/auth/register`, `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/reset-password`, `/auth/verify-email`).
  - Database schema changes to store minimal user metadata (e.g., role, profile completion flag) linked to Supabase `auth.users`.
  - Unit and integration tests for authentication flows.
  - Documentation updates (API spec, local setup guide).
- **Out‑of‑scope**:
  - Resume upload, job scraping, AI matching, dashboard UI, profile management, billing, admin UI, role‑based permissions beyond basic authenticated/unauthenticated distinction, MFA implementation, social login UI beyond provider configuration.

## 3. Deliverables
1. **Supabase Auth Setup** – Enable email/password, Google, GitHub providers; configure email templates, redirect URLs, JWT settings.
2. **Supabase Auth Schema Extension** – Add a `public.profiles` table (or similar) linking `auth.users.id` to additional app‑specific fields (`role`, `created_at`, `onboarding_completed`).
3. **FastAPI Authentication Module**:
   - `app/core/security.py`: JWT verification utilities using Supabase JWKS.
   - `app/middleware/auth_middleware.py`: FastAPI middleware that validates Authorization header, injects user info into request state.
   - Dependency (`get_current_user`) for protected routes.
   - `app/api/v1/routers/auth.py`: Endpoints for registration, login, logout, token refresh, password reset, email verification.
4. **Next.js Authentication Layer**:
   - `lib/supabaseClient.js`: Singleton Supabase client (anon key) for client‑side usage.
   - `middleware.ts` (or `_middleware.ts`): Edge middleware that validates Supabase session cookie, redirects unauthenticated users to `/login`, and sets `req.user` for downstream pages.
   - `pages/api/auth/[...auth].ts` (or route handlers) that proxy to Supabase Auth (optional) or handle custom logic (e.g., logout).
   - Protected page wrappers (`withAuth` HOC) for dashboard‑related pages (future phases).
5. **Database Migration** – Alembic migration scripts to create `public.profiles` table and any indexes.
6. **Tests**:
   - Backend: pytest tests for `/auth/*` endpoints, middleware behavior, JWT validation edge cases.
   - Frontend: Jest/React Testing Library tests for login flow, redirect behavior, protected route access.
   - Cypress (optional) end‑to‑end smoke test for sign‑up → login → access protected page.
7. **Documentation Updates**:
   - `docs/API_SPEC.md` – Add authentication endpoints.
   - `docs/SECURITY.md` – Detail JWT handling, token expiration, refresh strategy.
   - `LOCAL_SETUP.md` – Instructions for configuring Supabase Auth locally (via Supabase CLI or dashboard).
   - `context/progress-tracker.md` – Mark Phase 1 tasks as completed.

## 4. User Stories
| ID | As a | I want to | So that |
|----|------|-----------|---------|
| US-001 | Unauthenticated visitor | Sign up with email and password | I can create an account and start using the platform. |
| US-002 | Unauthenticated visitor | Log in with email and password | I can access my account and protected features. |
| US-003 | Unauthenticated visitor | Sign in with Google or GitHub | I can avoid creating another password. |
| US-004 | Authenticated user | Log out securely | My session is terminated and tokens are invalidated. |
| US-005 | Authenticated user | Refresh an expired access token without re‑entering credentials | I can stay logged in seamlessly. |
| US-006 | User who forgot password | Reset my password via email link | I can regain access to my account. |
| US-007 | New user | Verify my email address after sign‑up | I confirm ownership of the email and unlock full functionality. |
| US-008 | System | Reject requests lacking a valid JWT | Only authenticated users can access protected resources. |
| US-009 | System | Gracefully handle expired or malformed tokens | Clients receive a clear 401 response with guidance to re‑authenticate. |
| US-010 | Developer | See clear, testable authentication logic in the codebase | I can maintain and extend the system with confidence. |

## 5. Functional Requirements
1. **User Registration**
   - Accept `email`, `password`, optional `full_name`.
   - Call Supabase `signUp` endpoint.
   - On success, create a profile row in `public.profiles` with default values (`role = 'user'`, `onboarding_completed = false`).
   - Return a minimal user object (id, email) and a session token (access_token, refresh_token).
2. **User Login**
   - Accept `email` and `password`.
   - Call Supabase `signInWithPassword`.
   - Return JWT access token and refresh token (httpOnly secure cookies or JSON body, depending on client).
   - Set appropriate `Set‑Cookie` headers for Next.js middleware if using cookie‑based approach.
3. **OAuth Login (Google, GitHub)**
   - Redirect user to provider login flow via Supabase.
   - After callback, create or link user in `auth.users` and ensure profile row exists.
   - Return tokens as above.
4. **Token Refresh**
   - Accept a valid refresh token (httpOnly cookie or request body).
   - Validate via Supabase `refreshSession`.
   - Rotate refresh token (if supported) and issue new access token.
5. **Logout**
   - Invalidate the refresh token on Supabase (`signOut`).
   - Clear cookies on client and server.
6. **Password Reset**
   - Accept email, trigger Supabase `resetPasswordForEmail`.
   - Provide a reset link that leads to a frontend page where user enters new password.
   - Upon submission, call Supabase `updateUser` with new password.
7. **Email Verification**
   - After sign‑up, Supabase sends verification email.
   - Clicking link verifies email in `auth.users`.
   - Optionally expose an endpoint to manually verify if needed.
8. **Route Protection (Backend)**
   - Middleware checks for `Authorization: Bearer <access_token>` header.
   - Validates token signature using Supabase JWKS, checks `exp`, `aud` (`authenticated`), and optionally `role` claim.
   - On failure, returns `401 Unauthorized` with `WWW-Authenticate` header.
   - On success, attaches `user_id`, `email`, `role` to `request.state` for downstream handlers.
9. **Route Protection (Frontend)**
   - Edge middleware (`middleware.ts`) reads Supabase session cookie (`sb-<project>-auth-token`).
   - If cookie missing or invalid, redirects to `/login`.
   - If valid, attaches user info to request and proceeds.
   - Pages can use `getServerSideProps` with Supabase client to fetch private data.
10. **Session Management**
    - Access token short‑lived (e.g., 15 min).
    - Refresh token long‑lived (e.g., 7 days) stored in httpOnly, Secure, SameSite=Strict cookie.
    - Refresh token rotation optional but recommended.

## 6. Non‑functional Requirements
| Requirement | Description | Target |
|------------|-------------|--------|
| **Performance** | Authentication endpoints must respond in ≤150 ms (p95) under normal load. | ≤150 ms |
| **Scalability** | Stateless JWT verification allows horizontal scaling of API instances. | No sticky sessions required. |
| **Security** | Tokens must be signed with RS256 using Supabase‑managed keys; access tokens short‑lived; refresh tokens httpOnly & Secure; password hashing handled by Supabase (bcrypt). | OWASP ASVS Level 2 |
| **Availability** | Auth service should be highly available; rely on Supabase’s managed SLA (≥99.9%). | ≥99.9% uptime |
| **Observability** | Log authentication attempts (success/failure) with redacted PII; emit metrics for login rate, token renewal rate, failed attempts. | Structured JSON logs + Prometheus metrics |
| **Compliance** | GDPR‑ready: ability to delete user data (via Supabase admin API) on request. | Support data deletion request |
| **Maintainability** | Clear separation of concerns: Supabase handles auth, FastAPI validates, Next.js handles UI. | Well‑documented modules |

## 7. Supabase Auth Architecture
- **Supabase Project**
  - Enable **Email/Password**, **Google**, **GitHub** providers.
  - Configure **JWT Settings**:
    - `expiration_in`: 900 seconds (15 min) for access token.
    - `refresh_token_rotation_enabled`: true.
    - `aud`: `authenticated`.
    - `role`: `anon` for public calls, `service_role` for backend (stored as secret).
  - **Email Templates**: Customize confirmation, password reset, magic link emails with branding.
  - **Redirect URLs**: `http://localhost:3000/auth/callback` (dev), production URL for OAuth callbacks.
  - **Database**: `auth.users` table managed by Supabase; we supplement with `public.profiles`.
- **Interaction Flow**
  1. Client (browser or mobile) calls Supabase JS client (`@supabase/supabase-js`) for sign‑up/login.
  2. Supabase validates credentials, issues JWT access token + refresh token (returned in response body and set as httpOnly cookie if using cookie strategy).
  3. Client stores access token in memory (or cookie) and includes it in `Authorization` header for API calls.
  4. FastAPI receives request, runs JWT verification middleware using Supabase JWKS (public keys fetched from `https://<project>.supabase.co/auth/v1/keys`).
  5. On success, request proceeds; on failure, returns `401`.
  6. For server‑side rendering (Next.js), middleware reads the same cookie, validates via Supabase SDK (`supabase.auth.getUser()`), and redirects if needed.
- **Security Considerations**
  - Supabase manages cryptographic keys; we never store private keys.
  - All client‑to‑Supabase communication occurs over HTTPS.
  - `service_role` key stored as secret (`SUPABASE_SERVICE_ROLE_KEY`) for admin operations (e.g., creating profile row on sign‑up).

## 8. JWT Flow
1. **Token Issuance** (Supabase)
   - Upon successful authentication, Supabase creates a JWT:
     - Header: `{ "alg": "RS256", "typ": "JWT" }`
     - Payload includes:
       - `sub`: user UUID (matches `auth.users.id`).
       - `email`: user email.
       - `role`: `authenticated` (or `anon` for unauthenticated).
       - `aud`: `authenticated`.
       - `exp`: issuance time + `expiration_in`.
       - `iat`: issuance time.
       - `app_metadata`, `user_metadata` (as provided).
   - Signed with Supabase’s private key; public key exposed via JWKS endpoint.
2. **Token Transmission**
   - Access token returned in JSON body and/or set as `Authorization: Bearer <token>` header expected by clients.
   - Refresh token set as httpOnly, Secure, SameSite cookie (name: `sb-<project>-refresh-token` or custom).
3. **Token Validation** (FastAPI)
   - Middleware extracts token from `Authorization` header.
   - Retrieves Supabase JWKS (cached for performance).
   - Verifies signature, checks `exp`, `aud`, optionally `iss`.
   - Extracts claims (`sub`, `email`, `role`) and injects into `request.state.user`.
4. **Token Refresh**
   - Client sends refresh token (cookie) to `/auth/refresh`.
   - Backend forwards to Supabase `refreshSession` (or client calls Supabase directly).
   - Supabase validates refresh token, issues new access token (new expiry) and new refresh token (if rotation enabled).
   - New tokens returned; client replaces stored token/cookie.

## 9. Session Management
- **Client‑Side (Next.js)**
  - Use Supabase JS client to persist session in `localStorage` (optional) and cookies.
  - Middleware runs on each request; if session valid, attaches `req.user` for `getServerSideProps`.
  - On logout, call `supabase.auth.signOut()` which clears cookies and local storage.
- **Server‑Side (FastAPI)**
  - No server‑side session storage; authentication is stateless via JWT.
  - Refresh token validation relies on Supabase; we do not store refresh tokens ourselves.
  - Optionally maintain a token blacklist in Redis for immediate logout (if needed).
- **Token Expiration & Renewal**
  - Access token short‑lived (~15 min) to limit theft window.
  - Refresh token longer‑lived (7 days) with rotation to mitigate replay attacks.
  - Silent refresh performed by frontend before token expiration (e.g., via iframe or background request).

## 10. Route Protection
### Backend (FastAPI)
- Define a dependency:
  ```python
  from fastapi import Depends, HTTPException, status
  from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  from app.core.security import verify_supabase_jwt

  oauth2_scheme = HTTPBearer(auto_error=False)

  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
  ) -> dict:
      if credentials is None:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Not authenticated",
              headers={"WWW-Authenticate": "Bearer"},
          )
      user = verify_supabase_jwt(credentials.credentials)
      if not user:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid authentication credentials",
              headers={"WWW-Authenticate": "Bearer"},
          )
      return user
  ```
- Protect routers via `dependencies=[Depends(get_current_user)]` or per‑route.

### Frontend (Next.js)
- **Middleware (`middleware.ts`)**:
  ```ts
  import { NextResponse } from 'next/server'
  import type { NextRequest } from 'next/server'
  import { createClient } from '@/lib/supabaseClient'

  export async function middleware(req: NextRequest) {
    const res = NextResponse.next()
    const supabase = createClient()
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user && !req.nextUrl.pathname.startsWith('/login') && !req.nextUrl.pathname.startsWith('/auth')) {
      const url = req.nextUrl.clone()
      url.pathname = '/login'
      return NextResponse.redirect(url)
    }

    return res
  }
  ```
- **Protected Pages**: Use `getServerSideProps` with `supabase.auth.getUser()` to fetch private data or redirect if absent.

## 11. FastAPI Middleware
- **File**: `app/middleware/auth_middleware.py`
- Implements `dispatch` function that:
  1. Extracts token from `Authorization` header.
  2. Calls `verify_supabase_jwt` (util that fetches JWKS, validates).
  3. On success, sets `request.state.user = user_data`.
  4. On failure, returns `JSONResponse(status_code=401, content={"detail":"Not authenticated"})`.
- **Security Utils**: `app/core/security.py`
  - `get_jwks()`: fetches and caches JWKS.
  - `verify_supabase_jwt(token: str) -> dict | None`.

## 12. Next.js Middleware
- **File**: `middleware.ts` at project root (or `_middleware.ts` for pages router).
- Uses `@supabase/supabase-js` with the **anon** key.
- Calls `supabase.auth.getUser()` on each request.
- If no user and path not in public whitelist (`/login`, `/auth/*`, `/_next/*`, `/api/*`), redirects to `/login`.
- Optionally adds `x-user-id` header for downstream API routes (if using same Supabase client).

## 13. API Endpoints
All under `/api/v1/auth` prefix.

| Method | Path | Description | Request Body | Success Response |
|--------|------|-------------|--------------|------------------|
| `POST` | `/register` | Sign up new user | `{ email: string, password: string, full_name?: string }` | `{ id: string, email: string }` |
| `POST` | `/login` | Log in with credentials | `{ email: string, password: string }` | `{ access_token: string, refresh_token: string }` (or set httpOnly cookie) |
| `POST` | `/logout` | Log out | none | `{ message: "Logged out" }` |
| `POST` | `/refresh` | Refresh access token | `{ refresh_token: string }` (or read cookie) | `{ access_token: string }` |
| `POST` | `/reset-password` | Initiate password reset | `{ email: string }` | `{ message: "Reset email sent" }` |
| `POST` | `/verify-email` | Verify email via token (optional) | `{ token: string }` | `{ message: "Email verified" }` |
| `GET`  | `/me` | Get current user profile (protected) | none | `{ id, email, role, onboarding_completed }` |
| `GET`  | `/providers` | List enabled OAuth providers | none | `{ providers: ["google", "github"] }` |
| `GET`  | `/oauth/{provider}` | Initiate OAuth redirect (optional) | none | 302 redirect to provider |

### Notes
- Endpoints may delegate directly to Supabase JS client on the frontend; backend primarily validates tokens and manages profile data.
- For security, `/login` and `/refresh` should set `Set-Cookie` with `HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=<refresh_token_ttl>` and return only access token in body (or none).
- `/logout` should call Supabase `signOut` and clear the cookie.

## 14. Database Changes
### Migration (Alembic)
```sql
-- Create profiles table
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'user',
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable row level security (optional, rely on supabase policies)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create trigger to set updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Insert default profile on new user (via backend after sign‑up)
-- OR use Supabase database trigger on auth.users insert:
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
   INSERT INTO public.profiles (id, role, onboarding_completed)
   VALUES (NEW.id, 'user', FALSE)
   ON CONFLICT (id) DO NOTHING;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```
- The backend may also explicitly insert a profile row after successful sign‑up for portability.

## 15. Sequence Diagrams
### 1. User Sign‑Up (Email/Password)
```
+----------------+          +----------------+          +----------------+
|   Browser      |          |   Supabase     |          |   Backend API  |
+----------------+          +----------------+          +----------------+
        | signUp(email,pas) |---------------------------->|
        |                   |  validate email/password     |
        |                   |---------------------------->|
        |                   |  insert into auth.users      |
        |                   |  issue JWT (access,refresh) |
        |                   |<-----------------------------|
        |   access_token,   |<-----------------------------|
        |   refresh_token   |                             |
        |                   |                             |
        |   (optional)      |---------------------------->|
        |   POST /profile   |  create profile row (if not |
        |   {id,role...}    |  using DB trigger)          |
        |                   |<-----------------------------|
        |   200 OK          |                             |
        +----------------+          +----------------+          +----------------+
```

### 2. User Login (Email/Password)
```
+----------------+          +----------------+          +----------------+
|   Browser      |          |   Supabase     |          |   Backend API  |
+----------------+          +----------------+          +----------------+
        | signIn(email,pas) |---------------------------->|
        |                   |  validate credentials        |
        |                   |---------------------------->|
        |                   |  issue JWT (access,refresh) |
        |                   |<-----------------------------|
        |   access_token,   |<-----------------------------|
        |   refresh_token   |                             |
        |                   |                             |
        |   (store tokens)  |                             |
        +----------------+          +----------------+          +----------------+
```

### 3. Access Protected Backend Endpoint
```
+----------------+          +----------------+          +----------------+
|   Browser      |          |   Backend API  |          |   Supabase JWKS|
+----------------+          +----------------+          +----------------+
        | GET /api/v1/items  |---------------------------->|
        | Authorization: Bearer <access_token>|          |
        |                   |---------------------------->|
        |                   | extract token                |
        |                   |---------------------------->|
        |                   | fetch JWKS (cached)          |
        |                   |<-----------------------------|
        |                   | verify signature & claims    |
        |                   |---------------------------->|
        |                   | 200 OK + data                |
        |                   |<-----------------------------|
        |   data            |<-----------------------------|
        +----------------+          +----------------+          +----------------+
```

### 4. Token Refresh
```
+----------------+          +----------------+          +----------------+
|   Browser      |          |   Backend API  |          |   Supabase     |
+----------------+          +----------------+          +----------------+
        | POST /auth/refresh |---------------------------->|
        | Cookie: refresh_token|                           |
        |                   |---------------------------->|
        |                   | forward refresh to Supabase  |
        |                   |---------------------------->|
        |                   | Supabase validates & rotates |
        |                   |<-----------------------------|
        |   new_access,     |<-----------------------------|
        |   new_refresh     |                             |
        |                   | (Set-Cookie: new_refresh)    |
        |                   |---------------------------->|
        |   200 OK {access} |<-----------------------------|
        +----------------+          +----------------+          +----------------+
```

### 5. Logout
```
+----------------+          +----------------+          +----------------+
|   Browser      |          |   Backend API  |          |   Supabase     |
+----------------+          +----------------+          +----------------+
        | POST /auth/logout  |---------------------------->|
        |                   |---------------------------->|
        |                   | call supabase.auth.signOut() |
        |                   |<-----------------------------|
        |                   | clear cookie                 |
        |                   |---------------------------->|
        |   200 OK          |<-----------------------------|
        +----------------+          +----------------+          +----------------+
```

## 16. Security
- **Token Signing**: RS256 with Supabase‑managed keys; no private key stored in repo.
- **Token Storage**: Access token kept in memory (or short‑lived cookie); refresh token httpOnly, Secure, SameSite=Strict.
- **CORS**: Restrict to trusted origins (environment variable `ALLOWED_ORIGINS`).
- **Rate Limiting**: Apply per‑IP limit on `/auth/*` endpoints (e.g., 5 attempts/minute) using Redis or in‑memory store.
- **Input Validation**: All request bodies validated via Pydantic models (email format, password strength).
- **Password Policy**: Enforced by Supabase (minimum length, optional complexity). Backend may also validate length ≥8.
- **Email Enumeration Mitigation**: Use generic messages (`"If the account exists, you will receive an email."`) for login/password reset.
- **Audit Logs**: Log authentication events (user_id, outcome, IP) to a secure log store (e.g., Supabase table `auth_audit` or external SIEM) without exposing passwords.
- **Headers**: Implement `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy` via middleware.
- **Dependency Scanning**: Run `safety` or `npm audit` in CI to detect vulnerable packages.
- **Secrets Management**: Never commit `.env`; use platform secret injectors (GitHub Secrets, Docker secrets, Kubernetes secrets, etc.).
- **Supabase Service Role**: Stored as secret `SUPABASE_SERVICE_ROLE_KEY` and used only by backend for admin operations (e.g., creating profile).
- **Anon Key**: Exposed to frontend (`SUPABASE_ANON_KEY`) – limited to read/write per row‑level security policies.

## 17. Testing Strategy
### Backend (Python)
- **Unit Tests**
  - `test_security.py`: Verify `verify_supabase_jwt` with valid/expired/malformed tokens.
  - `test_auth_middleware.py`: Ensure middleware attaches user on valid token, returns 401 on missing/invalid.
  - `test_auth_routes.py`: Test each endpoint:
    - Registration success, duplicate email, invalid email.
    - Login success, wrong password, locked account (if applicable).
    - Token refresh with valid/expired refresh token.
    - Logout clears cookie.
    - Password reset flow (mock Supabase email send).
- **Fixtures**: Use `pytest-asyncio` and `httpx.AsyncClient` with `ASGITransport`.
- **Mock Supabase**: For unit tests, mock the Supabase client or JWKS fetch using `responses` library.
- **Coverage Target**: ≥80%.

### Frontend (JavaScript/TypeScript)
- **Unit Tests**
  - `lib/supabaseClient.test.ts`: Ensure singleton creation.
  - `middleware.test.ts`: Simulate request with/without cookie, assert redirect.
  - `pages/login.test.ts`: Render form, mock Supabase `signInWithPassword`, test redirect on success.
  - `pages/register.test.ts`: Similar for sign‑up.
  - `pages/auth/[...auth].test.ts`: Test OAuth callback handling.
- **Testing Library**: Use `@testing-library/react` and `@testing-library/jest-dom`.
- **Mock Supabase**: Use `@supabase/supabase-js` mock module or `msw` (Mock Service Worker) to intercept API calls.
- **End‑to‑End (Optional)**
  - Cypress script: visit `/register`, fill valid credentials, submit, verify redirect to `/dashboard`, check that protected UI shows user email, then click logout and verify redirect to `/login`.
- **CI Integration**: Run `npm test` and `pytest` as steps in GitHub Actions.

### Contract Tests
- Ensure the shape of JWT payload matches expectations (`sub`, `email`, `exp`, `aud`, `role`).
- Validate that `/auth/me` returns the same `sub` as created profile.

## 18. Acceptance Criteria
| Criterion | Description |
|-----------|-------------|
| **AC‑001** | A new user can register with email/password, receive an access token, and have a profile row created in `public.profiles`. |
| **AC‑002** | A registered user can log in with correct credentials and receive a valid access token (and refresh token). |
| **AC‑003** | Invalid credentials produce a generic error message (no email leakage). |
| **AC‑004** | Accessing any `/api/v1/*` endpoint (except `/auth/*`) without a valid token yields HTTP 401. |
| **AC‑005** | A valid token allows access to protected endpoints and returns the expected data. |
| **AC‑006** | Refreshing an expired access token with a valid refresh token yields a new access token. |
| **AC‑007** | Logging out clears the authentication cookie and subsequent requests are treated as unauthenticated. |
| **AC‑008** | Password reset flow sends an email, allows setting a new password, and enables login with the new password. |
| **AC‑009** | Email verification link marks the user’s email as verified in Supabase. |
| **AC‑010** | OAuth login (Google/GitHub) creates or links a user and creates a profile row. |
| **AC‑011** | All authentication-related logs contain no plaintext passwords or tokens. |
| **AC‑012** | Unit and integration tests for authentication pass with ≥80% coverage. |
| **AC‑013** | API specification (`docs/API_SPEC.md`) is updated to reflect new endpoints. |
| **AC‑014** | `LOCAL_SETUP.md` includes instructions for configuring Supabase Auth locally (via Supabase CLI or dashboard). |
| **AC‑015** | `context/progress-tracker.md` is updated to mark Phase 1 as completed. |

## 19. Definition of Done
- [x] All user stories (US‑001 … US‑010) are implemented and verified via acceptance criteria.
- [x] Source code follows the project’s coding standards (`docs/CODING_STANDARDS.md`).
- [x] All new and modified files have appropriate license headers (MIT).
- [x] Build passes (`npm run build` in frontend, `pip install -r requirements.txt && pytest` in backend).
- [x] Lint passes (`ruff check backend/`, `npm run lint frontend`).
- [x] Tests pass (backend pytest, frontend Jest) with ≥80% coverage.
- [x] Docker images for backend, frontend, and worker build successfully.
- [x] Docker Compose stack starts, healthchecks pass, and the authentication flow works end‑to‑end.
- [x] GitHub Actions workflow runs on PR and push to main, runs lint, tests, builds images, and reports success/failure.
- [x] Documentation updated: `docs/API_SPEC.md`, `docs/SECURITY.md`, `LOCAL_SETUP.md`, `README.md` (if needed), `context/progress-tracker.md`.
- [x] No `TODO` or `FIXME` comments remain in newly added authentication code.
- [x] No hard‑coded secrets; all configuration via environment variables or secret managers.
- [x] Security review completed: threat modelling, OWASP ASVS Level 2 checklist, dependency scan, and JWT validity verified.
- [x] Performance tested locally: authentication endpoint latency ≤150 ms (average).
- [x] Logging added: auth attempts (success/failure) logged in structured JSON format with timestamp, user_id (hashed if PII), outcome, IP address.
- [x] Error handling: consistent error responses with `error_code`, `message`, and `request_id` (via middleware).
- [x] (Optional) Any feature‑flag or configuration changes are documented and communicated (none for this phase).

--- 

*End of Specification*