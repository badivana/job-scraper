# Coding Standards

## Purpose

To establish a consistent, readable, and maintainable codebase across frontend (TypeScript/React/Next.js) and backend (Python/FastAPI) development. Following these standards reduces cognitive friction, facilitates code reviews, and improves long‑term project health.

## Contents

- General Principles
- Repository Organization
- Language‑Specific Guidelines
  - TypeScript / React / Next.js
  - Python / FastAPI
- Styling & CSS
- Database & Migrations
- API Design
- Testing Practices
- Security Considerations
- Tooling & Automation
- Documentation & Comments
- Review Checklist
- References

## General Principles

1. **Clarity over cleverness** – Favor explicit, straightforward code.
2. **Consistency** – Follow the established patterns in the file you are editing.
3. **DRY, but not at the expense of readability** – Extract reusable logic only when it simplifies understanding.
4. **Error handling** – Handle errors explicitly; avoid silent failures.
5. **Security first** – Validate input, encode output, use least privilege.
6. **Performance awareness** – Avoid unnecessary computations in hot paths; leverage caching and async correctly.
7. **Testability** – Write code that is easy to unit‑test (pure functions, dependency injection).
8. **Documentation** – Comment the *why*, not the *what*; keep public APIs documented via docstrings or JSDoc.
9. **Boy Scout Rule** – Leave the code cleaner than you found it.
10. **Zero tolerance for warnings** – Fix linter/type‑checker warnings before submitting.

## Repository Organization

```
/ (root)
├── /app                  # Next.js application (pages, components, hooks, lib, styles)
├── /backend              # FastAPI project (app/, alembic/, tests/)
├── /docker               # Docker‑Compose files, Dockerfiles
├── /docs                 # Documentation (markdown)
├── /scripts              # Helper scripts (db migration, seeding, etc.)
├── /tests                # End‑to‑end (Playwright) and integration tests
├── .github/              # GitHub Actions workflows
├── .husky/               # Git hooks (pre‑commit, pre‑push)
├── .vscode/              # Editor settings (optional)
├── .env.example          # Template for environment variables
├── .gitignore
├── docker-compose.yml
├── package.json
├── requirements.txt
└── README.md
```

### Naming Conventions

- **Directories & files**: `kebab-case` for configs and scripts; `PascalCase` for React components; `snake_case` for Python modules and files.
- **Variables**:
  - `camelCase` in TypeScript/JavaScript.
  - `snake_case` in Python.
- **Constants**: `UPPER_SNAKE_CASE` in both languages.
- **Functions & Methods**: `camelCase` (TS) / `snake_case` (PY).
- **Classes**: `PascalCase`.
- **Types/Interfaces**: `PascalCase` (TS) ; use `TypedDict` or `dataclass` (PY) with `CapWords`.
- **Database tables**: `snake_case`, plural (e.g., `users`, `job_applications`).
- **Columns**: `snake_case`.
- **Indexes**: `idx_<table>_<columns>`.
- **Migrations**: `alembic` revision slugs descriptive (e.g., `add_user_avatar_url`).

## Language‑Specific Guidelines

### TypeScript / React / Next.js

#### File Structure

- **Components**: `src/components/` – each component in its own folder with `index.tsx` and optional `styles.module.css`.
- **Hooks**: `src/hooks/` – custom hooks prefixed with `use`.
- **Utilities**: `src/lib/` – pure functions, API clients, constants.
- **Types**: `src/types/` – shared TS interfaces and types; domain‑specific folders if needed.
- **Styles**: `src/styles/` – global CSS, theme variables, `globals.css`.
- **Pages**: `src/app/` (App Router) – each route a folder with `page.tsx`, optional `layout.tsx`, `loading.tsx`, `error.tsx`.

#### Syntax & Formatting

- Use **ESLint** with plugins:
  - `eslint:recommended`
  - `@typescript-eslint/recommended`
  - `eslint-plugin-react`
  - `eslint-plugin-react-hooks`
  - `eslint-plugin-jsx-a11y`
  - `prettier`
