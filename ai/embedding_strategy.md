# Embedding Strategy

## Purpose

To describe how embeddings are generated for resumes and job postings using OpenAI's text-embedding-3-small model, stored in Supabase PostgreSQL with the pgvector extension, and used for similarity matching.

## Contents

- Embedding Model
- Input Preparation
- Storage and Indexing
- Usage in Matching
- Updating Embeddings
- Cost and Performance Considerations

## Embedding Model

We use OpenAI's `text-embedding-3-small` model, which returns a 1536‑dimensional vector. This model offers a good balance of quality, cost, and latency for our use case.

## Input Preparation

For resumes, we concatenate the cleaned sections (summary, experience, skills) and truncate to the model’s maximum token limit (8191 tokens). For job postings, we concatenate title, company, and description, applying the same truncation.

## Storage and Indexing

Embeddings are stored in a `vector(1536)` column (`skill_vector` in the `resumes` table, and optionally `description_vector` in the `jobs` table). We create an ivfflat index with `lists = 100` (tunable) using the `vector_cosine_ops` operator for efficient Approximate Nearest Neighbor (ANN) search.

## Usage in Matching

During matching, we retrieve the top‑k nearest neighbor job vectors to a user’s resume vector using the `<=>` cosine distance operator, then apply a hybrid scoring formula that combines vector similarity with keyword, recency, and location signals.

## Updating Embeddings

Embeddings are regenerated when:
- A resume is uploaded or re‑parsed.
- A job posting is ingested (if we store job embeddings).
- The embedding model version changes (triggered via a batch job).

## Cost and Performance Considerations

- We enforce per‑user daily quotas on embedding generation to control OpenAI API costs.
- Recent embeddings are cached in Redis (TTL 1 hour) to avoid duplicate API calls.
- Batch embedding jobs run during off‑peak hours to recompute stale vectors.
