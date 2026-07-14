# Low Level Design

## Purpose

To detail the internal structure of each major service, including key classes, data structures, algorithms, and concurrency considerations, based on the high‑level architecture.

## Contents

- Service‑by‑Service Breakdown
- Core Data Models
- Algorithmic Details
- Concurrency & Threading
- Error Handling & Logging
- Configuration Management
- API Contracts (summary)
- Security Primitives
- Testing Strategies (unit/mock)

## Service‑by‑Service Breakdown

### 1. Authentication Wrapper
- **FastAPI app** (`main.py`) includes a dependency `get_current_user` that validates JWTs issued by Supabase Auth.
- **Core Classes**:
  - `UserModel` (SQLAlchemy ORM) – extends `auth.users` via foreign key `id` -> `auth.users(id)`; stores profile fields: `full_name`, `avatar_url`, `bio`, `location`, `created_at`, `updated_at`.
  - No token storage; validation uses Supabase JWKS.
- **Dependencies**:
  - `get_current_user(token: str = Depends(oauth2_scheme))` → returns `UserModel` or raises HTTPException.
  - `get_optional_user` for endpoints that may be public.
- **Algorithms**:
  - JWT verification using `python-jwt` (PyJWT) with RS256 and Supabase JWKS endpoint.
  - Optional revocation list via Redis for immediate logout.
- **Concurrency**: Async request handlers; DB session per request (SQLAlchemy async engine).
- **Error Handling**: Returns 401 for invalid/expired tokens; 403 for insufficient permissions.
### 2. User Service
- **Responsibility**: profile CRUD, preferences.
- **Core Classes**:
  - `UserProfileModel` – extends `UserModel` with fields: headline, location, bio, links (JSONB), avatar_url, preferences (JSONB).
  - `PreferenceModel` – keys: email_notifications, job_match_threshold, default_remote, etc.
  - `UserService` – methods: `get_profile`, `update_profile`, `update_preferences`.
- **Data Structures**:
  - Preferences stored as JSONB for flexibility; validated via Pydantic models on read/write.
- **Algorithms**: Simple CRUD; no heavy computation.
    - **Concurrency**: Async request handlers; DB session per request (SQLAlchemy async engine).

### 3. Job Service
- **Responsibility**: ingestion, deduplication, storage, search.
- **Core Classes**:
  - `JobRawModel` – id, source, raw_json (JSONB), fetched_at.
  - `JobModel` – id, source_id, title, company, location (JSONB), description_text, salary_min, salary_max, currency, employment_type, remote_flag, post_date, apply_url, hash_dedup (unique), created_at.
  - `JobService` – methods: `ingest_batch`, `deduplicate`, `search_fulltext`, `get_by_id`, `list_recent`.
  - `ApifyConnector` – wraps Apify SDK: `start_actor(run_id)`, `poll_until_finished`, `download_dataset`.
  - `Deduplicator` – computes hash of (`lower(title)`, `lower(company)`, `url`) + fuzzy fallback.
- **Data Structures**:
  - `JobSearchQuery` Pydantic model with fields: query, location, salary_range, remote_only, employment_type, date_posted, sort, limit, offset.
  - Ingestion batch: list of dicts from Apify dataset.
- **Algorithms**:
  - **Full‑text search**: Uses PostgreSQL `tsvector` column (`search_vector`) built from `title` \`|| ' ' ||` `company` \`|| ' ' ||` `description`. GIN index.
  - **Fuzzy matching** (fallback): `rapidfuzz.fuzz.token_set_ratio` > 90.
  - **Salary parsing**: Regexes for patterns like `\$[\d,]+(?:–\$[\d,]+)?`, `\d{1,3}(?:,\d{3})*(?:\s?-\s?\d{1,3}(?:,\d{3})*)?`.
- **Concurrency**: Ingestion workers run as Celery tasks; each task processes a source independently. DB operations use SQLAlchemy session with retry on deadlock.
- **Error Handling**: Failed ingestion retries with exponential backoff (max 5 attempts). Dead‑letter pushes to Redis list `job_ingest:dlq` for manual replay.

