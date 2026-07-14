# Tech Stack

## Purpose

To document the primary technologies, languages, frameworks, and services used to build, deploy, and operate the AI‑Powered Job Finder platform. This list helps newcomers understand the ecosystem and guides decisions about upgrades or replacements.

## Contents

- Frontend
- Backend
- Infrastructure & Platform Services
- Data Storage & Caching
- Authentication & Authorization
- Background Processing
- External Integrations
- Development & Tooling
- Testing & Quality Assurance
- Observability & Monitoring
- Deployment & CI/CD
- Alternatives Considered

## Frontend

| Layer | Technology | Version (as of 2026‑07) | Notes |
|-------|------------|------------------------|-------|
| Framework | **Next.js** | 15.2.x | React 18, App Router, Server Components, built‑in image optimization, i18n routing. |
| Language | **TypeScript** | 5.4.x | Strict mode enabled; path aliases via `tsconfig.json`. |
| Styling | **Tailwind CSS** | 3.4.x | Utility‑first CSS; customized design tokens via `tailwind.config.js`. |
| Component Primitives | **shadcn/ui** (Radix UI based) | – | Accessible, unstyled components (buttons, dialogs, dropdowns, etc.). |
| Icons | **Heroicons** (outline/solid) | – | Consistent line‑icon set. |
| State Management | **React Query** (TanStack Query) | 5.x | Server‑state caching, background refetch, pagination. |
| Form Handling | **React Hook Form** | 7.x | Minimal re‑renders, Yup/Zod validation. |
| Validation Schema | **Zod** | 3.x | Typesafe schema validation, shared with backend. |
| Routing | **Next.js App Router** | – | File‑system based routing, Route Handlers for API if needed. |
| Internationalization | **next-i18next** | 14.x | Lazy‑loading of locale files, server‑side translation. |
| HTTP Client | **fetch** (native) + **swr** (optional) | – | Wrapper for API calls with automatic retries. |
| Analytics (optional) | **PostHog** or **Plausible** | – | Privacy‑first event tracking. |
| Linting | **ESLint** + **@typescript-eslint** | – | Airbnb base + plugin for React hooks. |
| Code Formatting | **Prettier** | 3.x | Integrated with VS Code, pre‑commit hook. |

## Backend

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| Framework | **FastAPI** | 0.112.x | Async, OpenAPI auto‑generation, Pydantic v2 validation. |
| Language | **Python** | 3.12.x | Official CPython. |
| ASGI Server | **Uvicorn** | 0.30.x | High‑performance async server. |
| ORM / DB Access | **SQLAlchemy** | 2.0.x (async) | Core + AsyncExtension; uses asyncpg driver. |
| Migration Tool | **Alembic** | 1.13.x | Version‑controlled schema migrations. |
| Validation | **Pydantic** | 2.7.x | Data parsing, serialization, models shared with frontend via JSON Schema. |
| Dependency Injection | **built‑in** (via `Depends`) | – | Service‑locator pattern for testability. |
| Background Tasks | **Celery** | 5.4.x | Distributed task queue; broker = Redis; result backend = Redis or DB. |
| Scheduler (beat) | **APScheduler** (integrated) or **Celery Beat** | – | Cron‑like scheduling for scraping, maintenance jobs. |
| HTTP Client | **httpx** (async) | 0.27.x | Calls to Apify, OpenAI, email providers. |
| Secrets Management | **python‑dotenv** (dev) / **AWS Secrets Manager** or **GCP Secret Manager** (prod) | – | Loaded at startup; never hard‑coded. |
| Logging | **structlog** + **python‑json‑logger** | – | JSON structured logs, correlated via request ID. |
| Type Checking | **mypy** | 1.10.x | Strict mode enforced in CI. |
| Linting | **ruff** + **flake8** | – | Fast linting, auto‑fixable rules. |
| Formatting | **black** | 24.x | Consistent code style. |
| API Docs | **Swagger UI** (via FastAPI) + **ReDoc** | – | Available at `/docs` and `/redoc`. |
| Testing Framework | **pytest** + **pytest‑asyncio** | 8.x | Unit, integration, and contract tests. |
| Mocking | **asynckmock** / **aioresponses** | – | Mock external HTTP calls. |
| Factory | **factory_boy** | 3.5.x | Test data generation. |

