# API Flow

## Purpose

To illustrate the typical flow of an HTTP request through the API layer of the AI-Powered Job Finder backend, from ingress to response, including middleware, authentication, routing, service invocation, and external calls.

## Contents

- Ingress
- Middleware Pipeline
- Routing & Dispatch
- Service Layer Interaction
- Data Access & External Integrations
- Response Assembly
- Error Handling
- Observability Hooks
- Example Flow: Job Search
- Example Flow: Resume Upload & Embedding

## Ingress

- Clients (browser, mobile app, external services) send HTTPS requests to the API gateway or directly to the FastAPI instance (if no proxy).
- The request includes headers (Authorization, Content-Type, Accept, etc.) and optionally a body or query parameters.

## Middleware Pipeline

Before reaching the route handler, the request passes through a series of middleware (order matters):

1. **CORS Middleware** – enforces allowed origins, methods, headers.
2. **Trusted Proxy Middleware** – reads `X-Forwarded-For`/`X-Forwarded-Proto` when behind a load balancer.
3. **Security Headers Middleware** – adds HSTS, CSP, X‑Content‑Type‑Options, etc.
4. **Request ID Middleware** – generates a unique `X-Request-ID` and stores it in the request context for tracing.
5. **Logging Middleware** – logs the start of the request (method, path, client IP, request ID).
6. **Authentication Middleware** – validates the JWT from `Authorization: Bearer <token>` using Supabase JWKS; sets `request.state.user` (or raises 401).
7. **Rate Limiting Middleware** – applies per‑IP and per‑user limits via `slowapi`; returns 429 if exceeded.
8. **Body Parsing Middleware** – FastAPI automatically parses JSON, form, or multipart data based on `Content-Type`.

## Routing & Dispatch

- The request reaches the appropriate **APIRouter** (versioned under `/api/v1/`).
- Path and method match a specific endpoint function (`async def`).
- Path, query, and body parameters are validated via Pydantic models; validation errors trigger a 422 response automatically.
- The endpoint function receives dependencies via `Depends`:
  - `db: AsyncSession` – SQLAlchemy async database session.
  - `current_user: UserModel` – from the auth dependency (returns the user mirrored from `auth.users`).
  - Optional: `settings: Settings`, `redis: Redis`, etc.

## Service Layer Interaction

- The endpoint delegates business logic to a **service** class or function (e.g., `JobService.search`, `ResumeService.upload`).
- Services receive the dependencies they need (DB session, Redis client, external HTTP clients) via constructor or method arguments.
- They contain the core logic: validation, calls to repositories, external API invocations, and aggregation of results.
- Services return plain Python data structures (dicts, lists, ORM models) or raise custom exceptions (`ValidationError`, `ExternalServiceError`, etc.).

## Data Access & External Integrations

- **Repository Layer**: Uses SQLAlchemy 2.0 async to perform CRUD operations (`select`, `insert`, `update`, `delete`). Complex queries (full‑text search, pgvector nearest neighbor) are expressed via `select(...).where(...).order_by(...)`.
- **External HTTP Clients**: `httpx.AsyncClient` instances (pooled) are used to call Apify, OpenAI, email providers. Timeouts, retry policies (via `tenacity`), and circuit‑breaker patterns are applied as needed.
- **Redis**: `aioredis` pool used for caching (`get`, `set`, `expire`), pub/sub (`subscribe`, `publish`), and rate‑limit counters (`incr`, `expire`).

## Response Assembly

- The endpoint transforms the service’s output into a JSON‑serializable structure (often directly returning a Pydantic model, which FastAPI serializes).
- Status code is set (default 200; overridden via `status_code` argument or by raising `HTTPException` with a specific code).
- Response headers may include `X-Request-ID` (for tracing), `Cache-Control` (if caching applies), and custom headers (e.g., `X-RateLimit-Remaining`).
- The response is sent back through the middleware stack in reverse order (logging the completion time, etc.).

## Error Handling

