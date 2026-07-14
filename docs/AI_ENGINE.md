# AI Engine

## Purpose

To describe the AI‑powered components of the Job Finder: resume parsing, skill extraction, embedding generation, job matching scoring, and generative features (cover letters, cold emails, skill‑gap analysis). The engine relies on OpenAI LLMs and the pgvector extension hosted in Supabase PostgreSQL.

## Contents

- Overview
- Core Capabilities
- Embedding Strategy
- Text Generation
- Safety & Moderation
- Performance & Cost Controls
- Integration Points
- Future Enhancements

## Overview

The AI Engine is a set of services and libraries invoked by the FastAPI backend. It does **not** train custom models; instead, it leverages pretrained OpenAI models (GPT‑4‑turbo for generation, text‑embedding‑3‑small for embeddings) and stores the resulting vectors in a `vector(1536)` column indexed with ` ivfflat ` for efficient Approximate Nearest Neighbor (ANN) search.

All AI interactions are asynchronous and rate‑limited per user to control costs.

## Core Capabilities

1. **Resume Processing**
   - Text extraction from PDF/DOCX (via `pdfminer.six`, `python-docx`, optional OCR).
   - Section segmentation (contact, summary, experience, education, skills, certifications).
   - Skill extraction (named entity + taxonomy mapping).
   - Embedding generation: concatenate cleaned sections (summary + experience + skills) → truncated to model token limit → request embedding from OpenAI → store `skill_vector`.

2. **Job Embedding**
   - For each ingested job posting, compute a description embedding (title + company + description) using the same embedding model.
   - Store in `jobs` table (optional) or compute on‑the‑fly during matching.

3. **Matching Scoring**
   - **Vector similarity**: cosine similarity between resume `skill_vector` and job description vector via `<=>` operator.
   - **Keyword boost**: Jaccard similarity of normalized skill sets.
   - **Recency decay**: exponential decay based on days posted (half‑life 14 days).
   - **Location preference**: boolean match or distance‑based scaling.
   - Final score = α·cosine + β·jaccard + γ·recency + δ·location (weights configurable per user).

4. **Generative Features**
   - **Cover Letter**: System prompt “You are a professional cover letter writer.” + user prompt with résumé summary and job description.
   - **Cold Email / LinkedIn Message**: Shorter, tone‑adjustable.
   - **Skill‑Gap Analysis**: Identify skills in job description missing from résumé; suggest learning resources.

5. **Safety & Moderation**
   - All prompts and outputs pass through OpenAI’s moderation endpoint.
   - Profanity filter applied to generated text before storage.

## Embedding Strategy

- **Model**: `text-embedding-3-small` (1536 dimensions, cost‑effective).
- **Input Size**: Max 8192 tokens; we truncate/reserve space for system prompt when generating embeddings for generation tasks.
- **Storage**: `vector(1536)` column with `ivfflat` index (`lists = 100`). Supports `ORDER BY embedding <=> query_vector LIMIT k`.
- **Update Policy**: Embeddings are regenerated when:
  - Resume is re‑uploaded or edited.
  - Job description changes (unlikely after ingestion).
  - Embedding model version changes (triggered via admin batch job).

## Text Generation

- **Model**: `gpt-4o-mini` (or `gpt-4-turbo` for higher quality) with temperature 0.7 for creative tasks, 0.2 for factual extraction (skill gap).
- **Max Tokens**: 500 for cover letters, 150 for emails, 300 for skill‑gap analysis.
- **Prompt Engineering**: Uses Jinja2 templates stored in `prompts/ai.md` (see prompt library). Variables: `resume_summary`, `job_description`, `tone`, `max_length`.
- **Post‑Processing**:
  - Strip markdown fences.
  - Ensure plain text; optionally convert to PDF via `weasyprint` or browser print.
  - Store generated text in `generated_documents.content_text` and file version in Supabase Storage bucket `documents`.

## Performance & Cost Controls

- **Per‑User Quotas**:
  - Embedding generation: 100 per day (resume edits).
  - Text generation: 50 per day (cover letters/emails).
- **Rate Limiting**: 4 req/s per IP via API gateway; internal services use token bucket.
- **Caching**: Recent embeddings stored in Redis (TTL 1 h) to avoid duplicate OpenAI calls.
- **Batch Jobs**: Nightly recompute embeddings for stale records using `SELECT` + `UPDATE` with `WHERE updated_at < now() - interval '7 days'`.

## Integration Points

| Component | Interaction |
|-----------|-------------|
| **FastAPI → AI Service** | Internal HTTP (or direct function calls) POST `/ai/embed`, `/ai/generate`. |
| **AI Service → OpenAI** | HTTPS API calls with API key stored in secret manager (Supabase settings or vault). |
| **AI Service → Supabase** | Read/write `resumes.skill_vector`, `jobs.description_vector` (optional), `generated_documents`. |
| **AI Service → Redis** | `GET/SET` embedding cache keyed by content hash. |
| **AI Service → Celery** | Heavy embedding batch jobs dispatched as tasks. |

## Future Enhancements

- Fine‑tune a domain‑specific embeddings model on job‑resume pairs for better relevance.
- Introduce adversarial training to reduce bias in generated cover letters.
- Add multilingual support (translate résumé/job description before embedding).
- Allow users to upload multiple résumé versions and select per‑job targeting.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*