### 4. Resume Service
- **Responsibility**: upload, parsing, skill extraction, embedding.
- **Core Classes**:
  - `ResumeModel` – id, user_id, file_name, file_size, mime_type, storage_key (Supabase Storage), raw_text, parsed_json (JSONB), skill_vector (pgvector), created_at, updated_at.
  - `ParseResult` – Pydantic model: contact, summary, experience (list), education (list), skills (list), certifications (list).
  - `ResumeService` – methods: `upload_resume`, `parse_resume`, `extract_skills`, `generate_embedding`, `get_resume`.
  - `TextExtractor` – uses `pdfminer.six` for PDF, `python-docx` for DOCX, fallback to `pytesseract` + `pdf2image`.
  - `SectionParser` – rule‑based regex headings + spaCy NER for entity extraction.
  - `SkillNormalizer` – loads ESCO/O*NET mapping from CSV; fuzzy matches skill strings to canonical IDs; returns list of `{id, name, confidence}`.
  - `EmbeddingClient` – thin wrapper around OpenAI `embeddings.create`.
- **Data Structures**:
  - `ParsedExperience` – fields: title, company, location, start_date, end_date, description, bullet_points (list).
  - `SkillEntry` – `{skill_id, skill_name, source_text, confidence}`.
- **Algorithms**:
  - **Skill extraction**: Noun chunk + named entity recognition; filter to known skill taxonomy; boost exact matches from resume sections.
  - **Normalization**: For each extracted skill, compute TF‑IDF weighted similarity against taxonomy candidates; pick best > 0.8 confidence.
  - **Embedding**: Input is concatenated cleaned sections (`summary` + `experience` + `skills`) truncated to token limit; OpenAI returns a single 1536‑dim vector.
- **Concurrency**: File upload is streamed directly to S3 via presigned URL; parsing runs in a background Celery task to avoid blocking request.
- **Error Handling**: Unsupported file types returns 415; extraction failures logged; user can retry with alternative format.
- **Security**: File virus scan (ClamAV) optional; storage bucket policies enforce private access; signed URLs for download with expiry.

### 5. Matching Service
- **Responsibility**: semantic and hybrid job‑to‑resume matching.
- **Core Classes**:
  - `MatchingService` – methods: `get_matches_for_user`, `calculate_match_score`, `update_user_preferences`.
  - `JobVectorRepo` – abstracts pgvector queries: `nearest_neighbors(resume_vector, k, filter_conditions)`.
  - `ScoreCalculator` – combines cosine similarity, keyword Jaccard, recency decay, location preference.
  - `PreferenceLoader` – reads user‑specific weights from `user_preferences` JSONB.
- **Data Structures**:
  - `MatchResult` – job_id, title, company, location, match_score, breakdown (dict of component scores), salary, apply_url.
  - `SearchFilter` – same as JobService search query but anchored to user context.
- **Algorithms**:
  - **ANN Search**: pgvector `ivfflat` index with `lists = 100`; probe `10` for recall ~90%.  
  - **Cosine Similarity**: `1 - (vector <=> resume_vector)` (PostgreSQL operator).  
  - **Keyword Jaccard**: Intersection over union of normalized skill sets (from resume and job’s extracted skill entities). Job skills derived from description via same `SkillNormalizer` (cached per job).  
  - **Recency Decay**: `exp(-λ * days_since_post)`, λ = ln(2)/half_life (half_life = 14 days).  
  - **Location Preference**: Boolean match if user set “remote only” or radius filter using Haversine distance (if lat/long available).  
  - **Weight Adjustment**: User can override default weights (α,β,γ,δ) via UI; stored as JSONB.
- **Data Structures**:
  - `UserMatchCache` – Redis hash keyed by `user:{id}:matches` storing JSON of top‑N matches with TTL 300 s.
- **Concurrency**: Matching requests are read‑only; can be served concurrently by many FastAPI workers. DB connections pooled. Redis read‑only pipelines.
- **Error Handling**: If pgvector extension unavailable, fallback to lexical search only (degraded mode). Service logs and returns 503 with retry‑after header.

