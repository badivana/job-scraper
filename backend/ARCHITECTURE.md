# Backend Architecture

## Purpose

To detail the backend architecture of the AI-Powered Job Finder, including its layered structure, components, communication protocols, and integration with Supabase and external services.

## Contents

- Overview
- Layered Architecture
- Core Components
- Data Flow
- Integration Points
- Concurrency & Parallelism
- Error Handling & Logging
- Security Considerations
- Configuration Management
- API Design
- Testing Strategy
- Deployment & Scaling

## Overview

The backend is built with **FastAPI** (Python 3.12) and follows an asynchronous, modular design. It provides the business logic for job ingestion, resume processing, matching, AI generation, notifications, scheduling, and administrative functions. The backend communicates with Supabase (PostgreSQL, Auth, Storage, Realtime), Redis, Apify, and OpenAI.

## Layered Architecture

The backend is organized into the following layers (from top to bottom):

1. **API Layer** – FastAPI routers that expose HTTP/WebSocket endpoints.
2. **Service Layer** – Business logic encapsulated in service classes (e.g., `JobService`, `ResumeService`, `MatchingService`, `AIService`, `NotificationService`).
3. **Data Access Layer** – Repository abstractions that interact with Supabase PostgreSQL using SQLAlchemy ORM (async).
4. **External Integration Layer** – Clients for Apify, OpenAI, email providers, and Redis.
5. **Infrastructure Layer** – Configuration, logging, security, and task queue (Celery) setup.

Each layer depends only on the layer below it, promoting loose coupling and testability.

## Core Components

| Component | Responsibility | Key Technologies |
|-----------|----------------|------------------|
| **API Routers** | Versioned endpoints (`/api/v1/...`) | FastAPI, Pydantic v2 |
| **Service Classes** | Implement use cases (ingest jobs, parse resumes, compute matches, generate text, send notifications) | Python, dependency injection |
| **Repositories** | CRUD operations and complex queries on Supabase tables | SQLAlchemy 2.0 (async), pgvector |
| **Apify Client** | Start actors, monitor runs, download datasets | `httpx.AsyncClient` |
| **OpenAI Client** | Generate embeddings and completions | `httpx.AsyncClient` with API key |
| **Email Client** | Send transactional emails via SMTP or API (SendGrid/Mailgun/SES) | `aiosmtplib` or provider SDK |
| **Redis Client** | Caching, rate limiting, Celery broker, pub/sub | `aioredis` |
| **Celery App** | Background task queues (job_ingest, resume_parse, embedding_batch, notification_send, notification_send, maintenance) | Celery 5.x, Redis broker |
| **Scheduler** (APScheduler/Celery Beat) | Trigger recurring tasks (scraping, maintenance) | APScheduler or Celery Beat |
| **Security Middleware** | JWT validation, rate limiting, CORS, security headers | `PyJWT`, `slowapi`, custom middleware |
| **Logging & Observability** | Structured logs, metrics, tracing | `structlog`, `prometheus_fastapi_instrumentator`, OpenTelemetry |

## Data Flow

1. **Job Ingestion**:
   - Scheduler triggers `job_ingest` Celery task.
   - Task calls Apify to start actor, polls for completion, downloads JSON.
   - Raw JSON stored in `jobs_raw` table.
   - Normalization, deduplication, and insertion into `jobs` table.
   - On insert, a `job_new` Redis event is published; workers generate job embeddings (if not present) and store them.
2. **Resume Upload**:
   - User uploads PDF/DOCX via frontend endpoint.
   - File stored in Supabase Storage bucket `resumes`.
   - Text extracted, sections parsed, skills normalized, embedding generated via OpenAI.
   - Embedding stored in `resumes.skill_vector`; metadata saved in `resumes` table.
   - On upload, a `resume_updated` Redis event may trigger matching refresh.
3. **Matching**:
   - Frontend requests `/matching/{user_id}`.
   - Service fetches user’s resume vector from `resumes`.
   - Queries `jobs` table using pgvector ANN search (`<=>` operator) to get top‑k candidates.
   - Calculates hybrid score (vector similarity + keyword Jaccard + recency decay + location preference).
   - Returns ranked list; results cached in Redis (TTL 5 min).
4. **AI Generation**:
   - Frontend requests `/ai/cover-letter` (or `/ai/cold-email`, `/ai/skill-gap`).
   - Service builds prompt from resume summary and job description (or skill sets) using Jinja2 templates.
   - Calls OpenAI chat/completions endpoint with appropriate temperature and max tokens.
   - Returns generated text; optionally stores a PDF version in Supabase Storage bucket `documents`.
5. **Notifications**:
   - Events (new match, application status change) are published to Redis channels.
   - Celery workers consume channels, render Jinja2 email templates, send via SMTP/API.
   - In‑app notifications are stored in the `notifications` table and/or published via Supabase Realtime.