- Exceptions raised in middleware or handlers are caught by FastAPI’s exception middleware.
- Custom exceptions (`AppException`) contain an error code, message, and optional details list.
- The middleware returns a consistent JSON error body:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Human readable description",
      "details": [{"field": "email", "issue": "must be a valid email"}]
    }
  }
  ```
- Unhandled exceptions result in a 500 response with a generic error message (details hidden in production) and are logged with full stack trace.

## Observability Hooks

- **Logging**: Each middleware and service logs key events (entry, exit, errors) with the request ID, timestamps, and structured fields.
- **Metrics**: The `prometheus_fastapi_instrumentator` instruments the HTTP server, exposing:
  - `http_requests_total{method,endpoint,status,le="0.8"}` – requests under 800 ms SLA.
  - `http_request_duration_seconds_bucket` – latency histograms.
  - `http_request_size_bytes` and `http_response_size_bytes`.
  - Custom business metrics (e.g., `jobs_indexed_total`, `matches_generated_total`) can be emitted via `Counter` or `Gauge` from services.
- **Tracing**: OpenTelemetry instrumentation automatically creates spans for HTTP requests, SQLAlchemy queries, Redis commands, and outgoing HTTP calls. The trace ID is propagated via the `traceparent` header and correlated with logs.

## Example Flow: Job Search

1. **Client** → `GET /api/v1/jobs/search?q=software%20engineer&remote_only=true&limit=20`
2. **Ingress**: TLS termination, request received by Uvicorn.
3. **Middleware**:
   - CORS: origin allowed.
   - Trusted Proxy: reads real IP.
   - Security Headers: adds HSTS, CSP.
   - Request ID: `x-request-id: abc123`.
   - Logging: logs request start.
   - Authentication: validates JWT, sets `request.state.user`.
   - Rate Limiting: checks counters, allows.
   - Body Parsing: none (GET).
4. **Routing**: Matches `GET /jobs/search` → `job_search` endpoint in `routers/jobs.py`.
5. **Dependencies**:
   - `db`: AsyncSession (from pool).
   - `current_user`: UserModel (from auth).
6. **Service Call**: `await job_service.search(db, current_user.id, q, remote_only, limit, offset)`.
7. **Repository**:
   - Builds a `tsvector` query for full‑text search on title/description/company.
   - Adds filters for `remote_flag`.
   - Orders by rank, limits.
   - Returns list of `Job` ORM objects.
8. **Service Post‑Processing**:
   - For each job, if needed, fetches cached embedding from Redis (or computes on‑the‑fly) for hybrid scoring (though pure search may skip embeddings).
   - Returns list of dictionaries with basic fields and a relevance score.
9. **Response**:
   - Endpoint returns `List[JobSearchResult]` (Pydantic model) → JSON.
   - Middleware logs completion time, adds `X-Request-ID`.
10. **Client** receives JSON list of jobs.

## Example Flow: Resume Upload & Embedding

1. **Client** → `POST /api/v1/resumes/upload` (multipart/form‑data with file).
2. **Middleware** steps as above (authentication validates JWT).
3. **Routing**: Matches to `upload_resume` endpoint.
4. **Dependencies**: `db`, `current_user`, `redis`, `httpx` client for OpenAI.
5. **Service**:
   - Validates file type and size.
   - Streams upload to Supabase Storage (via `supabase.storage.from_('resumes').upload`).
   - Retrieves public URL (or signed URL for private bucket) and stores `storage_key`.
   - Extracts text (PDF → `pdfminer.six`, DOCX → `python-docx`).
   - Sections parsed via regex/spaCy.
   - Skills normalized via lookup table.
   - Constructs text for embedding (summary + experience + skills), truncates to token limit.
   - Calls OpenAI `embeddings.create` (async via `httpx`).
   - Receives 1536‑dim vector.
   - Saves `Resume` row: links `user_id`, `storage_key`, `raw_text`, `parsed_json` (JSONB), `skill_vector` (vector(1536)), timestamps.
6. **Response**:
   - Returns the created `Resume` object (excluding raw binary) with ID and metadata.
7. **Post‑Response (Optional)**:
   - Background task may be enqueued (via Celery) to update any cached matches for the user.
   - The endpoint returns immediately; the user sees a success message.

## Summary

The API flow ensures that every request is authenticated, logged, rate‑limited, and traced, while delegating business logic to focused services that interact with the database and external APIs through well‑defined abstractions. Error handling is centralized, and observability is built in to support rapid debugging and performance tuning.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*