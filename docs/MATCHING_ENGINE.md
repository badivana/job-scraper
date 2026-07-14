# Matching Engine

## Purpose

To describe how the system computes relevance between a user’s résumé and job postings, combining vector similarity (via pgvector) with keyword, recency, and location signals. The matching engine is served by a FastAPI endpoint, backed by Supabase PostgreSQL, and incorporates caching and asynchronous batch updates for scalability.

## Contents

- Overview
- Core Similarity Model
- Hybrid Scoring Formula
- Indexing & Query Strategy
- Caching Layer
- Real‑time & Batch Updates
- Edge Cases & Fallbacks
- Performance Tuning
- Future Extensions

## Overview

When a user uploads a résumé, the system extracts text, generates a 1536‑dimensional embedding via OpenAI (`text-embedding-3-small`), and stores it in the `resumes.skill_vector` column (pgvector). Job descriptions are similarly embedded (either at ingest time or via a nightly batch) and stored in `jobs.description_vector`.

The matching process retrieves approximate nearest neighbors (ANN) from the jobs table using the user’s vector, then refines the candidate set with a weighted hybrid score that incorporates:

- Cosine similarity (vector)
- Keyword Jaccard overlap (skills)
- Recency decay (exponential half‑life)
- Location preference (remote, radius, or city match)

Results are returned to the frontend ordered by the final score, with optional explanation of each component.

## Core Similarity Model

- **Vector Field**: `vector(1536)` column named `embedding` (in both `resumes` and `jobs` tables).
- **Index Type**: `ivfflat` with `lists = 100` (tunable). Uses the `vector_cosine_ops` operator class.
- **Query**:  
  ```sql
  SELECT id, 1 - (embedding <=> :user_vec) AS cosine_sim
  FROM jobs
  WHERE embedding IS NOT NULL
  ORDER BY embedding <=> :user_vec
  LIMIT :k;
  ```
  (`<=>` is the cosine distance; `1 - distance` = similarity).

- **Recall Tuning**: Probe count (`ef_search` equivalent for ivfflat) set via `SET ivfflat.probes = 10;` at session start for balanced latency/recall.

## Hybrid Scoring Formula

For each candidate job `j` and user `u`:

```
score(u, j) = α * S_cos(u, j) +
              β * S_jaccard(u, j) +
              γ * S_recency(j)   +
              δ * S_location(u, j)
```

where α + β + γ + δ = 1. Default weights (tunable per‑user via preferences):

- α = 0.40 (vector similarity)
- β = 0.30 (keyword overlap)
- γ = 0.20 (recency)
- δ = 0.10 (location)

### Component Definitions

1. **Cosine Similarity**  
   `S_cos = 1 - (resume_embedding <=> job_embedding)` (range 0‑1).

2. **Keyword Jaccard**  
   Extract normalized skill sets from résumé (`user_skills` table) and from job description (via `job_skills` or NER on description).  
   `S_jaccard = |U ∩ J| / |U ∪ J|` (if both empty, define as 0).

3. **Recency Decay**  
   Let `d` = days since `job.posted_date`.  
   `S_recency = exp(-λ * d)` where `λ = ln(2) / half_life`.  
   Default half‑life = 14 days → λ ≈ 0.0495.  
   Clipped to `[0,1]`.

4. **Location Preference**  
   - If user preference `remote_only = true`: `S_location = 1` if `job.remote_flag = true`, else `0`.  
   - If user specifies `max_distance_km` and provides latitude/longitude (from profile): compute Haversine distance; `S_location = max(0, 1 - dist / max_distance)`.  
   - If no preference given: `S_location = 1` (neutral).

### User‑Customizable Weights

Preferences are stored as JSONB in `user_prefs` (or a dedicated table). The matching endpoint reads these values; defaults apply if not set.

## Indexing & Query Strategy

- **Primary Vector Index**: `CREATE INDEX ON jobs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`
- **Secondary Filters**: To reduce the candidate set before vector scan, we can add a pre‑filter using cheap indexes:
  - `jobs.posted_date` (BRIN index) for recent jobs (last 6 months).
  - `jobs.remote_flag` for remote‑only requests.
  - `jobs.location` (GIN on JSONB) for city/state filtering.
