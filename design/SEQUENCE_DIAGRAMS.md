# Sequence Diagrams

## Purpose

To illustrate the dynamic interactions between components (user interface, backend services, external APIs, data stores) for key scenarios in the AI-Powered Job Finder system. These diagrams help developers understand the order of method calls, message passing, and synchronization points.

## Contents

- Overview of Notation
- Key Scenarios
  1. User Login & Token Validation
  2. Job Ingestion (Apify → Backend → Supabase)
  3. Resume Upload & Embedding Generation
  4. Matching Request (Search with Personalized Scores)
  5. AI Generation (Cover Letter / Cold Email / Skill‑Gap)
  6. Notification Dispatch (Event → Email / In‑app)
  7. Admin‑Triggered Scrape
  8. Logout & Token Revocation (optional)
- How to Read the Diagrams
- Extending Diagrams for New Features

## Overview of Notation

We use a simplified UML sequence diagram style:
- **Participants** are shown as rectangles at the top (lifelines).
- **Vertical dashed lines** represent the lifeline (time proceeds downward).
- **Horizontal solid arrows** indicate synchronous messages (method calls / requests).
- **Dashed arrows** indicate asynchronous messages or callbacks (e.g., webhook replies, event notifications).
- **Activation bars** (thin rectangles on lifelines) show the period during which a participant is active (executing).
- **Notes** are placed in rectangles with a folded corner to explain steps.
- **Alt** (alternative) frames show conditional branches.
- **Loop** frames indicate repetition (e.g., polling).

## Key Scenarios

### 1. User Login & Token Validation

Participants: Browser (UI), Backend (FastAPI), Supabase Auth (JWKS), Redis (optional revocation), Database (users table).

```
Browser -> Backend: POST /auth/login (email, password)
Backend -> Supabase Auth: /auth/token (grant_type=password, username, password)
Supabase Auth --> Backend: 200 OK {access_token, refresh_token, user}
Backend -> DB: SELECT * FROM users WHERE id = user.id FROM token (optional join for profile)
Backend -> Redis: SETEX revoked_jti:<jti> <ttl> (if implementing logout list)
Backend --> Browser: 200 OK {access_token, refresh_token, user profile}
Browser -> Browser: Store tokens (httpOnly cookie / localStorage)
```

If using Supabase Auth directly from the browser, the browser talks to Supabase, then sends the JWT to the backend for validation on protected routes.

### 2. Job Ingestion (Apify → Backend → Supabase)

Participants: Scheduler (Celery Beat/APScheduler), Celery Worker (job_ingest), Backend API (internal service), Apify, Supabase PostgreSQL, Redis.

```
Scheduler -> Celery: enqueue job_ingest(task_id)
Celery -> Worker: execute job_ingest
Worker -> Apify: POST /runs (actor_id, input)
Apify --> Worker: 201 Created {run_id}
Worker -> Apify: GET /runs/{run_id} (poll every 5s until status=SUCCEEDED/FAILED)
Apify --> Worker: 200 OK {status: SUCCEEDED, ...}
Worker -> Apify: GET /runs/{run_id}/dataset/items
Apify --> Worker: 200 OK [{job1_json}, {job2_json}, ...]
Worker -> Backend (internal): ingest_batch([job1_json, job2_json, ...])
Backend -> Supabase: INSERT INTO jobs_raw (source, raw_json, fetched_at) VALUES (...)
Backend -> Supabase: Normalize each json → insert into jobs table (with dedup check ON CONFLICT DO NOTHING)
Backend -> Supabase: (Optional) compute embedding for new jobs via OpenAI (batch)
Backend -> Redis: PUBLISH job_new {job_id, source, timestamp}
Worker --> Scheduler: task completed (success/failure)
```

### 3. Resume Upload & Embedding Generation

Participants: Browser (UI), Backend API, Supabase Storage, Supabase PostgreSQL, OpenAI, Redis (optional cache).