## Infrastructure & Platform Services

| Service | Provider | Role |
|---------|----------|------|
| **Database** | **Supabase PostgreSQL** (managed) | Primary relational database; includes `pgvector` extension for vector similarity search, `uuid-ossp` for UUID generation, `btree_gin` for JSONB indexing. |
| **Authentication** | **Supabase Auth** | Email/password, OAuth (Google, GitHub, etc.), Magic Link, SSO, MFA, JWT issuance, refresh token rotation, row‑level security (RLS) ready. |
| **Object Storage** | **Supabase Storage** | Secure buckets for resumes, generated documents, avatars, assets; signed URLs for timed access; optional versioning. |
| **Realtime** | **Supabase Realtime** (optional) | WebSocket‑based broadcast for live notifications, chat, presence. |
| **Cache & Message Broker** | **Redis** (managed: RedisCloud, AWS Elasticache, Azure Redis, or self‑hosted) | Stores sessions, rate‑limit counters, Celery broker, transient computation caches (e.g., embeddings). |
| **Search / Vector** | **pgvector** (inside Supabase PostgreSQL) | Stores 1536‑dimensional embeddings for résumés and jobs; IVFFLAT index for ANN queries. |
| **File Processing (Temporary)** | **Local tmpfs** or **AWS S3** (if offloading) | For large file transformations (PDF→text) – streamed to avoid disk pressure. |
| **Email Delivery** | **Third‑Party SMTP/API** (SendGrid, Mailgun, Amazon SES) | Transactional emails (verify, password reset, notifications, weekly digest). |
| **Job Scraping** | **Apify** (Platform‑as‑a‑Service) | Pre‑built actors for LinkedIn, Wellfound, Greenhouse, Lever, Indeed, company pages; pays per successful run. |
| **LLM / Embeddings** | **OpenAI API** | `gpt-4o-mini` (chat/completions) and `text-embedding-3-small` (vectors); monitored for usage & cost. |
| **DNS & Traffic Management** | **Cloudflare** (or equivalent) | SSL/TLS termination, WAF, rate limiting, bot management, optional load balancing. |
| **Observability Backend** | **Prometheus** (metrics), **Grafana** (dashboards), **Loki** or **Elasticsearch** (logs), **Tempo** or **Jaeger** (traces) | Can be self‑managed or hosted services. |

## Data Storage & Caching

| Item | Technology | Details |
|------|------------|---------|
| Primary Datastore | PostgreSQL 15 (via Supabase) | ACID compliant; JSONB columns for semi‑structured data; indexes: B‑tree, GIN, BRIN, ivfflat (pgvector). |
| Secondary Cache | Redis 7 | Strings, hashes, sorted sets, pub/sub; TTL‑based eviction; used for rate limiting, session store (optional), Celery broker, query result caching. |
| Object Store | Supabase Storage | S3‑compatible API; per‑bucket policies; multipart upload support; objects ≤ 5 TB each. |
| Full‑Text Search (optional) | PostgreSQL `tsvector` + `gin` index | For keyword search on title/description/company; combined with vector score via reciprocal rank fusion. |
| Ledger / Audit | Append‑only table + trigger or dedicated extension (pg_audit) | Immutable logs for security and compliance. |

## Authentication & Authorization

