# Project Setup and Infrastructure

## Objective
Establish the development environment, CI/CD pipeline, and foundational infrastructure for the AI-Powered Job Finder SaaS project. This includes setting up the repository, Supabase project, Redis, Docker Compose, GitHub Actions, and the initial project structure for frontend and backend.

## Business Value
A solid foundation ensures consistent development, testing, and deployment practices. It enables the team to focus on feature development without worrying about environment inconsistencies, manual setup, or deployment delays. Early investment in CI/CD and infrastructure as code reduces risks and accelerates time-to-market.

## Scope
- Initialize GitHub repository with branch protection (main branch).
- Create a Supabase project with Authentication, Storage, and PostgreSQL (including pgvector extension).
- Set up a Redis instance (using Docker for local development, managed service for production).
- Create a Docker Compose file for local development (backend, frontend, Redis).
- Configure GitHub Actions workflow for CI (lint, testing, building) and CD (staging deployment).
- Establish basic project structure for frontend (Next.js 15 with TypeScript) and backend (FastAPI with Python 3.12).
- Create a README with setup instructions for developers.

## Out of Scope
- Writing any application business logic (authentication, resume handling, job ingestion, etc.).
- Implementing frontend or backend features beyond the basic structure.
- Setting up production hosting (e.g., Render, Railway) – this is covered in later phases.
- Configuring custom domain names or SSL certificates.
- Setting up monitoring tools (Prometheus, Grafana) – these are part of Phase 10.
- Creating detailed API specifications or database schemas – these are covered in later phases.

## Prerequisites
- A GitHub account for repository hosting.
- A Supabase account for the managed backend services.
- A Docker Desktop installation (for local development).
- Node.js (v18 or later) and npm (for frontend development).
- Python (version 3.12) and pip (for backend development).
- An OpenAI API key (for later phases, but not required for setup).
- An Apify API token (for later phases, but not required for setup).

## Dependencies
- None (this is the foundational phase).

## Deliverables
1. GitHub repository initialized with:
   - Main branch protected (requiring pull request reviews).
   - README.md with project overview and setup instructions.
   - .gitignore file for Node.js and Python projects.
2. LOCAL_SETUP.md: A detailed guide for setting up the development environment.
3. Supabase project with:
   - Authentication enabled (email/password, Google, GitHub providers).
   - Storage bucket created for resumes and generated documents.
   - PostgreSQL database with the pgvector extension enabled.
4. Docker Compose file (docker-compose.yml) that defines:
   - A PostgreSQL service (with pgvector and uuid-ossp extensions) for local development (mocking Supabase DB).
   - A Redis service.
   - A backend service (FastAPI) with code mounted for hot reloading.
   - A frontend service (Next.js) with code mounted for hot reloading (optional; can be run host-side).
   - A Mailhog service for email inspection during development.
5. GitHub Actions workflow (/.github/workflows/ci-cd.yml) that:
   - Triggers on push to main and pull requests.
   - Sets up Docker Buildx.
   - Logs into GitHub Container Registry (GHCR) using a token.
   - Builds Docker images for frontend, backend, and worker.
   - Runs unit and integration tests using a test-specific docker-compose.
   - Pushes images to GHCR.
   - Triggers deployment to a staging environment (via webhook or API call).
   - Runs smoke tests against the deployed staging endpoint.
6. Basic project structure:
   - `/frontend`: Next.js 15 TypeScript app (initialized with `npx create-next-app@latest --typescript`).
   - `/backend`: FastAPI application structure (main.py, requirements.txt, Dockerfile).
   - `/worker`: Shared code for Celery tasks (can reuse backend code).
   - Configuration files: tailwind.config.ts, postcss.config.js, tsconfig.json, etc.
7. Environment variable template (.env.example) with placeholder values for:
   - Supabase URL and keys.
   - Redis URL.
   - APIFY API token.
   - OpenAI API key.
   - SMTP variables.
   - Other required variables as per docs/DEPLOYMENT.md.

## Folder Structure
```
job-finder/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── .gitignore
├── docker-compose.yml
├── LOCAL_SETUP.md
├── README.md
├── .env.example
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── public/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/ (if using Alembic for migrations)
├── worker/
│   └── (shared code with backend for Celery tasks)
└── docs/
    └── (existing documentation, not modified in this phase)
```

## Files to Create
1. README.md
2. LOCAL_SETUP.md
3. .gitignore
4. docker-compose.yml
5. .env.example
6. .github/workflows/ci-cd.yml
7. frontend/ (skeleton created by `create-next-app`)
8. backend/ (skeleton with main.py, requirements.txt, Dockerfile)
9. worker/ (placeholder or symlink to backend for shared code)

