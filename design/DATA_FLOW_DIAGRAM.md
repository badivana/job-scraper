# Data Flow Diagram

## Purpose

To illustrate the movement of data through the AI-Powered Job Finder system, from external sources (job boards, user uploads) to storage, processing, and ultimately to the user interface, highlighting where data is transformed, enriched, and consumed.

## Contents

- Overview
- Major Data Flows
  1. Job Ingestion Flow
  2. Resume Upload & Processing Flow
  3. Matching & Recommendation Flow
  4. AI Generation Flow
  5. Notification Flow
  6. Feedback & Analytics Flow
- Data Stores Involved
- Transformations & Enrichments
- Consistency & Guarantees

## Overview

Data enters the system from two primary sources: **external job feeds** (via Apify) and **user‑provided artifacts** (resumes, feedback). Once inside, it flows through a series of stages—validation, enrichment, storage, indexing, querying, and presentation—each of which may add value (metadata, embeddings, scores) before the data is consumed by the UI or other subsystems.

## Major Data Flows

### 1. Job Ingestion Flow
```
[Apify Actor] → (HTTP) → [Job Ingestion Celery Task]
    → Raw JSON → jobs_raw table
    → Normalization & Dedup → jobs table
    → Embedding Generation (Optional) → OpenAI → jobs.embedding vector
    → Notification: "job_new" Redis event → Matching Workers (update caches)
```
- **Transformations**: HTML stripping, salary parsing, location structuring, deduplication hash.
- **Storage**: `jobs_raw` (immutable archive), `jobs` (searchable, indexed).
- **Output**: New jobs become available for search/matching within seconds.

### 2. Resume Upload & Processing Flow
```
[User] → (HTTPS multipart/form-data) → [Resume Upload Endpoint]
    → Supabase Storage (bucket: resumes)  (store original file)
    → Text Extraction (pdfminer / docx) → raw_text
    → Section Parsing → structured JSON (experience, education, skills, certifications)
    → Skill Normalization → normalized skill IDs + confidence
    → Embedding Generation → OpenAI → 1536‑dim vector
    → Persist: resumes table (storage_key, raw_text, parsed_json, skill_vector, metadata)
    → (Optional) Invalidate user’s match cache
```
- **Transformations**: Text cleaning, section detection, skill mapping to ontology.
- **Storage**: Original file in Supabase Blobs; metadata and vector in `resumes` table.
- **Output**: Resume becomes searchable and can be used to generate matches and AI content.

### 3. Matching & Recommendation Flow
```
[User Browser] → GET /api/v1/jobs/search?[filters]
    → Auth & Rate Limiting → JobService.search
    → Read user.resumes (latest) → embedding vector
    → ANN Search: jobs table using pgvector <#> (cosine distance) → TOP‑K candidates
    → For each candidate: compute
          • cosine similarity
          • keyword Jaccard (skill sets)
          • recency decay (exponential, half‑life 14 days)
          • location preference (remote or radius)
      → weighted sum → final score
    → Rank, paginate, return JSON (job metadata + score + breakdown)
    → (Optional) Cache top‑N results in Redis (key: user:{id}:matches, TTL 5 min)
```
- **Data Sources**: `resumes.skill_vector`, `jobs` table (includes optional pre‑computed job embeddings).
- **Enrichments**: Adds score breakdown, recency factor, location match.
- **Output**: List of jobs with relevance scores for UI display.

### 4. AI Generation Flow
```
[User] → POST /api/v1/ai/{type} (type=cover-letter|cold-email|skill-gap)
    → Auth & Validation → Assemble Prompt:
          • System instruction (fixed template)
          • User data: resume_summary (from resumes.parsed_json) and
            job_description (from jobs.description_text) or skill sets
          • Optional parameters (temperature, max_tokens)
    → Call OpenAI Chat Completions (async)
    → Post‑process: strip markdown, enforce length, optionally convert to PDF
    → Persist: generated_documents table (user_id, job_id, type, content_text,
                storage_key for PDF)
    → Return: plain text (and, if requested, signed URL to PDF)
```
- **Transformations**: Prompt building, language model inference, output sanitization.
- **Storage**: Generated text in `generated_documents.content_text`; optional file in bucket `documents`.
- **Output**: Ready‑to‑use cover letter/email/analysis for the user.