- **Auth Provider**: Supabase Auth (handles user signup, login, OAuth, MFA, password reset, email verification).
- **Token Format**: JWT (RS256) signed by Supabase; includes `sub` (user ID), `email`, `role` (`anon`/`authenticated`), `aud`, `exp`, `iat`.
- **Validation**: Verified by backend using Supabase JWKS endpoint (`https://<project>.supabase.co/auth/v1/keys`).
- **RLS**: Enforced on all tables with user‑specific data; bypassed via `service_role` key for backend operations.
- **Roles**: `anon` (public read‑only on jobs, etc.), `authenticated` (full access to own resources), `service_role` (backend, admin tasks). Optional custom `admin` claim for super‑users.
- **Session Handling**: Short‑lived access token (15 min) + rotating refresh token (httpOnly cookie). Refresh token reuse detection.
- **Password Policies**: Enforced by Supabase (min length 12, complexity, rate‑limited login attempts).
- **Account Linking**: Users can associate multiple OAuth providers with same account via Supabase UI.
- **Admin Superuser**: Access via Supabase dashboard or `service_role` for emergency operations.

## Background Processing

- **Task Queue**: Celery 5.x with Redis broker.
  - **Queues**:
    - `job_ingest`: Apify actor invocation, result download, normalization, dedup.
    - `resume_parse`: File upload → text extraction → sectioning → skill embed → store.
    - `embedding_batch`: Periodic recompute of stale embeddings (resumes/jobs).
    - `notification_send`: Email dispatch via SMTP/API.
    - `maintenance`: Index rebuild, log cleanup, temporary file prune.
- **Scheduler**: APScheduler (within FastAPI) or Celery Beat triggers tasks based on cron expressions (stored in `scheduled_tasks` table for persistence).
- **Concurrency**: Number of worker processes set via env var (`CELERY_WORKER_COUNT`); each worker prefetches configurable number of tasks.
- **Idempotency**: Tasks are designed to be safe to retry (e.g., use `ON CONFLICT DO NOTHING` for inserts, check flags before processing).
- **Monitoring**: Celery events → Flower (optional) or Prometheus exporter (`celery-prometheus`).

## External Integrations

| Service | Purpose | Integration Method |
|---------|---------|--------------------|
| **Apify** | Job posting extraction | HTTP API (start actor, poll run, get dataset). Uses API key stored secret. |
| **OpenAI** | Embeddings & text generation (GPT‑4, embeddings) | HTTPS API with Bearer token. Calls wrapped with retry & exponential backoff. |
| **Email Provider** (SendGrid/Mailgun/SES) | Transactional notifications (verification, password reset, weekly digest, application status) | SMTP or HTTP API. |
| **Payment Gateway** (Stripe) – *future* | Subscriptions, invoicing | HTTPS API with webhook for events (invoice.paid, subscription.created). |
| **Analytics** (PostHog/Plausible) | Event tracking | JavaScript snippet (frontend) or server‑side SDK. |
| **Error Tracking** (Sentry) | Exception reporting | DSN configured; captures backend & frontend errors. |
| **Social Login** (Google, GitHub) | Auth alternatives | Handled by Supabase Auth; client‑side redirects. |
| **Webhook Receivers** (optional) | ATS status sync, inbound events | Express endpoint; signature verification (HMAC). |

## Development & Tooling

- **IDE**: VS Code (recommended) with extensions: ESLint, Prettier, Github Copilot, Python, Tailwind CSS IntelliSense, Prisma (if used).
- **Package Managers**:
  - Frontend: `npm` (or `pnpm`/`yarn`).
  - Backend: `pip` with `pip-tools` for locked `requirements.txt`.
- **Version Control**: Git (GitHub). Branching strategy: `main` (release), `dev` (integration), feature branches (`feature/*`), release tags (`vX.Y.Z`).
- **Code Review**: Pull requests required; at least one approval; automated checks (CI) must pass.
- **Pre‑Commit Hooks**: `husky` + `lint‑staged` run lint, format, tests on staged files.
- **Dependency Updates**: `dependabot[bot]` for npm and PyPI; weekly PRs.
- **Documentation**: Markdown in `/docs`; API spec auto‑generated from FastAPI (`/openapi.json`); `mkdocs` or `docusaurus` for public docs (if needed).
- **Project Management**: GitHub Issues + Projects (kanban); milestones aligned with release versions.

## Testing & Quality Assurance

