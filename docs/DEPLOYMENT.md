# Deployment

## Purpose

To outline how to deploy the AI‑Powered Job Finder application across development, staging, and production environments. The deployment model uses Docker containers for the frontend and backend, Supabase for managed PostgreSQL, Auth, and Storage, Redis for caching and queueing, and GitHub Actions for CI/CD. The platform can be hosted on services like Railway, Render, or any Docker‑compatible infrastructure (including Kubernetes).

## Contents

- Overview
- Architecture Diagram
- Environment Variables
- Local Development (Docker‑Compose)
- Production Deployment (Docker + Host Platform)
- CI/CD Pipeline
- Configuration Management
- Scaling & Observability
- Backup & Disaster Recovery
- Rollback Strategy
- Environment Specifics (Dev / Staging / Prod)

## Overview

The system consists of three primary deployable components:

1. **Frontend** – Next.js 15 app (React + TypeScript) served as static assets or via a Node server.
2. **Backend** – FastAPI application (Python 3.12) exposing the REST/WebSocket API.
3. **Infrastructure Services** – Provided by Supabase (PostgreSQL with pgvector, Auth, Storage, Realtime) and a separate Redis instance (managed or self‑hosted).

All components are containerized, enabling consistent execution from a developer’s laptop to cloud providers.

## Architecture Diagram (textual)

```
[User Browser]
        |
        | HTTPS
        v
+------------------+      +------------------+
|   CDN / Edge     |<---->|   Next.js Frontend|
| (Vercel/Netlify) |      +------------------+
+------------------+             |
        | HTTPS (API)            |
        v                        v
+------------------+      +------------------+
|  API Gateway /   |      |   FastAPI Backend|
|  Load Balancer   |      +------------------+
+------------------+             |
        | gRPC/HTTP (internal)   |
        v                        v
+------------------+      +------------------+      +------------------+
|   Redis (Cache   |      |  Supabase        |      |  Supabase Auth   |
|   & Broker)      |      |  PostgreSQL +    |      |  (managed)       |
+------------------+      |   pgvector,      |      +------------------+
                          |   Storage,       |
                          +------------------+
                          |  Supabase Realtime|
                          +------------------+

External Services:
- Apify (HTTP) -> Backend (job ingestion)
- OpenAI (HTTP) -> Backend (AI embeddings/generation)
- Email Provider (SMTP/API) -> Background Workers (notifications)
```

## Environment Variables

The following variables are required for both frontend and backend (where applicable). They should be injected via the hosting platform’s settings or a `.env` file (never committed).

| Variable | Scope | Description | Example |
|----------|-------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Frontend | Base URL of the backend API (used by browser). | `https://api.jobfinder.example.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend (optional) | If using Supabase client directly (e.g., for auth UI). | `https://xyzcompany.supabase.co` |
| `SUPABASE_URL` | Backend & Workers | Supabase project REST endpoint. | `https://xyzcompany.supabase.co` |
| `SUPABASE_ANON_KEY` | Backend (optional) | Anon public key for client‑side flows (if needed). | `anon-…` |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend & Workers | Secret key with full bypass of RLS (used by backend). | `service_role-…` |
| `POSTGRES_PRISMA_URL` *(if using Prisma)* | Backend | Optional; not needed if using raw SQL/asyncpg. |
| `DATABASE_URL` | Backend & Workers | PostgreSQL connection string (provided by Supabase). Constructed as `postgresql://postgres.[password]@db.xyz.supabase.co:5432/postgres`. | `postgresql://postgres:mysecretpassword@db.xyzcompany.supabase.co:5432/postgres` |
| `REDIS_URL` | Backend & Workers | Redis connection (e.g., `redis://:password@host:6379/0`). | `redis://:redispass@redis-xyz.render.com:6379/0` |
| `APIFY_API_TOKEN` | Backend | Token for calling Apify API. | `apify_api_…` |
| `OPENAI_API_KEY` | Backend | Token for OpenAI API. | `sk-…` |
| `SMTP_HOST` | Workers (email) | SMTP server host. | `smtp.sendgrid.net` |
| `SMTP_PORT` | Workers (email) | SMTP port (usually 587). | `587` |
| `SMTP_USER` | Workers (email) | SMTP username. | `apikey` |
| `SMTP_PASS` | Workers (email) | SMTP password or API key. | `SG.xxxx` |
| `MAIL_FROM` | Workers (email) | Sender address. | `no-reply@jobfinder.example.com` |
| `SENTRY_DSN` *(optional)* | All | Error tracking endpoint. | `https://xxxx@o1.ingest.sentry.io/123456` |
| `LOG_LEVEL` | All | Logging verbosity (`debug`, `info`, `warn`, `error`). | `info` |
| `ENVIRONMENT` | All | Deployment label (`development`, `staging`, `production`). | `production` |
| `CELERY_BROKER_URL` | Workers | Usually same as `REDIS_URL`. | `redis://…` |
| `CELERY_RESULT_BACKEND` | Workers | Same as broker or a separate DB. | `db+postgresql://…` |
| `MAX_CONTENT_LENGTH` | Backend | Max upload size in bytes (e.g., `5242880` for 5 MB). | `5242880` |
| `JWT_ALGORITHM` | Backend | Algorithm used to verify Supabase JWT (`RS256`). | `RS256` |
| `JWT_AUDIENCE` | Backend | Expected `aud` claim (usually `authenticated`). | `authenticated` |
| `NEXT_PUBLIC_ENABLE_REALTIME` | Frontend | Boolean flag to enable Supabase Realtime subscription. | `true` |