```
Browser -> Backend: POST /resumes/upload (multipart/form-data, file)
Backend -> Supabase Storage: upload file to bucket `resumes` → returns storage_key
Backend -> Supabase: INSERT INTO resumes (user_id, storage_key, file_name, mime, file_size) RETURNING id
Backend -> Backend: extract_text(file) → raw_text
Backend -> Backend: parse_sections(raw_text) → parsed_json (experience, education, skills, certifications)
Backend -> Backend: normalize_skills(skills_extracted) → normalized_skill_list
Backend -> Backend: build_embedding_text = summary + " " + experience + " " + skills (truncated)
Backend -> OpenAI: POST /embeddings (model=text-embedding-3-small, input=embedding_text)
OpenAI --> Backend: 200 OK {embedding: [1536 floats]}
Backend -> Supabase: UPDATE resumes SET raw_text=..., parsed_json=..., skill_vector=… WHERE id = …
-- Optional: Invalidate match cache for this user
Backend -> Redis: DEL user:{user_id}:matches   (or SET with short TTL)
Backend --> Browser: 200 OK {resume_id, file_name, parsed_preview, skill_count}
```

### 4. Matching Request (Search with Personalized Scores)

Participants: Browser, Backend API (auth, rate limiting), Supabase PostgreSQL (jobs, resumes), Redis (match cache), optionally OpenAI (if job embedding not stored).

```
Browser -> Backend: GET /jobs/search?q=frontend&remote_only=true&limit=20
Backend -> Auth: validate JWT → user_id
Backend -> Redis: GET user:{user_id}:matches
if cache hit and not stale:
    --> Browser: 200 OK {jobs list from cache}
else:
    Backend -> Supabase: SELECT skill_vector FROM resumes WHERE user_id = ? LIMIT 1
    Supabase --> Backend: skill_vector (or NULL)
    Backend -> Supabase: SELECT * from jobs WHERE (filters: remote_only=true, text match via tsvector) ORDER BY embedding <=> ? LIMIT k  (k=200 pre‑filter)
    Supabase --> Backend: list of candidate jobs (id, embedding, title, …)
    Backend -> Backend: For each candidate:
        compute cosine = 1 - (candidate.embedding <=> user.vec)
        compute keyword Jaccard from parsed skills
        compute recency = exp(-ln(2) * days_since_post / half_life)
        compute location match (remote flag or distance)
        final score = α*cosine + β*jaccard + γ*recency + δ*location
    Backend -> Backend: Sort candidates by final score DESC, take top N (e.g., 20)
    Backend --> Browser: 200 OK {list of jobs with id, title, company, location, match_score, breakdown}
    Backend -> Redis: SET user:{user_id}:matches (JSON of result list) EXPIRE 300
```

### 5. AI Generation (Cover Letter / Cold Email / Skill‑Gap)

Participants: Browser, Backend API, OpenAI, Supabase PostgreSQL (resumes, jobs, generated_documents), Redis (optional rate limit/quota).

```
Browser -> Backend: POST /ai/cover-letter (json: {resume_id, job_id})
Backend -> Auth: validate JWT → user_id
Backend -> Supabase: SELECT r.*, j.* FROM resumes r JOIN jobs j ON r.id = ? AND j.id = ? WHERE r.user_id = user_id
Supabase --> Backend: resume row, job row
Backend -> Backend: Build prompt:
    System: "You are a professional cover letter writer."
    User: "Write a concise, tailored cover letter for the following resume and job description.\n\nResume:\n{resume.summary}\n{resume.experience}\n{resume.skills}\n\nJob Description:\n{job.description}"
Backend -> OpenAI: POST /chat/completions (model=gpt-4o-mini, messages=[system, user], temperature=0.7, max_tokens=500)
OpenAI --> Backend: 200 OK {choices: [{message: {content: "generated text"}}]}
Backend -> Backend: (Optional) Convert to PDF via weasyprint or browser print-to-PDF
Backend -> Supabase: INSERT INTO generated_documents (user_id, job_id, doc_type, content_text, storage_key) VALUES (...)
Backend --> Browser: 200 OK {generated_text, doc_id, download_url (if PDF)}
```

The flow for `cold-email` and `skill-gap` is analogous, differing only in prompt and parameters (temperature lower for fact‑based extraction, max_tokens smaller).

### 6. Notification Dispatch (Event → Email / In‑app)