6. **Scheduler & Maintenance**:
   - APScheduler/Celery Beat runs tasks like nightly embedding recompute, index rebuild, log cleanup.
   - Tasks are idempotent where possible.

## Integration Points

- **Supabase**:
  - PostgreSQL: connection via `DATABASE_URL` (asyncpg driver).
  - Auth: JWT validation using Supabase JWKS (`https://<project>.supabase.co/auth/v1/keys`).
  - Storage: file upload/download using Supabase SDK (or direct REST with `service_role` key).
  - Realtime: optional subscription to channels (e.g., `notifications`) for live updates.
- **Redis**:
  - Connection via `REDIS_URL`.
  - Used as Celery broker (`CELERY_BROKER_URL`) and result backend (`CELERY_RESULT_BACKEND`).
  - Stores caches: user profiles, top‑match lists, API responses, rate‑limit counters.
- **Apify**:
  - HTTP API calls with `APIFY_API_TOKEN`.
  - Actors invoked: LinkedIn, Wellfound, Greenhouse, Lever, Indeed, company career pages.
- **OpenAI**:
  - HTTP API calls with `OPENAI_API_KEY`.
  - Embeddings: `text-embedding-3-small`.
  - Completions: `gpt-4o-mini` (or `gpt-4-turbo`).
- **Email Provider**:
  - SMTP or HTTP API (SendGrid, Mailgun, Amazon SES) using credentials from environment.
- **Frontend**:
  - REST/JSON over HTTPS; CORS restricted to trusted origins.
  - Optional WebSocket/Supabase Realtime for live updates.

## Concurrency & Parallelism

- **Async Request Handling**: All FastAPI endpoint handlers are `async def`, using `await` for I/O (DB, HTTP, Redis).
- **Database**: SQLAlchemy async engine with `asyncpg` driver; connection pool (`size=20`, `max_overflow=10`).
- **Redis**: `aioredis` connection pool; shared across coroutines.
- **External HTTP**: `httpx.AsyncClient` with connection pooling.
- **Celery Workers**: Each worker process runs tasks sequentially; concurrency achieved by multiple worker processes (configured via `CELERY_WORKER_COUNT`).
- **CPU‑Bound Tasks**: Heavy computations (e.g., regex, text parsing) are off‑loaded to Celery workers to avoid blocking the async event loop.
- **Task Idempotency**: Design tasks to be safe to retry (e.g., use `ON CONFLICT DO NOTHING` for inserts, check flags before processing).

## Error Handling & Logging

- **Error Hierarchy**:
  - `BaseAppException` → `HTTPException` → specific subclasses (`ValidationError`, `ExternalServiceError`, `DatabaseError`, etc.).
