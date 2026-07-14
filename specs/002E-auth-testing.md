# 002E-auth-testing.md

## Objective
Provide a comprehensive testing strategy for the authentication system, covering unit, integration, and end‑to‑end tests for both the FastAPI backend and the Next.js frontend. The goal is to achieve ≥80 % coverage of authentication‑related code and to verify that all acceptance criteria from the specification are metaspec are satisfied.

## Scope
- **Backend tests** (Python, pytest):
  - Unit tests for JWT verification utilities (`app/core/security.py`).
  - Unit tests for the authentication middleware (`app/middleware/auth_middleware.py`).
  - Integration tests for the Auth API endpoints (`/auth/register`, `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/reset-password`, `/auth/verify-email`, `/auth/me`) using `httpx.AsyncClient` against the FastAPI app.
  - Tests for edge cases: expired tokens, malformed tokens, missing Authorization header, duplicate email sign‑up, wrong password, etc.
  - Mocking of Supabase interactions (JWKS fetch, auth client) using the `responses` library or `unittest.mock`.
  - Tests that the profile row is created upon successful registration (via DB trigger or explicit backend call) – can be done with a test database.
- **Frontend tests** (JavaScript/TypeScript, Jest + React Testing Library):
  - Unit test for `lib/supabaseClient.js` (singleton creation).
  - Unit test for middleware (`middleware.ts`) simulating request with/without cookie and asserting redirect behavior.
  - Tests for login page (`pages/login.tsx`): form submission with mock `supabase.auth.signInWithPassword`, verifying redirect on success and error message on failure.
  - Tests for registration page (if implemented).
  - Test for logout API route or client‑side logout function.
  - (Optional) Snapshot test for protected page that redirects when unauthenticated.
- **End‑to‑end tests** (optional but recommended) using Cypress or Playwright:
  - Scenario: visit `/register`, fill valid data, submit, check for verification email simulation (or mock), then login with same credentials, access a protected page, logout, assert redirect to login.
  - Can be run against a docker‑compose stack with a mock email service (e.g., Mailhog).
- **Test data & fixtures**:
  - Use a separate test database (e.g., `postgres_test`) spun up via `docker-compose.test.yml` or via `pg_isready` in CI.
  - For backend tests, override `DATABASE_URL` environment variable to point to the test DB.
- **Continuous Integration**:
  - Add steps in `.github/workflows/ci-cd.yml` to:
    - Install Python test dependencies (`pytest`, `pytest-asyncio`, `httpx`, `responses`).
    - Run `pytest` against the backend.
    - Install frontend test dependencies (if not already) and run `npm test`.
    - Optionally run Cypress tests (if added) against a docker‑compose environment.
  - Ensure test coverage reporting (e.g., `pytest --cov=app --cov-report=term-missing`) and enforce a threshold (≥80 %).
- **Documentation**:
  - Update `docs/TESTING_STRATEGY.md` to mention authentication test suite.
  - Mention in `LOCAL_SETUP.md` how to run tests locally (`make test` or explicit commands).

## Deliverables
1. **Backend test files** under `backend/tests/`:
   - `test_security.py`
   - `test_auth_middleware.py`
   - `test_auth_routes.py`
   - `conftest.py` (fixtures for test client, test DB override, Supabase mock).
2. **Frontend test files** under `frontend/src/__tests__/` (or `__tests__` at root):
   - `supabaseClient.test.ts`
   - `middleware.test.ts`
   - `login.test.tsx`
   - `register.test.tsx` (if applicable)
   - `logout.test.tsx` (if applicable)
   - `protectedPage.test.tsx` (optional)
3. **Cypress (or Playwright) test folder** `cypress/e2e/auth.cy.js` (optional) – include if the team decides to adopt E2E.
4. **Updated CI workflow** (add steps for installing test dependencies, running tests, collecting coverage).
5. **Updated documentation**:
   - `docs/TESTING_STRATEGY.md` – add section “Authentication testing”.
   - `LOCAL_SETUP.md` – section “Running tests”.
   - `README.md` – possibly reference testing commands.
6. **Coverage badge** (optional) added to README.

## Acceptance Criteria (Test‑Specific)
- [ ] All unit tests pass locally and in CI.
- [ ] Integration tests for each auth endpoint pass, covering success and failure paths.
- [ ] Mocked Supabase calls do not hit real external services during unit tests.
- [ ] Backend test coverage for authentication‑related modules ≥80 %.
- [ ] Frontend test coverage for authentication‑related components ≥80 %.
- [ ] End‑to‑end test (if added) validates a full sign‑up → login → access protected resource → logout flow.
- [ ] CI pipeline fails if any test fails or if coverage drops below the threshold.
- [ ] No test contains hard‑coded real secrets; all configuration uses environment variables or mocks.
- [ ] Test execution time reasonable (<2 minutes for unit/integration; optional E2E may be longer but still acceptable in CI).

## Estimated Effort
4‑5 hours (writing backend unit+integration tests, frontend unit tests, updating CI and docs).

## Dependencies
- Phase 0 (Docker Compose, GitHub Actions CI skeleton).
- 002A‑supabase‑auth.md (Supabase configured, providing JWKS endpoint).
- 002B‑backend‑auth.md (actual implementation to be tested).
- 002C‑frontend‑auth.md (frontend implementation to be tested).
- 002D‑profile‑bootstrap.md (db schema; tests verify trigger works).

---