### 6. AI Service
- **Responsibility**: LLM‑based generation of cover letters, cold emails, skill‑gap analysis.
- **Core Classes**:
  - `AIService` – methods: `generate_cover_letter`, `generate_cold_email`, `analyze_skill_gap`.
  - `PromptBuilder` – Jinja2 templates loaded from `prompts/ai.md` (or separate files). Variables: `resume_summary`, `job_description`, `tone`, `max_length`.
  - `LLMClient` – async wrapper around OpenAI `chat.completions.create` (or `completions`). Handles retry, rate‑limitbackoff.
  - `OutputSanitizer` – strips markdown, enforces plain text, optionally converts to PDF via `weasyprint`.
- **Data Structures**:
  - `GenerationRequest` – Pydantic: `resume_id`, `job_id`, `type` (cover_letter|cold_email|skill_gap), `parameters` (dict).
  - `GenerationResponse` – `generated_text`, `format`, `token_usage`.
- **Algorithms**:
  - **Prompt Construction**: Concatenate system instruction, user instruction, and data; ensure token count < model limit (8191 for gpt-4-turbo).  
  - **Temperature**: 0.7 for creative tasks; 0.2 for factual extraction (skill gap).  
  - **Max Tokens**: 500 for cover letter, 150 for cold email, 300 for skill gap.  
  - **Retry Logic**: Exponential backoff with jitter (max 4 attempts) on 429/5xx errors.
- **Concurrency**: Each generation is an independent OpenAI API call; async handler allows high concurrency limited by rate limits.  
- **Error Handling**: Propagate OpenAI error with status 429 (rate limit) → return 429 to client with Retry‑After header. Other errors → 502 with message.
- **Cost Control**: Per‑user daily quota enforced via Redis counter (`ai_quota:{user_id}`); reset at midnight UTC.

### 7. Notification Service
- **Responsibility**: templating, delivering email and in‑app notices.
- **Core Classes**:
  - `NotificationService` – methods: `send_email`, `send_inapp`, `process_event`, `get_preferences`.
  - `TemplateEngine` – Jinja2 environment with autoescape; loads templates from `templates/email/` and `templates/inapp/`.
  - `DeliveryClient` – wrapper around SMTP (smtplib) or HTTP API (SendGrid, Mailgun, SES).
  - `EventProcessor` – subscribes to Redis channels (`user:{id}:notifications`) and dispatches.
- **Data Structures**:
  - `NotificationRequest` – recipient_id, template_name, context (dict), channels (list of email/inapp), priority.
  - `SentRecord` – id, recipient_id, template, sent_at, channel, status.
- **Algorithms**:
  - Render template with context → produce subject and body (HTML & text).  
  - For email: use SMTP TLS or API key; handle bulk send via batch API if provider supports.  
  - In‑app: store record in DB table `notifications`; optionally push via Redis pub/sub for real‑time UI update.  
  - Debounce: if same event fires multiple times within short window, coalesce.
- **Concurrency**: Email sending is I/O‑bound; use thread pool executor (`run_in_executor`) to avoid blocking async event loop.  
- **Error Handling**: Retry transient SMTP errors (max 3 attempts) with exponential backoff; permanent errors logged and message marked as failed.  
- **Rate Limiting**: Respect provider limits; secondary leaky bucket per API key.

### 8. Scheduler & Worker Services (combined for brevity)
- **Scheduler** (`apscheduler`) triggers jobs at cron intervals; stores jobs in PostgreSQL table `scheduled_jobs`.
- **Worker** (Celery) receives tasks from Redis broker; executes:
  - `ingest_jobs(source)` – calls ApifyConnector.
  - `process_resume(resume_id)` – invokes ResumeService steps.
  - `update_embeddings(batch_size)` – re‑compute embeddings for stale resumes.
  - `refresh_user_matches(user_id)` – calls MatchingService and caches result.
- **Concurrency**: Number of worker processes configurable (`celery worker -c 4`). Each process prefetches tasks (default 1).  
- **Error Handling**: Task autoretry for known transient exceptions (max 3). Failed tasks move to dead‑letter queue after max retries.

## Core Data Models (shared snippets)

