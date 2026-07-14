# Scraping Engine

## Purpose

To outline how job postings are collected from external sources, processed, and stored in the system. The scraping engine relies on Apify for reliable, scalable extraction, and uses Celery (or equivalent) for orchestration, deduplication, and persistence into Supabase PostgreSQL.

## Contents

- Overview
- Architecture
- Workflow
- Deduplication & Normalization
- Error Handling & Retry
- Scheduling
- Monitoring & Alerting
- Data Retention
- Future Improvements

## Overview

Job data originates from public career sites (LinkedIn, Wellfound, Greenhouse, Lever, Indeed, company career pages). Rather than maintaining fragile in‑house scrapers, we delegate extraction to Apify actors—pre‑built, maintained scrapers that return structured JSON. The FastAPI backend (via a dedicated Job Service) triggers these actors, monitors their completion, retrieves the result dataset, and stores the normalized records.

All scraping activities are performed by background workers to avoid blocking HTTP request loops.

## Architecture

- **Apify Platform**: Provides actors for each source; we store actor IDs and input parameters (e.g., search queries, limits) in the database.
- **Job Service (FastAPI)**: Exposes internal API to start a scrape, poll for completion, download results, and invoke the ingestion pipeline.
- **Celery Workers**: Run tasks such as `ingest_jobs(source_id)` and `process_job_batch(batch)`.
- **Supabase PostgreSQL**: Holds raw JSON (`jobs_raw`) and cleaned, deduplicated records (`jobs`).
- **Redis**: Used as the Celery broker and for temporary caching of actor run IDs.
- **Monitoring**: Logs sent to a structured logging system; metrics exported to Prometheus.

## Workflow

1. **Schedule Trigger** (APScheduler or Celery Beat):
   - At a defined cron interval (e.g., every 2 h for LinkedIn, daily for company pages), a task `schedule_scrape(source)` is enqueued.
2. **Start Apify Actor**:
   - Job Service calls Apify API: `POST /actors/{actor_id}/runs` with input (e.g., keyword, location).
   - Receives a `run_id`.
3. **Monitor Completion**:
   - Poll Apify `/runs/{run_id}` until status is `SUCCEEDED` or `FAILED` (with exponential backoff, max 5 min timeout).
4. **Download Results**:
   - Retrieve the run’s dataset via `GET /runs/{run_id}/dataset/items` (JSON array).
5. **Ingestion Pipeline**:
   - **Raw Storage**: Insert each item into `jobs_raw` (columns: `id`, `source`, `raw_json` JSONB, `fetched_at`).
   - **Normalization**:
     - Extract `title`, `company`, `location` (string → JSONB with optional lat/long).
     - Clean description (strip HTML, normalize whitespace).
     - Parse salary via regex patterns → `salary_min`, `salary_max`, `currency`.
     - Determine `employment_type`, `remote_flag` from keywords.
     - Generate deduplication hash: `lower(title) || '|' || lower(company) || '|' || URL`.
   - **Deduplication**:
     - Check `jobs.hash_dedup` unique constraint; if conflict, treat as duplicate.
     - Optional fuzzy match against recent jobs (last 30 days) using `rapidfuzz.fuzz.token_set_ratio` > 90.
   - **Persist Clean Record**:
     - Insert into `jobs` with all normalized fields.
   - **Post‑Insert Hooks**:
     - Notify matching service via Redis channel `job_new` (payload: job ID) so that embeddings can be generated asynchronously.
6. **Completion**:
   - Record success/failure in a `scraping_runs` table (or update source metadata).
   - Send alerts if consecutive failures exceed threshold.

## Deduplication & Normalization

- **Exact Hash**: Prevents re‑ingesting the exact same posting (same URL and title/company).
- **Fuzzy Fallback**: Captures near‑duplicates where the source reposts with minor title variations.
- **Normalization Functions**:
  - `clean_location(raw)`: Splits by comma, trims, returns `{city, state?, country?}`.
  - `parse_salary(text)`: Looks for patterns like `$\\d[\\d,]+(?:-\\$\\d[\\d,]+)?`, converts to annual USD assuming 2080 work‑hours/year if needed.
  - `detect_remote(text)`: True if contains “remote”, “telecommute”, “work from home”.
  - `detect_employment_type(text)`: Maps keywords to enum values (full‑time, part‑time, contract, internship, temporary).

## Error Handling & Retry

- **Apify Failures**: If an actor fails (timeout, blocked, internal error), the task is retried with exponential backoff (max 5 attempts). Repeated failures go to a dead‑letter table `scraping_dlq` for manual inspection.
- **Network Issues**: HTTP calls to Apify use retry‑after status; overall task timeout prevents hanging workers.
- **Database Errors**: Unique constraint violations are caught and logged as duplicates; deadlocks trigger retry.
- **Data Validation**: Pydantic models validate normalized fields before insert; invalid rows are quarantined in a `jobs_invalid` table for review.

## Scheduling

- Managed by APScheduler embedded in the FastAPI process or a dedicated Celery Beat schedule.
- Each source has its own cron expression:
  - LinkedIn: `*/2 * * * *` (every 2 hours)
  - Wellfound: `0 3 * * *` (daily at 03:00 UTC)
  - Greenhouse: `0 4 * * *` (daily)
  - Lever: `0 5 * * *` (daily)
  - Indeed: `0 6 * * *` (daily)
  - Company Pages: `0 2 * * *` (daily)
- The schedule is stored in the database table `scheduled_scrapes` to allow runtime changes without code redeploy.

## Monitoring & Alerting

- **Logs**: Structured JSON (`source`, `run_id`, `status`, `item_count`, `duration_ms`).
- **Metrics**: Prometheus counters:
  - `scraping_jobs_total{source, outcome}`.
  - `scraping_items_total{source}`.
  - `scraping_duration_seconds{source}`.
- **Alerts** (via Alertmanager):
  - `scraping_failure_rate{source} > 0.1` over 5 min → critical.
  - `scraping_latency{source} > 300s` → warning.
  - No successful run for a source in `2 × interval` → warning.

## Data Retention

- **Raw JSON (`jobs_raw`)**: Retained for 30 days (configurable) for reprocessing; after that, partitioned and deleted.
- **Cleaned Jobs (`jobs`)**: Retained indefinitely unless marked `archived` (soft delete) after 90 days of inactivity; archived rows are excluded from default queries but可用于historical analysis.
- **Metadata**: Source run stats retained for 90 days.

## Future Improvements

- **Webhook Integration**: If Apify supports webhooks, replace polling with push‑based notifications to reduce latency.
- **Incremental Scraping**: Use `since` timestamps to request only new items from Apify where supported.
- **Source‑Specific Enhancements**: Add custom actors for niche job boards or company ATS feeds.
- **Change Detection**: Store a hash of the normalized job; on re‑scrape, compare to detect updates (e.g., salary change) and create a new version rather than duplicate.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*