## Configuration Required
- **GitHub Repository Settings**:
  - Enable branch protection rules for `main` (require pull request reviews, require status checks to pass).
  - Enable GitHub Actions.
  - Set up repository secrets for:
    - `SUPABASE_URL`
    - `SUPABASE_SERVICE_ROLE_KEY`
    - `APIFY_API_TOKEN`
    - `OPENAI_API_KEY`
    - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
    - `GHCR_TOKEN` (for GitHub Container Registry login)
    - `RENDER_HOOK_URL` or similar for deployment trigger (if using Render/Railway).
- **Supabase Project Configuration**:
  - Enable Email and OAuth (Google, GitHub) providers in Authentication settings.
  - Create a storage bucket named `resumes` (private) for storing uploaded resumes.
  - Create a storage bucket named `documents` (private) for generated cover letters and letters.
  - Ensure the `pgvector` extension is enabled in the database (can be done via SQL: `CREATE EXTENSION IF NOT EXISTS vector;`).
  - Ensure the `uuid-ossp` extension is enabled (for UUID generation): `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`.
- **Docker Compose**:
  - Ensure the docker-compose file mounts the local code for backend and frontend (for development hot-reload).
  - Configure the backend service to use the local PostgreSQL (not Supabase) for development.
  - Configure the frontend service to point to the backend via an environment variable (e.g., `NEXT_PUBLIC_API_URL=http://localhost:8000`).

## Environment Variables
The following environment variables are required (as per docs/DEPLOYMENT.md) and should be defined in `.env.example`:
- `NEXT_PUBLIC_API_URL`: Frontend -> Base URL of the backend API.
- `NEXT_PUBLIC_SUPABASE_URL`: Frontend (optional) -> Supabase project URL.
- `SUPABASE_URL`: Backend & Workers -> Supabase project REST endpoint.
- `SUPABASE_ANON_KEY`: Backend (optional) -> Anon public key.
- `SUPABASE_SERVICE_ROLE_KEY`: Backend & Workers -> Secret key with full bypass of RLS.
- `DATABASE_URL`: Backend & Workers -> PostgreSQL connection string.
- `REDIS_URL`: Backend & Workers -> Redis connection.
- `APIFY_API_TOKEN`: Backend -> Token for Apify API.
- `OPENAI_API_KEY`: Backend -> Token for OpenAI API.
- `SMTP_HOST`: Workers (email) -> SMTP server host.
- `SMTP_PORT`: Workers (email) -> SMTP port.
- `SMTP_USER`: Workers (email) -> SMTP username.
- `SMTP_PASS`: Workers (email) -> SMTP password or API key.
- `MAIL_FROM`: Workers (email) -> Sender address.
- `SENTRY_DSN`: (Optional) All -> Error tracking endpoint.
- `LOG_LEVEL`: All -> Logging verbosity (`debug`, `info`, `warn`, `error`).
- `ENVIRONMENT`: All -> Deployment label (`development`, `staging`, `production`).
- `CELERY_BROKER_URL`: Workers -> Usually same as `REDIS_URL`.
- `CELERY_RESULT_BACKEND`: Workers -> Same as broker or separate DB.
- `MAX_CONTENT_LENGTH`: Backend -> Max upload size in bytes (e.g., `5242880` for 5 MB).
- `JWT_ALGORITHM`: Backend -> Algorithm for Supabase JWT verification (`RS256`).
- `JWT_AUDIENCE`: Backend -> Expected `aud` claim (`authenticated`).
- `NEXT_PUBLIC_ENABLE_REALTIME`: Frontend -> Boolean flag for Supabase Realtime.

## Database Requirements
- **Supabase PostgreSQL** (managed) with:
  - `pgvector` extension installed.
  - `uuid-ossp` extension installed.
  - Database named `postgres` (default).
  - Role `postgres` with password (for local Docker Compose, we use a mock DB).
- **Local Development Database** (via Docker Compose):
  - PostgreSQL 15 with `pgvector` and `uuid-ossp` extensions initialized via an init script.
  - Database: `postgres`
  - User: `postgres`
  - Password: `postgres` (or as defined in compose file).
  - Port: 5432 (exposed to host for tooling if needed).

## API Requirements
- None for this phase (no endpoints are implemented yet). The backend will be a placeholder that responds to health checks.

## Frontend Requirements
- A Next.js 15 application with TypeScript, Tailwind CSS, and shadcn/ui configured.
- A placeholder page that displays a welcome message or the project name.
- The frontend should be able to run in development mode (`npm run dev`) and connect to the backend API (once available).