*Note*: Never commit actual values; use placeholder or rely on platform secret injection.

## Local Development (Docker‑Compose)

A `docker-compose.yml` is provided for quick local setup. It spins up:

- `db`: PostgreSQL 15 with `pgvector` and `uuid-ossp` extensions (mock Supabase DB).
- `redis`: Redis 7.
- `backend`: FastAPI service (code mounted with hot reload).
- `frontend`: Next.js dev server (optional; can also run `npm run dev` host‑side for faster refresh).
- `worker`: Celery worker (shared code with backend).
- `mailhog`: Dummy SMTP server for inspecting emails.

### Steps

1. Clone repository.
2. Copy `.env.example` to `.env` and fill in dummy values (or leave empty for DB defaults).
3. Run `docker compose up --build`.
4. Initialize the database:
   ```bash
   docker exec -it jobfinder_db_1 psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS uuid-ossp; CREATE EXTENSION IF NOT EXISTS pgvector;"
   ```
   (The `docker-compose.yml` already includes these extensions via an init script.)
5. Run migrations (if using Alembic):
   ```bash
   docker exec -it jobfinder_backend_1 alembic upgrade head
   ```
6. Open `http://localhost:3000` for frontend, `http://localhost:8000` for backend API docs.

### Commands

- `docker compose ps` – list containers.
- `docker compose logs -f backend` – follow backend logs.
- `docker compose exec backend pytest` – run test suite.
- `docker compose down -v` – stop and remove volumes.

## Production Deployment (Docker + Host Platform)

### Option A: Render (or Railway, Fly.io, etc.)

Both platforms support deploying Docker containers from a Git repository.

#### Steps (Render example)

1. **Create Services**:
   - **Web Service** (Backend): Dockerfile from `./Dockerfile.backend`.
   - **Web Service** (Frontend): Use static site build (if using Vercel/Netlify) **or** a Dockerfile that builds the Next.js app and serves via `next start`.
   - **Background Worker** (Optional): Another web service using the same image but with command `celery -A app.worker worker`.
   - **PostgreSQL**: Use Render’s managed PostgreSQL (or connect to external Supabase).
   - **Redis**: Use Render’s managed Redis (or external).

2. **Attach Environment Variables** as per the table above (set via platform UI).

3. **Enable Auto‑Deploy** from GitHub branch (main).

4. **Health Checks**:
   - Backend: `GET /health` (returns 200).
   - Frontend: root path.

#### Dockerfile (backend)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non‑root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile (frontend)

```dockerfile
# Base image with Node
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build   # outputs to .next

# Production image
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js .
COPY --from=builder /app/public ./public

ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "node_modules/next/dist/server/start.js"]
```

#### Dockerfile (worker) – reuse backend image, override command:

```dockerfile
# Use same backend image
FROM <backend-image-name>
CMD ["celiah", "-A", "app.worker", "worker", "--loglevel", "info"]
```

### Option B: Kubernetes (EKS/GKE/AKS)

If you prefer full orchestration, you can deploy using Helm charts or plain manifests:

- **Namespace**: `jobfinder`
- **Deployments**:
  - `frontend` (replicas 2‑4, autoscaling by CPU).
  - `backend` (replicas 2‑4, autoscaling by CPU & queue length via KEDA).
  - `worker` (replicas 2‑6, scaled by Redis queue length via KEDA).
- **StatefulSets**:
  - `redis` (if self‑managed) – or use managed Elasticache/Azure Redis.
- **External Services**:
  - `Secret` for Supabase keys, OpenAI token, Apify token.
  - `ConfigMap` for non‑secret env vars.
- **Ingress**: NGINX‑Ingress or Cloud Load Balancer terminates TLS and routes `/api/*` to backend, `/_next/*` and static to frontend.
- **Horizontal Pod Autoscaler (HPA)** for CPU; **KEDA** for event‑driven scaling (Celery).
- **PodDisruptionBudgets** to maintain availability during node drains.
- **PersistentVolumeClaims** not required (stateless); persistence handled by Supabase and Redis.

### Option C: Vercel/Netlify + Separate Backend

- Deploy frontend to Vercel/Netlify (automatic builds from `main` branch).
- Deploy backend as a Docker service on Render/Fly.io or a VPS.
- Set `NEXT_PUBLIC_API_URL` to the backend URL.

## CI/CD Pipeline (GitHub Actions)

We maintain a workflow that:

1. **Triggers** on push to `main` and on pull requests.
2. **Steps**:
   - Checkout code.
   - Set up Docker Buildx (multi‑arch).
   - Log in to Docker Registry (GHCR or Docker Hub) using secrets.
   - Build three images: `frontend`, `backend`, `worker`.
   - Run unit & integration tests inside a temporary container (using `docker compose` with test overrides).
   - Push images to registry.
   - Trigger deployment:
     - For Render/Railway: via webhook or API call (using stored tokens).
     - For Kubernetes: `kubectl set image` or Helm upgrade.
   - Run smoke tests against the deployed endpoint (health check, auth login, sample search).
   - Notify Slack on success/failure.

### Sample Workflow Snippet (simplified)

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
      - ... similar for frontend and worker ...
      - name: Run tests
        run: |
          docker compose -f docker-compose.test.yml up --abort-on-container-exit
      - name: Deploy to Render
        if: github.ref == 'refs/heads/main'
        run: |
          curl -X POST $RENDER_HOOK_URL   # webhook provided by Render
      - name: Smoke test
        run: |
          curl -sf https://api.jobfinder.example.com/health || exit 1
          curl -sf https://jobfinder.example.com   # frontend
```

## Configuration Management

- **Immutable Infrastructure**: Container images are versioned by Git SHA; tags never change.
- **Feature Flags**: Optional use of LaunchDarkly or home‑grown JSON stored in Supabase (`feature_flags` table) to enable/disable features without redeploy.
- **Database Migrations**:
  - Use Alembic (if adopting) or Supabase Migration API.
  - Migrations run as part of the bootstrap script in the container start‑up (or as a separate release step).
  - Backward‑compatible changes only; breaking changes require a two‑phase deploy.
- **Secret Rotation**:
  - Automated via cloud provider secret rotation (e.g., AWS Secrets Manager Lambda rotation) or manual quarterly process.
  - Application picks up latest values on restart (or via side‑car agent like `envconsul`).

## Scaling & Observability

- **Horizontal Pod Autoscaler (HPA)**: Scale `backend` and `frontend` based on CPU utilization (>70 %).
- **KEDA for Workers**: Scale based on Redis queue length (`llen celery`).
- **Autoscaling Rules**:
  - Scale out: if average CPU > 70 % for 2 min → add 1 replica.
  - Scale in: if average CPU < 30 % for 5 min → remove 1 replica (min 2).
- **Load Testing**: Use k6 or Locust to validate scaling policies before peak events.
- **Distributed Tracing**:
  - Instrument OpenTelemetry in FastAPI and Next.js (via `@opentelemetry/api`).
  - Export to Jaeger/Tempo via OTLP gateway.
- **Metrics**:
  - Prometheus scrapes `/metrics` endpoint (exposed by `prometheus-fastapi-instrumentator`).
  - Grafana dashboards for request latency, error rates, queue depth, cache hit ratio.

## Backup & Disaster Recovery

- **Supabase Managed Backups**:
  - Point‑in‑time recovery (PITR) enabled; retain daily backups for 30 days, weekly for 90 days.
  - Manual snapshots can be taken via Supabase dashboard.
- **Redis Backup**:
  - If using self‑hosted Redis, enable AOF and RDS snapshots; ship to S3.
  - If managed (e.g., RedisCloud), rely on provider backups.
- **Object Storage (Supabase Storage)**:
  - Versioning can be enabled (if supported) for critical buckets (`resumes`, `documents`).
  - Replicate to a secondary bucket via lifecycle rules or manual sync (rclone) for DR.
- **Disaster Recovery Steps**:
  1. Failover to secondary region (if multi‑region Supabase is configured).
  2. Point DNS to standby frontend/backend endpoints.
  3. Recreate worker nodes.
  4. Validate data integrity via checksum sample.
  4. Resume traffic after smoke tests.

## Rollback Strategy

- **Image Rollback**: Since each deployment tags images with Git SHA, rolling back is as simple as redeploying the previous SHA.
- **Database Rollback**: For backward‑compatible migrations, forward‑only is safe. For breaking changes, maintain a migration script that can revert (or rely on PITR to restore to pre‑migration point).
- **Feature Flag Kill Switch**: If a new feature causes issues, toggle off via Supabase `feature_flags` table or config map without redeploy.

## Environment Specifics

| Setting | Development | Staging | Production |
|---------|-------------|---------|------------|
| `LOG_LEVEL` | `debug` | `info` | `warn` |
| `ENVIRONMENT` | `development` | `staging` | `production` |
| `CACHE_TTL` | 60s | 300s | 600s |
| `RATE_LIMIT_PER_USER` | 1000/min | 200/min | 100/min |
| `ENABLE_DEBUG_ENDPOINTS` | true | false | false |
| `USE_MOCK_APIS` (Apify/OpenAI) | true (optional) | false | false |
| `SMTP` | Mailhog | Real (sandbox) | Real (production) |
| `ALLOWED_ORIGINS` (CORS) | `http://localhost:3000` | `https://staging.jobfinder.example.com` | `https://jobfinder.example.com` |
| `SOURCE` (Apify webhook secret) | test secret | staging secret | production secret |

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*