# Component Diagram

## Purpose

To illustrate the major logical components of the AI-Powered Job Finder system and their interconnections, highlighting how the frontend, backend services, infrastructure, and third‑party APIs collaborate to deliver the product’s functionality.

## Contents

- Overview
- Components
- Inter‑Component Communication
- Data Flow Summary
- Deployment View Relation

## Overview

The system is composed of loosely coupled components that communicate via well‑defined protocols (HTTP/HTTPS, WebSocket, Redis pub/sub, database connections). This diagram shows the *logical* boundaries; the physical deployment may containerize or manage some components as managed services.

## Components

| Component | Responsibility | Technology / Notes |
|-----------|----------------|--------------------|
| **Frontend (SPA)** | User interface: authentication, profile, resume upload, job search & matching, application tracking, AI generators, notifications, settings. | Next.js 15, React 18, TypeScript, Tailwind CSS, shadcn/ui. Communicates with backend via REST/JSON (and optional WebSocket for realtime updates). |
| **API Gateway (Optional)** | Edge termination, TLS, rate limiting, request routing, basic auth placeholder. | NGINX, Traefik, or cloud load balancer; can be omitted if the backend is directly exposed. |
| **Backend API (FastAPI)** | Core business logic: job ingestion, resume processing, matching, AI generation, notification handling, scheduling, admin functions. | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Celery. |
| **Supabase** | Managed backend‑as‑a‑service providing: <br>• PostgreSQL (with pgvector, uuid‑ossp, btree_gin) <br>• Auth (email/pass, OAuth, MFA, JWT) <br>• Storage (buckets for resumes, generated documents, avatars) <br>• Realtime (optional WebSocket feed) <br>• Dashboard, SQL editor, auto‑generated REST/PostgREST APIs. | Hosted service; connection via standard PostgreSQL lib and REST endpoints. |
| **Redis** | In‑memory data store used for: <br>• Celery broker and result backend <br>• Session cache (optional) <br>• Rate‑limiting counters <br>• Top‑match caching per user <br>• Pub/sub channels for events (job_new, resume_updated, notification_send, etc.). | Self‑managed or managed (AWS Elasticache, Azure Redis, RedisCloud). |
| **Celery Workers** | Background, long‑running or asynchronous tasks: <br>• Job ingestion (call Apify, normalize, dedup) <br>• Resume parse & embedding <br>• Embedding batch recompute (nightly) <br>• Notification dispatch (SMTP/API) <br>• Maintenance (index rebuild, log cleanup). | Python, Celery 5.x, concurrency via worker processes. |
| **Apify** | Cloud‑based web‑scraping platform providing pre‑built actors for LinkedIn, Wellfound, Greenhouse, Lever, Indeed, company career pages, etc. | HTTP API; API key stored secret. |
| **OpenAI** | Provider of large language models and embedding models used for: <br>• Resume & job embedding (text‑embedding‑3‑small) <br>• Generative text (cover letter, cold email, skill‑gap analysis) via gpt‑4o‑mini or gpt‑4‑turbo. | HTTPS API; API key stored secret. |
| **Email Provider** | Sends transactional emails: verification, password reset, welcome, weekly digest, notifications. | SMTP (Mailhog in dev) or HTTP API (SendGrid, Mailgun, Amazon SES). |
| **Admin Dashboard (Optional)** | Internal tool for platform operators: view metrics, manage users, trigger scrapes, monitor queues. | Could be a separate Next.js route protected by admin role, using the same backend API. |
| **Monitoring & Observability Stack** (external to core but tightly integrated): <br>• Prometheus (metrics scraping) <br>• Grafana (dashboards) <br>• Loki / Elasticsearch (logs) <br>• Tempo / Jaeger (traces) <br>• Alertmanager (alert routing). | OpenTelemetry instrumentation in frontend/backend. |

## Inter‑Component Communication

- **Frontend ↔ Backend**: HTTPS JSON REST (`/api/v1/...`); optional WebSocket (`/ws/notifications`) via Supabase Realtime or custom endpoint.
- **Backend ↔ Supabase**:
  - PostgreSQL via asyncpg (DATABASE_URL) for CRUD, pgvector queries.
  - Auth: JWT validation using JWKS endpoint (`https://<project>.supabase.co/auth/v1/keys`).
  - Storage: Supabase SDK (or direct HTTP with service_role key) for upload/download of blobs.
  - Realtime: optional subscription to broadcast new matches, notifications, or chat.
- **Backend ↔ Redis**:
  - Standard Redis protocol (via aioredis/lredis) for get/set, pub/sub, blocking pop (Celery broker).
- **Backend ↔ Celery**:
  - Workers read tasks from Redis broker (`CELERY_BROKER_URL`) and write results to Redis backend.
  - The `celery` app is instantiated in the same codebase; tasks are imported and decorated with `@shared_task`.
- **Backend ↔ Apify**:
  - HTTPS API calls (`api.apify.com/v2`) to start actors, monitor runs, fetch dataset (`/runs/{run_id}/dataset/items`).
- **Backend ↔ OpenAI**:
  - HTTPS API (`api.openai.com/v1/embeddings` and `/v1/chat/completions`) with bearer token.
- **Backend ↔ Email Provider**:
  - SMTP (TCP port 25/587) or HTTP API (POST to SendGrid/Mailgun/SES endpoint) with auth credentials.
- **Backend ← Supabase Realtime (optional)**:
  - Realtime payloads sent over WebSocket to the frontend (if the frontend subscribes directly); alternatively the backend can listen and push via its own WebSocket.
- **Frontend ↔ Supabase Auth (Optional)**: For convenience, the frontend may handle sign‑in/up via Supabase’s GoTrue API directly, receiving JWTs that it then sends to the backend.
- **External Monitoring**: Prometheus scrapes the `/metrics` endpoint exposed by the backend (and optionally the frontend). Logs are forwarded via vector/Fluentbit to Loki; traces exported via OTLP to Tempo/Jäger.

## Data Flow Summary (High Level)

1. **Job Ingestion**: Scheduler → Celery worker → Apify → backend (normalization, dedup) → Supabase `jobs` & `jobs_raw` → Redis `job_new` → embedding worker → update `jobs` with vector.
2. **Resume Upload**: Frontend → backend (validation) → Supabase Storage (`resumes` bucket) + metadata in `resumes` table → embedding via OpenAI → store `skill_vector` → Redis `resume_updated` → matching worker may refresh user’s top matches.
3. **Matching Request**: Frontend → backend (fetch user vector, ANN search via pgvector, hybrid scoring) → Redis cache (top‑N) → JSON response.
4. **AI Generation**: Frontend → backend (prompt templating) → OpenAI → generated text → optional storage (`documents` bucket) → metadata in `generated_documents` table → JSON/file URL response.
5. **Notifications**: Event (match, app status) → Redis channel → Celery worker → render template → send via SMTP/API → log in `notifications` table.
6. **Admin Actions**: Frontend → backend (admin‑protected endpoints) → trigger Celery task (e.g., start scrape) or modify DB → updates reflected via Realtime or next poll.

## Deployment View Relation

The component diagram maps to the deployment view as follows:
- Frontend → served via CDN or container (Next.js).
- Backend & Celery workers as container replicas behind a load balancer.
- Supabase and Redis as managed services (or self‑hosted clusters accessed via private endpoints).
- Apify, OpenAI, Email Provider called over public internet.
- Monitoring stack may reside in the same VPC or be offered as SaaS.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*