## Backend Requirements
- A FastAPI application with:
  - A single endpoint `/health` that returns `{"status": "ok"}`.
  - Dependency on `asyncpg` or `SQLAlchemy` for database connectivity (to be used in later phases).
  - Dependency on `redis` for caching (to be used in later phases).
  - Basic structure for routers, models, and services (to be expanded in later phases).
- A worker configuration that shares the backend code for Celery tasks.

## Infrastructure Requirements
- Docker Desktop installed locally for running the multi-container development environment.
- GitHub Actions enabled for CI/CD.
- Supabase project created and configured as described.
- Redis accessible via Docker Compose (for development) and a managed service (for production, to be set up later).

## Acceptance Criteria
- [ ] The GitHub repository is initialized with a README, .gitignore, and initial folder structure.
- [ ] LOCAL_SETUP.md provides clear, step-by-step instructions for a new developer to set up the environment.
- [ ] The Supabase project is created with Auth, Storage, and PostgreSQL (pgvector) configured.
- [ ] Docker Compose successfully starts all services (db, redis, backend, frontend, mailhog) and they are healthy.
- [ ] GitHub Actions runs on push to main and passes lint/unit tests.
- [ ] API health endpoint (`/health`) returns 200 OK with `{"status": "ok"}`.
- [ ] Frontend loads and shows a placeholder page at `http://localhost:3000`.

## Test Plan
- **Unit Tests**: Not applicable in this phase (no business logic).
- **Integration Tests**: Validate that Docker Compose services start and can communicate (e.g., backend can connect to Postgres and Redis).
- **End-to-End Smoke Test**: After environment setup, run:
  1. `docker compose up -d` to start services.
  2. Wait for backend to be healthy (curl `http://localhost:8000/health`).
  3. Verify frontend is accessible (curl `http://localhost:3000` returns 200).
  4. Run `docker compose down -v` to clean up.
- **CI/CD Pipeline Test**: Push a commit to a feature branch and ensure the GitHub Actions workflow runs (lint, build, test) and passes on a pull request to main.

## Risks
- **Misconfigured Secrets**: If repository secrets are not set correctly, CI/CD or local development may fail. Mitigation: Document required secrets in LOCAL_SETUP.md and validate early.
- **Docker Compose Conflicts**: Port conflicts on the host machine (e.g., port 8000 already in use). Mitigation: Allow configurable ports via .env or document how to change them.
- **Supabase Setup Errors**: Incorrectly enabling extensions or buckets. Mitigation: Provide step-by-step instructions and verification steps in LOCAL_SETUP.md.
- **Version Drift**: Using outdated Node.js or Python versions leading to compatibility issues. Mitigation: Specify exact versions in documentation and use tools like nvm/pyenv.
- **GitHub Actions Failures**: Due to missing dependencies or incorrect workflow syntax. Mitigation: Validate workflow locally with act or by pushing to a test branch first.

## Rollback Plan
- **Code Rollback**: Since no application code is written yet, rolling back is simply reverting the commits that added the setup files.
- **Infrastructure Rollback**:
  - Docker Compose: Running `docker compose down -v` removes containers and volumes, returning the host to a clean state.
  - Supabase: If a mistake is made in the Supabase project (e.g., wrong bucket settings), you can either delete and recreate the project (acceptable in early setup) or adjust settings via the Supabase dashboard.
  - GitHub Actions: If the workflow is erroneous, revert the workflow file or disable it temporarily.
- **Environment Variables**: If .env.example is committed with real secrets by mistake, immediately rotate those secrets and remove the commit via git history rewrite or contact GitHub support if already pushed.

## Definition of Done
- [x] Build passes (Docker Compose builds images without errors).
- [x] Lint passes (if linting tools are configured in placeholder projects; otherwise, skip).
- [x] Tests pass (the basic health check endpoint returns 200).
- [x] Documentation updated (README.md, LOCAL_SETUP.md, .env.example reflect the setup).
- [x] Progress tracker updated (`context/progress-tracker.md` reflects completed work).
- [x] Architecture unchanged (no existing architecture modified).
- [x] No TODO comments remain in the created setup files.
- [x] No dead or unreachable code in the skeleton projects.
- [x] Security review completed (no hard‑coded secrets in repository; all secrets referenced via environment variables).
- [x] Performance reviewed (containers start within reasonable time; no obvious regressions).
- [x] Logging added (the backend health endpoint logs a simple message; optional but acceptable).
- [x] Error handling implemented (the health endpoint returns appropriate status codes; future endpoints will be handled later).
- [ ] (Optional) Any feature‑flag or configuration changes are documented and communicated (none yet).

## Estimated Effort
20–30 hours (broken into 2‑6 hour units) as outlined in the Build Plan Phase 0.