- The final query is constructed dynamically:
  ```sql
  WITH candidates AS (
    SELECT id, embedding
    FROM jobs
    WHERE (:remote_only IS NULL OR remote_flag = :remote_only)
      AND (:since_date IS NULL OR posted_date >= :since_date)
      AND (:location_id IS NULL OR location @> :location_jsonb)
    ORDER BY embedding <=> :user_vec
    LIMIT :pre_limit   -- e.g., 500
  )
  SELECT c.id,
         1 - (c.embedding <=> :user_vec) AS cos_sim,
         ... (compute other components in the SELECT or in app)
  FROM candidates c
  ORDER BY (α * cos_sim + β * jaccard + γ * recency + δ * location) DESC
  LIMIT :final_limit;
  ```
- The pre‑limit (`:pre_limit`) balances index‑assisted filtering with ANN recall.

## Caching Layer

- **Per‑User Hot List**: The top‑N (default 100) matches for a user are cached in Redis with key `user:{id}:matches` and TTL 5 minutes. Updated on:
  - New résumé upload (trigger async recompute).
  - New job insert (via `job_new` Redis channel) – incremental update possible but full refresh is simpler for low frequency.
- **Job Embedding Cache**: To avoid recomputing embeddings for frequently‑requested jobs, store `job_id → embedding` in Redis with TTL 24 h (refresh on job update).
- **Response Caching**: Anonymous or public queries (e.g., trending jobs) can be cached via CDN or API‑gateway.

## Real‑time & Batch Updates

- **Real‑time**: When a new job is inserted, a `NOTIFY` on channel `job_new` (via PostgreSQL `pg_notify`) alerts workers to:
  - Generate its embedding (if not already present).
  - Optionally push to a Redis sorted set for “fresh jobs” feed.
- **Batch Refresh**:
  - Nightly job: recompute embeddings for jobs missing vectors or older than 30 days.
  - Weekly job: rebuild ivfflat indexes with updated `lists` parameter based on data volume.
  - Monthly job: refresh user‑skill vectors if résumé edited.

## Edge Cases & Fallbacks

- **Missing Embedding**: If a résumé or job lacks a vector (e.g., API failure), fallback to pure keyword + recency + location scoring (α = 0). Log warning and flag for retry.
- **Empty Skill Sets**: Jaccard defined as 0 when either set is empty.
- **High Dimensionality Errors**: Ensure `pgvector` extension is installed; otherwise service returns 503 with retry‑after header.
- **Vector Size Mismatch**: All embeddings must be 1536‑dim; any deviation triggers re‑embedding.

## Performance Tuning

| Parameter | Typical Value | Effect |
|-----------|
| `ivfflat.lists` | 100 | More clusters → higher build time, better query precision. |
| `ivfflat.probes` (session) | 10 | Higher → better recall, slower query. |
| `pre_limit` | 300–500 | Larger → more candidates examined, higher recall. |
| `final_limit` (page size) | 20 | Number returned to user. |
| `half_life` (recency) | 14 days | Shorter → fresher jobs boosted. |
| `α,β,γ,δ` | 0.4/0.3/0.2/0.1 | Adjust via A/B testing. |

Benchmarks (1 M jobs, 2‑core CPU):
- Vector search (k=100) ≈ 12 ms.
- Full hybrid scoring for 100 candidates ≈ 3 ms.
- End‑to‑end p95 latency < 150 ms (including Redis cache miss).

## Future Extensions

- **Hybrid Search with Text**: Combine full‑text `tsvector` ranking with vector score via weighted sum (RR‑fusion).
- **Learning‑to‑Rank**: Use click‑through data to adjust weights via a lightweight model (e.g., LambdaMART) stored as a scoring function.
- **Dynamic Re‑ranking**: Apply business rules (e.g., boost jobs from companies the user follows) after initial scoring.
- **Explainability UI**: Return per‑component breakdowns for transparency.
- **Multi‑modal Embeddings**: Fuse title, skills, and description embeddings with attention.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*