- **BaseModel** – integer `id` primary key, `created_at` TIMESTAMP WITH TIME ZONE DEFAULT now(), `updated_at` TIMESTAMP WITH TIME ZONE.
- **SoftDeleteMixin** – `deleted_at` TIMESTAMP NULL; queries filter WHERE deleted_at IS NULL.
- **TimestampMixin** – as above.
- **UUIDMixin** (optional) – `uuid` UUID DEFAULT uuid_generate_v4() UNIQUE.
- **AuditMixin** – `created_by` FK to users, `updated_by` FK.

## Algorithmic Details (selected)

### Skill Normalization Pipeline
1. Extract noun chunks + named entities (spaCy en_core_web_md).  
2. Lowercase, strip punctuation.  
3. Exact lookup in ESCO/O*NET dictionary (hash map).  
4. For unknowns, compute TF‑IDF vector vs. dictionary entries (pre‑computed matrix).  
5. Choose candidate with highest cosine similarity > 0.7; else mark as “unknown”.  
6. Return list of `{canonical_id, canonical_name, confidence}`.

### Salary Parsing Heuristic
- Regex patterns capture ranges, single values, periodicities (per hour, per year).  
- Normalize to annual USD assuming 2080 work‑hours/year if needed (configurable).  
- If ambiguous, store `null` and flag for manual review.

### Recency Decay Function
\[
score_{recency} = e^{-\lambda \cdot d}
\]
where \(d\) = days since job posted, \(\lambda = \frac{\ln(2)}{half\_life}\). Half‑life configurable (default 14 days).

### Hybrid Matching Formula
\[
S = \alpha \cdot S_{cosine} + \beta \cdot S_{jaccard} + \gamma \cdot s_{recency} + \delta \cdot s_{location}
\]
Weights default: α=0.40, β=0.30, γ=0.20, δ=0.10; sum = 1.

## Concurrency & Threading

- **FastAPI**: Uses `starlette` asyncio; each request runs in its own task; no global mutable state.  
- **Database**: SQLAlchemy async engine with `asyncpg` driver; connection pool sized to `max_workers * 2`.  
- **Redis**: `aioredis` connection pool; shared across coroutines.  
- **Celery**: Prefork pool; each worker process handles tasks sequentially; suitable for CPU‑bound (embedding batch) and I/O‑bound (Apify) tasks.  
- **Email Sending**: Offloaded to `ThreadPoolExecutor` (max_workers=10) to avoid blocking event loop.  
- **Blocking CPU work** (e.g., heavy regex) is kept minimal; if needed, use `run_in_executor`.

## Error Handling & Logging

- **Hierarchy**: `BaseAppException → HTTPException → specific subclasses (ValidationError, ExternalServiceError, DatabaseError, etc.)`.  
- **Handlers**: FastAPI exception middleware returns JSON with `error`, `message`, `details` (optional).  
- **Logging**: Structured JSON via `loguru` or `structlog`; fields: `timestamp`, `level`, `logger`, `trace_id`, `span_id`, `message`, `payload*`.  
- **Tracing**: OpenTelemetry instrumentation for FastAPI, SQLAlchemy, Redis, HTTPX; exporters to Jaeger or Tempo.  
- **Sensitive Data**: Never log passwords, tokens, API keys; replace with `[REDACTED]`.  
- **Alerting**: Critical errors (5xx, DB down) trigger alerts via Alertmanager (PodDisruptionBudget, dead‑letter queue length).

## Configuration Management