- **Prettier** configuration:
  - Print width: 100
  - Tab width: 2
  - Use tabs: `false`
  - Trailing commas: `es5`
  - Arrow function parentheses: `avoid`
- **Type Strictness**:
  - `"strict": true` in `tsconfig.json`.
  - `"noImplicitAny": true`, `"strictNullChecks": true`.
  - Avoid `any`; use `unknown` when type is truly unknown and then narrow.
- **Imports**:
  - Order: 1) Built‑in/node modules, 2) External libraries, 3) Internal aliases (`@/...`), 4) Relative paths.
  - One import per line; blank line between groups.
  - Use path alias `@/` pointing to `src`.
- **Naming**:
  - Component filenames: `PascalCase.tsx` (e.g., `Button.tsx`).
  - Export default a named component (`export default function Button() {}`).
  - Avoid barrel (`index.ts`) exports unless needed for re‑exports.
- **JSX**:
  - Self‑closing tags when possible.
  - No extra whitespace inside curly braces.
  - Props destructured at top level.
  - Event handlers: `handleClick`, `onChange`.
  - Conditional rendering: prefer ternary or `&&` for simple cases; extract to function for complex logic.
- **State Management**:
  - Prefer React Query for server state.
  - Use `useState`/`useReducer` for local UI state.
  - Avoid prop‑drilling; lift state only when needed; consider Context for truly global state (theme, auth).