### 5. Notification Flow
```
[Trigger] (e.g., job_new, application_status_change, manual broadcast)
    → Redis channel (notifications:user:{id} or notifications:broadcast)
    → Celery Worker (notification_send) consumes message
        → Retrieve template (from DB or file)
        → Render with context (Jinja2)
        → Send via SMTP/API (SendGrid/Mailgun/SES)
        → Log sent record to notifications table (status, timestamp)
        → (If realtime enabled) Publish to Supabase Realtime channel
[User] → (Optional) Receives in‑app alert via WebSocket / polling
```
- **Data Sources**: Notification templates (stored in DB or files), user preferences.
- **Enrichments**: Personalization (user name, job title, match score), localization.
- **Output**: Delivered email or in‑app notice.

### 6. Feedback & Analytics Flow
```
[User Action] (thumbs up/down on a job, click, application status change)
    → Frontend → POST /api/v1/feedback/{event}
    → Auth → Write to analytics_events table (event_type, entity_id, payload, timestamp)
    → Periodic ETL (Airflow, dbt, or simple cron) extracts events to
          analytics warehouse (Snowflake/BigQuery/Redshift) or a dedicated
          PostgreSQL schema for reporting.
    → Dashboard (Metabase, Grafana, PowerBI) visualizes:
          • Conversion funnel (search → save → apply → interview → offer)
          • Match score distribution
          • User retention & engagement
          • Skill demand trends from job descriptions
```
- **Transformations**: Enrichment with contextual data (user demographics, job attributes).
- **Storage**: Raw events in PostgreSQL; aggregated materialized views or external warehouse for reporting.
- **Output**: Insights for product decisions, performance monitoring, and bias audits.

## Data Stores Involved

| Store | Purpose | Technology |
|-------|---------|------------|
| **Supabase PostgreSQL** | Primary relational DB (users, resumes, jobs, applications, generated documents, notifications, audit, config, seeds) | PostgreSQL 15 + pgvector, uuid-ossp, btree_gin |
| **Supabase Storage** | Binary objects (resumes, generated docs, avatars, assets) | S3‑compatible bucket |
| **Redis** | Cache, rate limiting, Celery broker, pub/sub, session store (optional) | Redis 7 |
| **Object Storage (Backup)** | Encrypted logical dumps, backup assets | S3‑compatible (or Supabase bucket with versioning) |
| **External APIs** | Job boards (Apify), language models (OpenAI), email providers (SendGrid/Mailgun/SES) | HTTPS APIs |
| **Analytics Warehouse** (optional) | Long‑term trend analysis, BI | Snowflake/BigQuery/Redshift or dedicated PostgreSQL schema |
| **Monitoring Stack** | Metrics, logs, traces | Prometheus, Grafana, Loki, Tempo (optional) |

## Transformations & Enrichments

- **Text Cleaning**: Strip HTML, normalize whitespace, lower‑case for matching.
- **Entity Extraction**: spaCy + custom rules for skills, locations, dates.
- **Skill Normalization**: Mapping free‑text strings to canonical ontology IDs (ESCO/O*NET) via fuzzy matching.
- **Embedding Generation**: Convert raw text → dense vector via OpenAI’s `text‑embedding‑3‑small`.
- **Scoring Functions**: Cosine similarity, Jaccard index, exponential decay, fuzzy location match.
- **Data Enrichment**: Add derived fields (e.g., `is_recent`, `salary_norm`, `location_score`) during query time for ranking.
- **Aggregation**: Roll‑up raw events into time‑series tables for dashboards.

## Consistency & Guarantees

- **Within a Transaction**: Single‑request DB operations (e.g., creating a resume row) are atomic.
- **Eventual Consistency**: Between services (e.g., job inserted → embedding computed → cache updated) we rely on idempotent consumers and retries; temporary inconsistencies are resolved within seconds.
- **Durability**: All committed writes are persisted to Supabase PostgreSQL with synchronous replication; WAL archiving ensures recoverability to the second.
- **Idempotency**: External calls (Apify, OpenAI) are made with dedup keys or idempotency tokens where possible; internal consumers check flags before acting.
- **Delivery Guarantees**: Notifications use at‑least‑once semantics (Redis pub/sub + Celery retries); duplicate suppression via unique event IDs stored temporarily.

## Diagram Notation (if rendered)

If rendered as a Mermaid flowchart, the diagram would show:
- Rectangles for external systems (Apify, OpenAI, User UI, Email Provider).
- Cylinders for data stores (PostgreSQL, Supabase Storage, Redis, Blob Backup).
- Rounded boxes for processing steps (Ingestion Tasks, Services, Workers).
- Arrows labeled with protocols (HTTP/S, WebSocket, RPC, SQL, Pub/Sub).
- Decision points for validation, caching, and error handling.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*