Participants: Event Source (Job Ingestion Worker, Resume Service, Application Service, Scheduler), Redis (pub/sub), Celery Worker (notification_send), Supabase PostgreSQL (notifications table, notification_prefs), Email Provider (SMTP or HTTP API), Supabase Realtime (optional).

```
Event Source -> Redis: PUBLISH notification_send {user_id, type, context}
Redis -> Celery Worker (notification_send): receives message
Worker -> Supabase: SELECT * FROM notification_prefs WHERE user_id = ?
Supabase --> Worker: preferences (email_enabled, inapp_enabled, frequency, quiet hours)
Worker -> Supabase: INSERT INTO notifications (user_id, type, context, status='pending') RETURNING id
Worker -> Supabase: UPDATE notifications SET status='sending', attempt=1, last_attempt=now() WHERE id = ?
Worker -> Email Provider: (if email_enabled and not in quiet hour) send via SMTP/API
Email Provider --> Worker: 200 OK (or error)
Worker -> Supabase: UPDATE notifications SET status='sent' (or 'failed'), sent_at=now() WHERE id = ?
Worker -> Supabase: (If inapp_enabled) INSERT into inapp_notifications table OR simply rely on notifications table for UI polling
Worker -> Supabase Realtime: (if enabled) BROADCAST to channel `notifications:user:{user_id}` payload {notification_id, type, context}
Worker --> Event Source: task completed
[User Browser] -> (if subscribed to Realtime) receives payload -> updates UI badge/list
[User Browser] -> (if polling) GET /notifications/recent → Supabase: SELECT * FROM notifications WHERE user_id = ? ORDER BY sent_at DESC LIMIT 20
Supabase --> Browser: 200 OK {list}
Optional: User clicks “Mark as read” → Backend: UPDATE notifications SET is_read=true WHERE id = ?
```

### 7. Admin‑Triggered Scrape

Participants: Admin UI (frontend), Backend API (auth + admin check), Scheduler (or direct Celery task), Job Ingestion Worker, Apify, Supabase.

```
Admin Browser -> Backend: POST /admin/scraping/{source}/run (source=linkedin)
Backend -> Auth: validate JWT + admin role/service_role
Backend -> Scheduler (or Celery): enqueue job_ingest task for source
Scheduler -> Celery: assign to worker
Worker -> Apify: start actor for source
... (same as Job Ingestion flow from step 2 onward) ...
Worker --> Backend: task completed (success/failure count)
Backend --> Admin Browser: 200 OK {result summary}
```

### 8. Logout & Token Revocation (Optional)

Participants: Browser, Backend, Redis (revocation list).

```
Browser -> Backend: POST /auth/logout (refresh token in httpOnly cookie or body)
Backend -> Redis: GET revoked_jti:<jti from access token> (if using access token jti) OR add refresh token jti to revoked set with appropriate TTL
Backend -> Redis: SETEX revoked_jti:<jti> <ttl> (matching refresh token expiry)
Backend --> Browser: 200 OK {msg: "logged out"} (clears cookie)
```

*Note: If using short‑lived access tokens (15 min) and refresh token rotation, the access token expires naturally; revoking the refresh token prevents new access tokens from being issued.*

## How to Read the Diagrams

- Follow the arrows from top to bottom (time descending).
- Synchronous calls block the caller until a response is returned.
- Asynchronous messages (e.g., publishing to Redis, webhook responses) do not block the sender; the receiver processes the message when it pulls from the queue or receives the callback.
- Activation bars (thin rectangles on lifelines) indicate the period during which a component is actively processing a message.
- Alt/Loop/Optional frames can be added to show conditional branches, retries, or loops (e.g., polling Apify for completion).

## Extending Diagrams for New Features

When adding a new feature:
1. Identify the participants involved (new external service, new internal service, new data store).
2. Draw a new sequence diagram following the same layout.
3. Keep the diagram focused on a single scenario (e.g., “Generate skill‑gap analysis” or “Weekly embedding recompute”).
4. Include error paths (alt frames) for common failure modes (network timeout, validation failure, rate limit).
5. Store the diagram in `design/SEQUENCE_DIAGRAMS.md` as a markdown code block (mermaid or plantuml) or as a description as above.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*