- **Styling**:
  - Use **Tailwind** utility classes exclusively; avoid custom CSS unless absolutely necessary (then use CSS modules with scoping).
  - Apply responsive prefixes (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`).
  - Use `dark:` variants if dark mode is ever added.
- **Accessibility (a11y)**:
  - All interactive elements must have an accessible name (`aria-label`, `aria-labelledby`, or native label).
  - Use semantic HTML (`button`, `<a>`, `<input>`, `<select>`, `<textarea>`).
  - Ensure focus order is logical; avoid `tabIndex` > 0 unless unavoidable.
  - Provide sufficient contrast (checked via axe).
  - Respect `prefers-reduced-motion`.
- **Performance**:
  - Lazy‑load routes (`dynamic import` with `next/dynamic`) for heavy pages.
  - Use `next/image` for optimized images.
  - Memoize expensive calculations with `useMemo`.
  - Prevent unnecessary re‑renders with `React.memo` where appropriate.
  - Avoid inline object/function creation in render (`{}` or `() => {}`); prefer `useCallback`/`useMemo`.
- **Error Boundaries**:
  - Provide a global error boundary in `app/layout.tsx` (or a dedicated `ErrorBoundary` component) to catch unexpected errors and show fallback UI.
- **Testing**:
  - Unit tests: Jest + React Testing Library.
  - Test file naming: `Component.test.tsx`.
  - Aim for ≥ 80% line coverage on components.
  - Mock API calls with `MSW` (Mock Service Worker) or `jest.mock`.

### Python / FastAPI

#### File Structure

- **backend/** (or `src/`) containing:
  - `app/` – main package.
    - `__init__.py`
    - `main.py` – FastAPI instance creation, middleware inclusion, router inclusion.
    - `api/` – API routers grouped by version (`v1/`, `v2/`).
      - `v1/`
        - `__init__.py`
        - `routers/` – each resource (`users.py`, `resumes.py`, `jobs.py`, `matching.py`, `ai.py`, `notifications.py`, `admin.py`).
        - `dependencies.py` – reusable `Depends` (db session, auth, rate limiter).
        - `models/` – SQLAlchemy models (`users.py`, `resumes.py`, etc.).
        - `schemas/` – Pydantic v2 models (request/response bodies).
        - `services/` – business logic functions (pure or with db session injected).
        - `utils/` – helpers (token validation, email sending).
    - `core/` – configuration, logging, security, exception handlers.
      - `config.py` – settings via `pydantic.BaseSettings`.
      - `logging.py` – logger configuration.
      - `security.py` – JWT verification and security utilities.
      - `exceptions.py` – custom HTTPException subclasses.
    - `tasks/` – Celery tasks (`tasks.py` or module per domain).
    - `migrations/` – Alembic version scripts.
  - `tests/` – mirrors package structure for unit/integration tests.
  - `alembic.ini` – Alembic configuration.
  - `requirements.txt` – pinned dependencies.
  - `README.md` – service‑specific instructions.

#### Syntax & Formatting

- **Formatter**: `black` line length 88 (default) – enforce via pre‑commit.
- **Linter**: `ruff` (select `I`, `F`, `E`, `W`, `C` rules) + `flake8-bugbear`.
- **Type Checking**: `mypy` strict mode.
  - Enable `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`.
  - Use `# type: ignore` only with a comment explaining why.
- **Imports**:
  - Standard library first, then third‑party, then local application.
  - Blank line between groups.
  - Use explicit imports (`from module import Class`) rather than `import *`.
  - Relative imports within the package (`from .models import User`).
- **Naming**:
  - Functions, variables, attributes: `snake_case`.
  - Classes: `PascalCase`.
  - Constants: `UPPER_SNAKE_CASE`.
  - Private (internal) names: leading single underscore (`_helper`).
- **Docstrings**:
  - Follow **PEP 257** (docstring conventions).
  - Use triple double quotes (`"""`) .
  - For public functions/classes/modules: include a short summary line, blank line, then detailed description.
  - Include `Args:`, `Returns:`, `Raises:` sections as needed.
  - Keep line length ≤ 88.
- **Error Handling**:
  - Raise `HTTPException` from `fastapi` for API errors (status code, detail dict).
  - Define custom exceptions in `core.exceptions.py` for domain‑specific errors.
  - Use `@app.exception_handler` to return consistent JSON error shape.
  - Never let raw exceptions bubble to the client in production (they are caught by global handler).
- **Dependency Injection**:
  - Use FastAPI’s `Depends` for:
    - Database session (`AsyncSession`) – yield from `get_db()`.
    - Current user (`get_current_user`) – validates JWT and returns user model.
    - Rights checks (`require_role`, `require_ownership`).
- **Async / Await**:
  - All I/O bound calls (db, http, redis) must be `await`ed.
  - Avoid blocking calls inside async functions (use `run_in_executor` for CPU‑bound if unavoidable).
- **SQLAlchemy 2.0 Style**:
  - Use Declarative base with `registry`.
  - Prefer `select(`...`).where(...)` for queries.
  - Use `await session.execute(stmt)` and `scalars().first()` etc.
  - Relationships: `relationship(..., lazy="selectin")` for collections; `lazy="joined"` for single‑valued if needed.
- **Pydantic Models**:
  - Use `BaseModel` with `config = ConfigDict(from_attributes=True, str_strip_outer=True, validate_assignment=True)`.
  - Define fields with `Field(..., description="...")`.
  - Use `Annotated` for complex types when needed.
  - For ORM Mode, enable `from_attributes`.
  - Create separate schemas for `Create`, `Update`, `Response` to avoid over‑exposing fields.
- **Validation**:
  - Field‑level validators via `@field_validator`.
  - Root validators via `@model_validator(mode='after')`.
  - Use `Literal` for enums when possible.
- **Routing**:
  - Prefix each router with `/api/v1/{resource}` using `APIRouter`.
  - Define route functions as `async def`.
  - Use `response_model` to declare output schema.
  - Use `status_code` parameter for non‑200 responses (e.g., `status_code=201` for `POST`).
  - Secure routes with `dependencies=[Depends(get_current_user), ...]`.
- **Logging**:
  - Use the logger from `core.logging` (`logger = get_logger(__name__)`).
  - Log at appropriate levels: `debug` (detailed tracing), `info` (business flow), `warning` (unexpected but recoverable), `error` (failed operation), `critical` (system‑level).
  - Never log sensitive data (passwords, tokens, raw PII) – mask or omit.
- **Background Tasks (Celery)**:
  - Define tasks in `tasks/` module.
  - Use `@shared_task` (or `@app.task` if using app instance).
  - Idempotent where possible; accept `kwargs` for flexibility.
  - Log entry/exit with correlation ID if available.
  - Retry policy: `autoretry_for=(Exception,)`, `retry_kwargs={'max_retries': 3}`, `retry_backoff=True`, `retry_jitter=True`.
- **Security**:
  - Passwords hashed using `passlib.context.CryptContext` with `scheme="pbkdf2_sha256"` (or `argon2` if available).
  - JWT verification uses `python-jwt` (`PyJWT`) with the public key from Supabase JWKS; never accept tokens from unverified sources.
  - Ensure CORS middleware restricts origins to known domains.
  - Rate limiting implemented via `slowapi` (limits per IP and per authenticated user).
- **Testing**:
  - Unit tests: `pytest` + `pytest-asyncio`.
  - Mock external services with `asynckmock` or `aioresponses`.
  - Use `factory_boy` for generating model instances (`SQLAlchemyModelFactory`).
  - Test database interactions with an actual PostgreSQL container (via `docker-compose` in CI) or use `sqlalchemy.NullPool` + transaction rollback fixture.
  - Aim for ≥ 80% line coverage; ≥ 90 % on security‑related and mutation endpoints.
  - Run `pytest --cov=app --cov-report=term-missing`.
- **Documentation**:
  - Keep `README.md` up‑to‑date with setup instructions.
  - Inline docstrings for public functions and classes.
  - Use `typer` or similar for CLI scripts if needed.
  - Generate OpenAPI schema automatically; ensure all endpoints have good `summary` and `description`.
  - Consider using `mkdocs` or similar for developer portal if needed.

## Styling & CSS

- **Utility‑First**: Use Tailwind classes exclusively for styling UI components.
- **Avoid custom CSS** unless implementing a complex design token not achievable with utilities (e.g., complex gradients, CSS animations requiring keyframes). If needed, place in `src/styles/` and import globally or via CSS module.
- **Responsive Design**: Apply breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`). Default styles target mobile first.
- **Dark Mode** (if applicable): define `dark:` variants; use `class` strategy.
- **Component Styling**:
  - For shadcn/ui wrappers, extend base classes via `clsx` or `tailwind-merge`.
  - Avoid overriding internal classes that could break updates.
- **CSS Variables** (if needed):
  - Define in `:root` for theme colors, spacing, radii.
  - Access via `var(--var-name)` in CSS or `style={{ '--var': value }}` in JSX.
- **Font Loading**:
  - Use `next/font` to self‑host Google Fonts (e.g., `Inter`) with automatic subsetting.
- **Third‑Party UI Libraries**:
  - If integrating a non‑tailwind component, wrap it in a container that forces your design tokens (e.g., set width, margin, color via tailwind classes on a parent div).

## Database & Migrations

- **Schema Design**:
  - Use **UUID** primary keys (`uuid_generate_v4()`).
  - Store timestamps as `timestamptz` with `DEFAULT now()`.
  - Favor `JSONB` for semi‑structured data (e.g., raw scraped JSON, parsed resume sections).
  - Use `ENUM` (Postgres enum type) for static sets (employment type, contract type) OR lookup tables if the list may evolve.
  - Index foreign key columns (`user_id`, `job_id`, …).
  - Index columns used in `WHERE`, `ORDER BY`, `JOIN` clauses.
  - For vector columns, create `ivfflat` index with appropriate `lists` (start with 100, monitor).
  - Consider `BRIN` indexes on large monotonic columns like `posted_date`.
- **Migrations**:
  - Write migrations that are **backward compatible** whenever possible (add columns with defaults, make columns nullable).
  - For breaking changes (column rename, type change), create a two‑phase deploy:
    1. Add new column, backfill data, keep old column.
    2. Update code to use new column.
    3. Remove old column in later release.
  - Keep migration files small and focused (< 200 lines).
  - Use procedural SQL (`UPDATE … FROM …`) for bulk data changes.
  - Test migration on a copy of production data (via `pg_dump`/`pg_restore`) before applying to prod.
- **Queries**:
  - Prefer ORM for CRUD; use raw SQL (`text()`) only for complex analytics or performance‑critical sections, always with bound parameters.
  - Never concatenate user input into SQL strings.
  - Use `SELECT … FOR UPDATE` when needed for locking rows in transactions.
  - Keep transactions short; commit or rollback promptly.
- **Connection Handling**:
  - Use async engine (`create_async_engine`) with `pool_size=20`, `max_overflow=10`.
  - Dispose of engine on app shutdown.
- **Testing**:
  - Use a separate test database (e.g., suffix `_test`).
  - Rollback transactions after each test or use `SAVEPOINT`.

## API Design

- **RESTful Conventions**:
  - Use nouns for resource names (`/users`, `/resumes/{id}`).
  - HTTP methods map to CRUD:
    - `GET` – retrieve (list or single).
    - `POST` – create.
    - `PUT` / `PATCH` – update (PUT for full replace, PATCH for partial).
    - `DELETE` – remove.
  - Return appropriate status codes:
    - `200` – SUCCESS (GET, PUT, PATCH).
    - `201` – Created (POST).
    - `204` – No Content (DELETE).
    - `400` – Bad Request (validation error).
    - `401` – Unauthorized (missing/invalid token).
    - `403` – Forbidden (authenticated but insufficient rights).
    - `404` – Not Found.
    - `409` – Conflict (e.g., duplicate unique key).
    - `422` – Unprocessable Entity (schema validation errors).
    - `429` – Too Many Requests (rate limit).
    - `500` – Internal Server Error (unexpected).
    - `502` – Bad Gateway (upstream failure).
    - `503` – Service Unavailable (temporary overload).
- **Versioning**:
  - Include version in URL path: `/api/v1/...`.
  - Increment major version for breaking changes.
  - Minor changes (adding optional fields, new endpoints) stay within same version.
  - Deprecate endpoints via `Deprecated` header and provide sunset timeline.
- **Request/Response Body**:
  - Use **JSON** (`application/json`) as the primary format.
  - For file uploads, accept `multipart/form-data`.
  - Responses should follow a consistent envelope:
    ```json
    {
      "data": {/* resource */},
      "meta": {...},   // optional: pagination info, timestamps
      "links": {/* pagination links */} // optional
    }
  - Error responses:
    ```json
    {
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human readable description",
        "details": [{"field": "email", "issue": "must be a valid email"}]
      }
    }
    ```
- **Idempotency**:
  - `PUT` and `DELETE` should be idempotent.
  - For `POST` operations that are not naturally idempotent (e.g., creating a charge), accept an `Idempotency-Key` header and store processed keys temporarily (Redis with TTL) to avoid duplicate processing.
- **Pagination**:
  - Use **cursor‑based** (keyset) pagination for large datasets when possible (`WHERE id > :cursor ORDER BY id LIMIT :limit`).
  - Fall back to offset‑limit for simplicity when dataset size is known to be small (< 10k rows) or when sorting by non‑indexable fields.
  - Return `next_cursor` in `meta` for client to use in next request.
- **Filtering & Searching**:
  - Support query parameters for common filters (`?status=active&role=admin`).
  - For full‑text search, use PostgreSQL `tsvector`/`tsquery` or rely on external search if needed.
  - Provide sensible defaults (e.g., `limit=20`, `offset=0`).
- **Security**:
  - Enforce HTTPS everywhere (`Strict-Transport-Security`).
  - Apply rate limiting per IP and per authenticated user.
  - Validate and sanitize all inputs; never trust client‑side validation.
  - Output JSON with proper `Content-Type`; avoid returning HTML unless intentionally documented.
  - Use `Content-Security-Policy` header to mitigate XSS.
- **Documentation**:
  - Each route function should have a docstring that becomes the OpenAPI description (visible in `/docs`).
  - Use `summary` argument for short title.
  - Tag routers for grouping in Swagger UI (`tags=["users"]`).
  - Mark deprecated endpoints with `deprecated=True`.

## Testing Practices

- **Unit Tests**:
  - Focus on pure functions, service layer logic, validation, and utility helpers.
  - Mock external dependencies (db, HTTP, filesystem).
  - Use `pytest` fixtures for reusable objects (e.g., `client`, `db_session`, `auth_headers`).
  - Test both success and failure paths.
- **Integration Tests**:
  - Spin up a full stack with Docker Compose (db, redis, minio for S3‑mock, smtp mock).
  - Test end‑to‑end API flows: user signup → login → upload resume → list jobs → match → generate cover letter.
  - Use `httpx.AsyncClient` with `app` (FastAPI test client) for in‑process testing when possible, but prefer real services for catching integration bugs.
  - Clean up test data after each run (unique emails, random UUIDs).
- **End‑to‑End (E2E) Tests**:
  - Use **Playwright** (or Cypress) with TypeScript.
  - Test critical user journeys: registration, login, resume upload, job search, apply, notification.
  - Run against a staging‑like environment (separate DB, same config as prod).
  - Include visual regression checks if desired (optional).
- **Performance Tests**:
  - Use **k6** or **Locust** to simulate realistic load (e.g., 500 concurrent users, ramp‑up 5 m).
  - Measure API latency, error rates, queue depths.
  - Define SLA thresholds (p95 < 800 ms, error rate < 1%).
- **Security Tests**:
  - Run **OWASP ZAP** baseline scan against staging.
  - Conduct periodic **penetration testing** (third‑party) for high‑risk areas (auth, payment‑like endpoints, file upload).
  - Check for common vulnerabilities: SQLi, XSS, CSRF (though JWT CSRF not needed if using Authorization header), open redirects, information disclosure.
- **Test Data**:
  - Never use real PII in test suites.
  - Use generated fake data (`faker`, `factory_boy`).
  - Keep test data sets small and deterministic for unit tests.
- **Coverage**:
  - Run `pytest --cov=app --cov-report=html` and ensure required thresholds are met.
  - Block merges if coverage drops below agreed minimum (e.g., 80% overall, 90% on security‑relevant modules).
- **Continuous Integration**:
  - Run the test suite on every pull request.
  - Fail the build on test failures, lint errors, type-checker errors, or security scan failures.

## Security Considerations

- **Authentication**:
  - Verify JWT signature using Supabase JWKS.
  - Enforce expiration (`exp`) and not‑before (`nbf`) claims.
  - Optionally maintain a revocation list (Redis set `revoked_jti:<jti>`) for immediate logout.
  - Use HTTPS only; set `Secure` and `SameSite=Strict` cookies for refresh tokens.
- **Authorization**:
  - Apply RBAC/RLS at the database layer.
  - In endpoint handlers, double‑check that the `sub` claim matches the resource owner (`user_id`).
  - Restrict administrative endpoints to `service_role` or a custom `admin` claim (set via Supabase custom claims if needed).
  - Never trust the client‑provided `user_id`; always derive from the token.
- **Input Validation**:
  - Use Pydantic models to enforce type, length, format, and allowed values.
  - Reject unknown fields (`extra="forbid"`).
  - Sanitize free‑text inputs for XSS (though JSON APIs are less prone, still escape if rendered in HTML).
- **Output Encoding**:
  - JSON responses are automatically safe; if embedding data in HTML templates (e.g., email bodies), use Jinja2 auto‑escape (`{{ user_input | e }}`).
- **Secrets Management**:
  - Never commit secrets to VCS.
  - Use environment variables injected at runtime (Docker‑compose `.env`, platform secret manager, Kubernetes Secrets).
  - Rotate secrets regularly (quarterly or upon incident).
  - For local development, provide `.env.example` with placeholder values.
- **CSRF**:
  - As we rely on `Authorization: Bearer` header, traditional CSRF is not applicable.
  - If using cookie‑based session for any endpoint, enable `CSRFProtect` or `SameSite` attributes.
- **Rate Limiting**:
  - Implement per‑IP (e.g., 60 req/min) and per‑user (e.g., 300 req/min) limits via `slowapi` or custom middleware.
  - Strict limits for expensive endpoints (AI generation: 5 req/min per user).
- **Logging & Monitoring**:
  - Avoid logging passwords, auth tokens, or full request bodies containing PII.
  - Mask sensitive fields (`"*****"`).
  - Monitor for abnormal patterns (brute‑force login attempts, spikes in 401/403).
- **Dependencies**:
  - Keep all dependencies up‑to‑date; use `Dependabot` or `Renovate` for automated PRs.
  - Run `pip-audit` and `safety` in CI.
  - Run `npm audit` for frontend packages.
- **Secure Headers**:
  - Apply via middleware:
    - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `Referrer-Policy: strict-origin-when-cross-origin`
    - `Content-Security-Policy: default-src 'self'; img-src * data:; style-src 'self' 'unsafe-inline';`
- **File Uploads**:
  - Validate MIME type and extension.
  - Limit file size (e.g., 5 MB for resumes, 2 MB for avatars).
  - Scan uploads for malware if integrating with ClamAV or similar (optional in MVP).
  - Store files in a bucket with private ACL; serve via signed URLs with short expiry.
- **Database Security**:
  - Enable RLS on all tables containing user data.
  - Use `service_role` only in trusted backend services.
  - Regularly review `pg_catalog.pg_user` and role permissions.
  - Consider using `pgcrypto` for column‑level encryption if storing highly sensitive data (e.g., SSN) – not required for current scope.

## Tooling & Automation

- **Editors/IDEs**:
  - Recommended: VS Code with extensions:
    - `esbenp.prettier-vscode`
    - `dbaeumer.vscode-eslint`
    - `ms-python.python`
    - `ms-toolsai.jupyter`
    - `bradlc.vscode-tailwindcss`
    - `jeff-hykin/test-explorer-ui`
  - Enable format‑on‑save (Prettier for JS/TS, Black for Python).
- **Pre‑commit Hooks** (via `husky` + `lint-staged`):
  - Run `lint-staged` on staged files:
    - `*.{ts,tsx}` → `eslint --fix` + `prettier --write`
    - `*.py` → `isort` + `black` + `ruff --fix`
    - `*.json` → `prettier --write`
    - `*.md` → `prettier --write`
- **CI`:
  - GitHub Actions workflow runs on every push and PR:
    - `setup-node`, `setup-python`.
    - `npm ci` && `npm run lint` && `npm run test -- --coverage`.
    - `pip install -r requirements.txt` && `pip install -r requirements-test.txt`.
    - `flake8` `.` ; `mypy` `.` ; `pytest` `--cov=app --cov-report=xml`.
    - Build Docker images.
    - Run integration test suite (docker‑compose).
- **Versioning**:
  - Follow **Semantic Versioning** (MAJOR.MINOR.PATCH).
  - Increment `MINOR` for backward‑compatible feature additions.
  - Increment `MAJOR` for breaking changes (API contract, database schema breaking change).
  - `PATCH` for bug fixes and non‑functional improvements.
  - Tag releases in Git (`v1.2.0`).
- **Changelog**:
  - Maintain `CHANGELOG.md` (Keep a Changelog format).
  - Each release entry includes:
    - Added
    - Changed
    - Deprecated
    - Removed
    - Fixed
    - Security
- **Dependency Lock Files**:
  - `package-lock.json` (npm).
  - `requirements.txt` ( pinned via `pip freeze` after resolving with `pip-tools` or manually).
- **Release Process**:
  1. Merge to `main` after approval.
  2. Run CI pipeline (tests, build, scan).
  3. Tag release (`git tag vX.Y.Z && git push --tags`).
  4. CI detects tag → builds Docker images with tag `vX.Y.Z` and pushes.
  5. Deploy to staging (automatic) and/or production (manual trigger).
  6. Write release notes in GitHub using the content from `CHANGELOG.md`.

## Documentation & Comments

- **Docstrings**:
  - Follow language‑specific conventions (PEP 257 for Python, JSDoc/TSDoc for TypeScript).
  - Keep them up‑to‑date when the function signature or behavior changes.
- **Inline Comments**:
  - Use sparingly; prefer expressive variable and function names.
  - When necessary, explain *why* a decision was made, not *what* the code does (the latter should be obvious from code).
  - Use `// TODO:` or `# TODO:` with a ticket reference if applicable (`# TODO: JIRA‑1234: replace with service X`).
- **File Headers**:
  - Not required; rely on VCS for provenance.
  - If used, keep concise: `// @flow` or `# -*- coding: utf-8 -*-`.
- **README**:
  - Must contain:
    - Project overview.
    - Badges (build status, coverage, license).
    - Quick start (prerequisites, `docker compose up`, migrations).
    - API reference link (`/docs`).
    - Contributing guidelines.
    - License.
- **Inline Documentation for APIs**:
  - Each route should have a `summary` and `description` that appear in Swagger UI.
  - Use `response_model` examples and `examples` in `Field` to illustrate payloads.
- **Architecture Docs**:
  - Keep `docs/` directory updated whenever major changes occur (new service, data flow, security mechanism).
  - Link to relevant ADRs (Architecture Decision Records) if adopting that practice.

## Review Checklist (for Pull Requests)

- [ ] Code builds without errors (frontend `npm run build`, backend `python -m py_compile` or `mypy`).
- [ ] No linting errors (`eslint`, `ruff`, `prettier`).
- [ ] Type‑check passes (`tsc --noEmit`, `mypy`).
- [ ] Unit tests pass and coverage does not drop below agreed threshold.
- [ ] No secrets or credentials accidentally added (scan with `git secrets` or `gitlab secrets detection` if configured).
- [ ] All new/modified functions have appropriate docstrings or JSDoc.
- [ ] Follows naming conventions (camelCase/Snake_case/PascalCase as appropriate).
- [ ] Consistent use of tech stack patterns (React hooks, FastAPI dependencies, etc.).
- [ ] Handles edge cases (empty input, malformed data, downstream failure).
- [ ] Includes logging where appropriate (entry/exit of external calls, errors).
- [ ] Respects security considerations (input validation, output encoding, least privilege).
- [ ] Includes tests for new logic (unit, integration, e2e if touching UI).
- [ ] Does not introduce breaking changes without a documented migration plan.
- [ ] Updates relevant documentation (README, API spec, architecture docs) if needed.
- [ ] If UI changes, verify responsiveness and basic accessibility (color contrast, focus outline).
- [ ] If database changes, migration script is present and tested.

## References

- **TypeScript**: https://www.typescriptlang.org/docs/
- **React**: https://react.dev/learn
- **Next.js**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Pydantic**: https://docs.pydantic.dev/
- **Celery**: https://docs.celeryq.dev/
- **Docker**: https://docs.docker.com/
- **GitHub Actions**: https://docs.github.com/en/actions
- **ESLint**: https://eslint.org/
- **Prettier**: https://prettier.io/
- **Black**: https://black.readthedocs.io/
- **Mypy**: https://mypy.readthedocs.io/
- **Ruff**: https://docs.astral.sh/ruff/
- **OWASP ASVS**: https://owasp.org/www-project-application-security-verification-standard/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Supabase Docs**: https://supabase.com/docs
- **Apify Docs**: https://docs.apify.com/
- **OpenAI API**: https://platform.openai.com/docs/api-reference

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*