- **Handlers**: FastAPI exception middleware returns consistent JSON error bodies:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Human readable description",
      "details": [{"field": "email", "issue": "must be a valid email"}]
    }
  }
  ```
- **Logging**:
  - Structured JSON via `structlog` or `python‑json‑logger`.
  - Fields: `timestamp`, `level`, `logger_name`, `trace_id`, `span_id`, `user_id` (if authenticated), `request_id`, `message`, `error`.
  - Sensitive data (passwords, tokens, PII) are redacted (`[REDACTED]`).
  - Logs shipped to stdout/stderr; collected by container orchestrator and forwarded to Loki/Promtail or Elastic Filebeat.
- **Monitoring**:
  - Prometheus metrics: request latency, error rates, queue depths, cache hit/miss, external API latency.
  - Distributed tracing: OpenTelemetry instrumentation for FastAPI, SQLAlchemy, Redis, httpx.
  - Health endpoints: `/healthz` (liveness), `/ready` (readiness checks DB, Redis, optional external API).

## Security Considerations

- **Authentication**:
  - All protected endpoints validate JWT issued by Supabase Auth.
  - RS256 signature verified using Supabase JWKS.
  - Optionally check Redis‑based token revocation list for immediate logout.
- **Authorization**:
  - Service layer checks that the `sub` claim matches resource ownership (e.g., `user_id` on resumes).
  - Administrative endpoints require `service_role` key or a custom `admin` claim (if extended).
  - Row Level Security (RLS) enforced in Supabase for data access control.
- **Input Validation**:
  - Pydantic v2 models validate all incoming data (strict, `extra='forbid'`).
  - Length, format, and range constraints applied.
- **Output Encoding**:
  - JSON responses are safe by default.
  - Email bodies rendered via Jinja2 with auto‑escape enabled.
- **Secrets Management**:
  - No secrets in source code.
  - Supabase `anon` and `service_role` keys, Apify token, OpenAI key, SMTP credentials injected via environment or secret manager.
- **Rate Limiting**:
  - `slowapi.Limiter` with per‑IP (60 req/min) and per‑user (300 req/min) limits; stricter limits for AI endpoints (30 req/min per user).
- **Security Headers**:
  - `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`.

## Configuration Management

- Settings loaded at startup from environment variables (or `.env` for dev) using `pydantic.BaseSettings`.
- Critical secrets must be supplied via environment; never committed.
- Feature flags stored in Supabase table `feature_flags` (key, description, enabled, rollout_percentage) and cached in Redis (TTL 5 min) for fast evaluation.
- Database migrations managed via Alembic (or Supabase Migration CLI); scripts stored in `alembic/versions/`.
- Logging level adjustable via `LOG_LEVEL` (`debug`, `info`, `warn`, `error`).

## API Design

- **Versioning**: All endpoints under `/api/v1/...`; breaking changes increment the version number.
- **RESTful Conventions**:
  - `GET`: retrieve (list or single).
  - `POST`: create.
  - `PATCH`: partial update.
  - `DELETE`: remove.
- **Status Codes**:
  - `200`: success (GET, PATCH).
  - `201`: created (POST).
  - `204`: no content (deleted).
  - `400`: validation error.
  - `401`: missing/invalid token.
  - `403`: insufficient permissions.
  - `404`: not found.
  - `409`: conflict (e.g., duplicate unique key).
  - `422`: schema validation errors.
  - `429`: rate limit exceeded.
  - `500`: internal server error.
  - `502`: bad gateway (external failure).
  - `503`: service unavailable (overload).
- **Error Responses**:
  ```json
  {
    "error": {
      "code": "...",
      "message": "...",
      "details": [...]
    }
  }
  ```
- **Pagination**: Cursor‑based (keyset) preferred for large datasets; fallback to offset‑limit for small sets.
- **Filtering & Searching**:
  - Query parameters for standard filters (`?status=active&location=NY`).
  - Full‑text search via PostgreSQL `tsvector`/`tsquery` (title, description, company, skills).
  - Vector search via pgvector `<=>` operator.
- **Documentation**:
  - Auto‑generated OpenAPI spec available at `/docs` (Swagger UI) and `/redoc` (ReDoc).
  - Each route function includes a docstring that becomes the endpoint description.
  - Tag routers for grouping in Swagger UI (`tags=["jobs"]`).
  - Deprecate endpoints with `Deprecated` header and provide sunset timeline.

## Testing Strategy

- **Unit Tests**:
  - `pytest` + `pytest-asyncio` for async handlers.
  - Mock external dependencies (Apify, OpenAI, Redis) using `asynckmock` or `aioresponses`.
  - Factory Boy for test data.
  - Coverage goal ≥ 80% lines; ≥ 90% on security‑relevant modules.
- **Integration Tests**:
  - Docker‑Compose stack with real PostgreSQL, Redis, and mock external services.
  - Test end‑to‑end API flows: signup → login → upload resume → job search → match → generate cover letter.
- **Contract Tests**:
  - Validate OpenAPI spec using `schemathesis` or `dredd`.
- **Load Tests**:
  - k6 scripts simulating peak load (e.g., 1000 VUs) on search, matching, and auth endpoints.
- **Security Tests**:
  - Bandit and Semgrep for static analysis.
  - OWASP ZAP dynamic scan against staging.
  - Dependency scanning via `pip‑audit` and `safety`.
- **Test Data**:
  - No real PII; use `Faker` and deterministic factory sequences.
  - Clean up after each test (unique emails, random UUIDs).

## Deployment & Scaling

- **Container Image**:
  - Built via Docker (`Dockerfile.backend`).
  - Tagged with Git SHA and pushed to GHCR or Docker Hub.
- **Orchestration**:
  - Kubernetes: Deployment with Horizontal Pod Autoscaler (HPA) based on CPU and custom metrics (queue length via KEDA).
  - Alternative: AWS ECS/Fargate, Google Cloud Run, Azure Container Apps with autoscaling.
- **Autoscaling Triggers**:
  - CPU utilization > 70% (add replica).
  - CPU utilization < 30% (remove replica, min 2).
  - Queue length (`llen job_ingest`, `llen resume_parse`, etc.) > threshold (add workers via KEDA).
  - Latency SLA breach (p95 > 800 ms).
- **Database**:
  - Use Supabase read replicas for read‑heavy workloads (job search, matching, analytics).
  - Monitor replication lag; consider partitioning `jobs` table by `posted_date` for large volumes.
- **Redis**:
  - Use managed Redis (Elasticache, Azure Redis, RedisCloud) or self‑hosted cluster.
  - Scale vertically or horizontally based on memory usage and hit rate.
- **Observability in Production**:
  - Prometheus scrape `/metrics` endpoint.
  - Grafana dashboards for latency, error rates, resource usage, business metrics.
  - Alertmanager rules for critical alerts (high error rate, latency spikes, queue backlog).
- **Rollback Strategy**:
  - Redeploy previous image SHA.
  - For database migrations, rely on Supabase point‑in‑time recovery (PITR) if breaking change; otherwise forward‑only with backward‑compatible migrations.
  - Feature flag kill switch to disable problematic features without redeploy.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*