| Type | Tool / Framework | Scope |
|------|------------------|-------|
| Unit | `pytest` + `pytest‑asyncio` | Individual functions, classes, pydantic models. |
| Integration | `pytest` + Docker Compose (services: postgres, redis, mock Apify/OpenAI) | End‑to‑end API flows, worker tasks, Celery integration. |
| Contract | `schemathesis` or `dredd` against OpenAPI spec | Validate API declaration matches implementation. |
| End‑to‑End (E2E) | **Playwright** (or Cypress) | Full UI flows: sign up → upload resume → search jobs → apply → view notifications. |
| Load / Stress | **k6** or **locust** | Simulate 1k–10k virtual users on search, matching, auth endpoints. |
| Security | **bandit** (Python), **semgrep**, **OWASP ZAP** (DAST) | Vulnerability scanning, dependency checks (`pip-audit`, `safety`). |
| Accessibility | **axe-core** (jest‑axe) | Automated a11y checks in CI; manual testing quarterly. |
| Visual Regression | **Chromatic** (if using Storybook) | UI component snapshots. |
| Mutation Testing | **mutmut** (Python) | Ensure test suite effectiveness (optional, run nightly). |
| Test Coverage Goal | ≥ 80 % lines overall; ≥ 90 % on critical paths (auth, payment‑like endpoints, data mutation). | Measured via `pytest --cov`. |

## Observability & Monitoring

- **Metrics**:
  - Exported via `@opentelemetry/instrumentation-fastapi` and `prometheus_fastapi_instrumentator`.
  - Endpoints: `/metrics` (Prometheus scrape).
  - Counters: `http_requests_total`, `http_request_duration_seconds`, `business_event_total` (e.g., resume_uploaded, job_matched, email_sent).
  - Gauges: `queue_length`, `active_connections`, `cache_hit_ratio`.
  - Histograms: `embedding_generation_latency`, `ai_generation_latency`.
- **Logging**:
  - Structured JSON via `structlog`.
  - Fields: `timestamp`, `level`, `logger_name`, `trace_id`, `span_id`, `user_id` (if authenticated), `request_id`, `message`, `error`.
  - Redaction of PII (passwords, tokens, email addresses in non‑auth contexts).
  - Sent to stdout/stderr; collected by container orchestrator and forwarded to Loki/Promtail or Elastic Filebeat.
- **Tracing**:
  - OpenTelemetry SDK automatic instrumentation for FastAPI, sqlalchemy (asyncpg), redis, httpx.
  - Propagation via `traceparent` header (W3C TraceContext).
  - Exported to Tempo or Jaeger via OTLP/HTTP.
- **Alerting** (via Alertmanager or cloud-native equivalents):
  - High error rate (> 5% 5xx/4xx over 5 min).
  - Latency SLA breach (p95 > 800 ms for API).
  - Redis memory > 80%.
  - Celery worker crash loops.
  - Auth failure spike > 10 /min.
  - Disk/Dumbo usage > 85% on any persistent volume.
- **Dashboards** (Grafana):
  - Overview: request rate, error rate, latency.
  - DB: query time, slow queries, replication lag.
  - Redis: hit rate, memory, connected clients.
  - Business: daily active users, matches generated, emails sent.
  - Deployments: version annotation, rollback markers.
- **Log Retention**:
  - Operational: 30 days (hot) + 90 days (cold) via lifecycle policies.
  - Audit logs: 365 days (immutable storage, e.g., WORM bucket or append‑only table with legal hold).
- **Health Checks**:
  - Liveness: `/healthz` (simple process check).
  - Readiness: `/ready` (checks DB connectivity, Redis ping, optional external API ping).

## Deployment & CI/CD

- **Container Images**:
  - Built via Docker Buildx (multi‑platform: linux/amd64, linux/arm64).
  - Tagged with Git SHA (`<repo>:<sha>`) and additionally `latest` for convenience.
  - Stored in GitHub Container Registry (`ghcr.io/<org>/<service>`) or Docker Hub.
