# GitHub Actions

## Purpose

To define the continuous integration and continuous deployment (CI/CD) workflows that automate building, testing, and delivering the AI-Powered Job Finder application.

## Contents

- Workflow Overview
- Trigger Events
- Jobs and Steps
  - Checkout
  - Setup Node.js
  - Setup Python
  - Install Dependencies
  - Linting
  - Type Checking
  - Unit Tests
  - Security Scans
  - Docker Build
  - Push to Registry
  - Deploy to Staging
  - Deploy to Production (manual)
- Secrets and Environment Variables
- Caching
- Artifacts
- Deployment Strategies
- Customizing the Workflow

## Workflow Overview

The repository uses GitHub Actions to automate the software delivery pipeline. Workflows are defined in `.github/workflows/` and include:

- **ci.yml**: Runs on every push to any branch and on pull requests targeting `main`. Executes linting, type checking, unit tests, and security scans.
- **cd.yml**: Triggers on pushes to `main` (for continuous deployment to staging) and on release tags (for production deployment). Builds Docker images, pushes them to a container registry, and initiates deployment to the target environment.

## Trigger Events

### ci.yml
```yaml
on:
  push:
    branches: ['**']
  pull_request:
    branches: [main]
```

### cd.yml
```yaml
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:   # allows manual triggers
  release:
    types: [published]
```

## Jobs and Steps

Below is a consolidated view of the typical jobs; the actual YAML files may split them differently.

### Checkout
- Uses `actions/checkout@v4` to fetch the repository.
- With `fetch-depth: 0` to obtain full history for versioning.

### Setup Node.js
- Uses `actions/setup-node@v4`.
- Installs the LTS version (e.g., 20.x).
- Enables caching of `node_modules` based on `package-lock.json`.

### Setup Python
- Uses `actions/setup-python@v5`.
- Installs Python 3.12.
- Caches the `pip` download directory via `pip` cache or `actions/cache`.

### Install Dependencies
- **Frontend**: `npm ci` (or `pnpm install --frozen-lockfile`).
- **Backend**: `pip install -r requirements.txt` (and `pip install -r requirements-dev.txt` for test dependencies).

### Linting
- Frontend: `npm run lint` (ESLint + Prettier).
- Backend: `ruff check .` and/or `flake8`.
- Shared: `prettier --check .` (if applicable).

### Type Checking
- Frontend: `npx tsc --noEmit`.
- Backend: `mypy .` or `pyright`.

### Unit Tests
- Frontend: `npm test` (Jest + React Testing Library) with coverage.
- Backend: `pytest` with coverage (`--cov=app --cov-report=xml`).

### Security Scans
- **Dependencies**: `npm audit`, `pip-audit`, `safety check -r requirements.txt`.
- **Code**: `bandit -r . -ll` (Python), `semgrep --config=auto .`.
- **Container** (if applicable): `trivy image` on built Docker images.

### Docker Build
- Uses `docker/build-push-action@v5`.
- Builds multi‑platform images (linux/amd64, linux/arm64) when pushing to a registry.
- Tags:
  - `sha-${{ github.sha }}` (for traceability).
  - `ref-${{ github.ref_name }}` (branch or tag).
  - `latest` (only on `main` for staging).

### Push to Registry
- Requires `REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD` (stored as secrets).
- Pushes only when the workflow is triggered on a `push` to `main` or a `release` event.

### Deploy to Staging
- Triggered automatically on successful `main` build.
- Uses the cluster’s deployment mechanism (e.g., `kubectl set image`, AWS ECS `update-service`, Google Cloud Run `deploy`).
- Deploys the `frontend`, `backend`, and `worker` images with the `sha-${{ github.sha }}` tag.

### Deploy to Production
- Manual trigger (`workflow_dispatch`) or automatic on published release.
- Similar to staging but targets the production environment.
- May include additional steps like database migration validation, smoke tests, and approval gates.

## Secrets and Environment Variables

The following secrets must be configured in the repository settings:

| Secret Name | Description |
|-------------|-------------|
| `REGISTRY_URL` | Container registry hostname (e.g., `ghcr.io` or `index.docker.io`). |
| `REGISTRY_USERNAME` | Username for registry authentication. |
| `REGISTRY_PASSWORD` | Password or personal access token for registry access. |
| `SUPABASE_URL` | Supabase project REST endpoint. |
| `SUPABASE_SERVICE_ROLE_KEY` | Service‑role key for bypassing RLS (backend only). |
| `SUPABASE_ANON_KEY` | Anonymous key (optional, for frontend if needed). |
| `APIFY_API_KEY` | Token for calling Apify API. |
| `OPENAI_API_KEY` | Token for OpenAI API. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` | Email provider credentials. |
| `SENTRY_DSN` *(optional)* | For error tracking. |
| `KUBECONFIG_DATA` *(optional)* | Base64‑encoded kubeconfig for cluster access. |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` *(optional)* | For ECS/EKS deployments. |
| `GCP_SERVICE_ACCOUNT` *(optional)* | JSON key for Google Cloud deployments. |

Environment variables for the application (e.g., `LOG_LEVEL`, `PORT`, `REDIS_URL`) are injected via the deployment manifests or the container’s environment; they are **not** exposed as GitHub Action secrets unless they need to vary between environments.

## Caching

- **Node.js Modules**: Cache based on `package-lock.json` (or `pnpm-lock.yaml`).
- **Python Packages**: Cache based on the hash of `requirements.txt` (or `pyproject.toml`).
- **Docker Layers**: Enable `cache-from` and `cache-to` in `docker/build-push-action` to speed up repeated builds.
- **Build Artifacts**: Persist test reports, coverage reports, and build logs as workflow artifacts for debugging.

## Artifacts

The workflow may upload the following artifacts:
- `test-results.xml` (JUnit‑format) for test reporting.
- `coverage.xml` (Cobertura) for coverage tracking.
- `scan-results.sarif` for security tool output (to enable GitHub code scanning alerts).
- `docker-image-${{ github.sha }}.tar` (if needed for debugging).

## Deployment Strategies

- **Blue/Green**: Deploy the new version to a parallel set of pods/services, switch traffic after health checks.
- **Rolling Update**: Default for Kubernetes Deployments; gradually replaces old pods with new ones.
- **Canary**: Optional advanced strategy using Istio/Flagger or AWS CodeDeploy for gradual rollout.
- **Feature Flags**: Used in conjunction with deployments to enable/disable functionality without redeploying.

## Customizing the Workflow

To adjust the pipeline:
- Edit the relevant YAML files in `.github/workflows/`.
- Modify the `jobs.` sections to add, remove, or reorder steps.
- Change the `if:` conditions to control when specific jobs run (e.g., only run security scans on `main`).
- Update the container registry URL and authentication method if switching providers.
- For enterprise proxies, ensure that `http_proxy`/`https_proxy` environment variables are set in the job containers.

## Best Practices

- Keep workflows **idempotent** where possible.
- Fail fast: order steps so that inexpensive checks (lint, type) run before expensive ones (tests, builds).
- Use **concurrency** to cancel outdated runs when a new push occurs on the same branch.
- Protect the `main` branch with required status checks and review requirements.
- Regularly audit the least‑privilege nature of the tokens used in secrets.
- Archive old workflow logs and artifacts to stay within storage limits.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*