- **Sources** (in order of precedence):  
  1. Environment variables (`DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `APIFY_TOKEN`, `SECRET_KEY`).  
  2. `.env` file (python‑dotenv) for local development.  
  3. `config.yaml` (optional) for non‑secret feature flags.  
- **Validation**: Pydantic `BaseSettings` subclass (`Settings`) with env prefix `APP_`.  
- **Immutable at Runtime**: Settings loaded once at startup; changes require restart.  
- **Secret Management**: In production, prefer Kubernetes Secrets or AWS Secrets Manager injected as env vars.

## API Contracts (summary)

All services expose OpenAPI 3.0 documents accessible at `/docs`. Key endpoints grouped by tag:

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `POST /auth/logout` (token revocation)

### User
- `GET /users/{id}`
- `PATCH /users/{id}`
- `GET /users/{id}/preferences`
- `PATCH /users/{id}/preferences`

### Job
- `GET /jobs/search`
- `GET /jobs/{id}`
- `POST /jobs/{id}/apply` (record click)
- `GET /jobs/{id}/similar` (internal)

### Resume
- `POST /resumes/upload`
- `GET /resumes/{id}`
- `GET /resumes/{id}/parse`
- `POST /resumes/{id}/reparse`

### Matching
- `GET /matching/{user_id}`
- `GET /matching/{user_id}/scores/{job_id}` (debug)

### AI
- `POST /ai/cover-letter`
- `POST /ai/cold-email`
- `POST /ai/skill-gap`

### Notification
- `GET /notifications/prefs`
- `PATCH /notifications/prefs`
- `GET /notifications/recent`
- `POST /notifications/test-email`

### Admin
- `GET /admin/users`
- `POST /admin/scraping/{source}/run`
- `GET /admin/stats`
- `POST /admin/maintenance/reindex`  
- `GET /admin/logs` (paginated)

All endpoints require `Authorization: Bearer <jwt>` except public docs and health check (`/health`).

## Security Primitives

- **Password Hashing**: Not applicable (handled by Supabase Auth).
- **JWT Validation**: Verify Supabase‑issued JWT using PyJWT (RS256) and the Supabase JWKS.  
- **Token Revocation**: Optional Redis set `revoked_jti` for immediate logout; otherwise rely on short‑lived access tokens and refresh‑token rotation via Supabase.  
- **Rate Limiting**: `slowapi.Limiter` with key function `get_remote_address`; custom exemptions for trusted IPs.  
- **CORS**: `fastapi.middleware.cors.CORSMiddleware` with `allow_origins` from env, `allow_credentials=True`, `allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]`, `allow_headers=["*"]`.  
- **Security Headers**: `Starlette` middleware adds:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy: default-src 'self'; img-src * data:; style-src 'self' 'unsafe-inline';`
- **SQL Injection Prevention**: ORM usage; any raw SQL uses `sqlalchemy.text()` with bound parameters.  
- **Input Sanitization**: `pydantic` `str.strip()` and `regex` validation; HTML rendering uses Jinja2 auto‑escape.  
- **File Upload Validation**:
  - Check `content-type` against allowed list (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`).  
  - Limit size via `FastAPI` `File(..., max_length=5_242_880)` (5 MB).  
  - Scan uploaded stream with `clamsd` if ClamAV daemon available.  
- **Dependency Checks**: `safety check -r requirements.txt` in CI; `bandit -r . -ll`.

## Testing Strategies (unit/mock)

- **Unit Tests**:
  - `pytest` with `pytest-asyncio` for async endpoints.  
  - Mock external services using `asynckmock` or `respx` for HTTPX.  
  - Use `factory_boy` or custom fixtures for model instances.  
  - Assert JSON schema compliance via `jsonschema`.  
- **Integration Tests**:
  - Spin up docker‑compose stack with real PostgreSQL, Redis, MinIO (S3 mock), and a mock Apify server (`respx`).  
  - Run API contract tests against the stack.  
- **Contract Tests**:
  - Generate OpenAPI spec from source (`pyantic extract`).  
  - Validate against spec using `Dredd` or `schemathesis`.  
- **End‑to‑End Tests**:
  - Cypress specs covering: user registration → login → resume upload → job search → apply → notification.  
  - Runs against a staging‑like environment (headless Chrome).  
- **Load & Stress Tests**:
  - k6 scenarios simulating 500 VUs ramp‑up to 5k over 5 min on search & matching endpoints.  
  - Monitor latency, error rate, resource utilization.  
- **Security Tests**:
  - OWASP ZAP baseline scan against deployed staging.  
  - Dependency vulnerability scans (`safety`, `pip-audit`).  
- **Coverage Goals**:
  - Overall line coverage ≥ 80 %.  
  - Critical paths (authentication, payment‑like endpoints, data mutation) ≥ 90 %.  
  - Mutation testing (`mutmut`) on core algorithms (≥ 70 % mutation score).  

---  
*Document Version: 1.0*  
*Last Updated: 2026‑07‑14*