- **Continuous Integration** (GitHub Actions):
  - Workflow triggered on `push` to `main` and `pull_request`.
  - Steps: checkout → setup Node & Python → install dependencies → build lint → run unit tests → build Docker images → run integration tests (using docker‑compose test stack) → push images → trigger deployment (via webhook to Render/Railway or kubectl set image) → smoke test.
  - Deployment to staging on every `main` merge; production gated by manual workflow dispatch or tag‑based release.
- **Continuous Deployment**:
  - **Option A – Render/Railway/ Fly.io**:
    - Services configured to auto‑deploy when a new image tag is pushed to the registry (via webhook or integrated registry).
    - Separate services for frontend, backend, worker.
    - Environment variables set in platform UI.
  - **Option B – Kubernetes**:
    - ArgoCD or Flux for GitOps.
    - Helm chart (`charts/jobfinder`) containing Deployments, Services, HorizontalPodAutoscalers, PodDisruptionBudgets, Secrets, ConfigMaps.
    - `helm upgrade --install` on each push to `main` (auto) or on tag (prod).
    - Canary: Deploy to a subset (`canary` label) with weighted routing via Istio/NGINX.
- **Database Migrations**:
  - Run as part of container start‑up (`alembic upgrade head`) *or* as a separate init container/job before launching the app.
  - Migration scripts stored under `alembic/versions/`.
  - Backward‑compatible changes only; breaking changes require two‑phase deploy with feature flag.
- **Configuration Management**:
  - Environment variables injected at runtime (platform’s secret manager or `.env` for local).
  - No configuration stored in image; ensures immutability.
  - Feature flags stored in Supabase table `feature_flags` (key, description, enabled, rollout_percentage) – fetched at startup and cached for short TTL.
- **Rollback Procedure**:
  - Tag-based rollback: redeploy previous image SHA.
  - Database: if migration introduces breaking change, rely on point‑in‑time recovery (PITR) from Supabase (available for paid plans) to restore to pre‑migration state; alternatively, write a reverse migration script.
  - Rollback feature flags: toggle off via Supabase dashboard or API.

## Alternatives Considered (and Why Not Chosen)

| Area | Option Considered | Reason for Rejection |
|------|-------------------|----------------------|
| Database | Self‑hosted PostgreSQL on AWS RDS / Google Cloud SQL | Would require managing backups, patches, scaling, and VPC peering; Supabase offers managed Postgres with built‑in Auth, Storage, Realtime, reducing operational burden. |
| Vector DB | Pinecone, Weaviate, Milvus, Qdrant | Additional service to operate, cost, and data synchronisation overhead. Postgres with pgvector suffices for current scale (≤ 10M vectors) and keeps stack simpler. |
| Auth | Custom JWT + OAuth (via Auth0 / Firebase) | Duplicates effort; Supabase Auth already provides required providers, email/sms, MFA, and integrates tightly with Postgres RLS. |
| Storage | AWS S3 / Google Cloud Storage | Would need separate IAM credentials, CORS setup, and lose the tight integration with Supabase auth (signed URLs can still work but adds another service). |
| Messaging Queue | RabbitMQ / Apache Kafka | More operational complexity; Redis + Celery is sufficient for current task volume and offers low‑latency pub/sub for lightweight events. |
| Search Engine | Elasticsearch / OpenSearch | Overhead of managing a cluster; unnecessary when Postgres + pgvector + tsvector can handle required search/relevance. |
| Backend Framework | Django / NestJS / Express | FastAPI offers superior async performance, automatic OpenAPI, and Pydantic integration; chosen for Python ML‑friendly ecosystem. |
| Frontend Framework | React (CRA) / Vue / Svelte | Next.js provides SSR/SSG, image optimization, and built‑in routing; beneficial for SEO and initial load. |
| Styling | CSS‑modules / Styled Components | Tailwind + shadcn/u offers rapid utility‑based styling with a rich primitive library, reducing CSS footprint. |
| Testing Framework | Jest (frontend) / Mocha (backend) | Preference for pytest (mature, rich plugin ecosystem) and Playwright (modern, reliable) over older stacks. |

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*