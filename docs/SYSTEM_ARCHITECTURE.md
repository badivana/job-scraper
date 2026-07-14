# System Architecture

## Purpose

Describes the high-level system architecture, showing how components interact, data flows, and the role of Supabase as the backend platform.

## Contents

- Overview
- Components
- Data Flow
- Integration Points
- Deployment View
- Security Considerations
- Scalability
- Evolution Path

## Overview

The AI-Powered Job Finder is a web application composed of a Next.js 15 frontend, a FastAPI backend, and Supabase providing managed PostgreSQL (with pgvector), authentication, file storage, and realtime capabilities. Redis is used for caching and task queuing. Background workers (Celery) handle scraping, matching, and notification jobs. Apify provides job scraping, and OpenAI provides language models.

## Components

- **Frontend (Next.js 15)**: UI built with TypeScript, Tailwind CSS, shadcn/ui; communicates with backend via REST/WebSocket.
- **Backend (FastAPI)**: Implements business logic: resume parsing, job matching, AI orchestration, scraper coordination, scheduling, analytics, API layer, validation.
- **Supabase**:
  - **PostgreSQL**: Primary database, includes pgvector extension for vector similarity search.
  - **Auth**: User authentication (email/password, OAuth providers) issuing JWT.
  - **Storage**: Secure object storage for resumes, generated documents, assets.
  - **Realtime**: Optional realtime updates for notifications.
  - **Backups**: Automated database backups.
- **Redis**: Caching layer, rate limiting, Celery broker.
- **Celery Workers**: Background jobs for scraping (via Apify), resume processing, embedding generation, notification dispatch.
- **Apify**: Scraping actors for LinkedIn, Wellfound, etc.
- **OpenAI**: GPT-4‑turbo for text generation, embedding models for resume/job vectors.

## Data Flow

1. **Job Ingestion**: Celery triggers Apify actors → raw JSON → FastAPI Job Service normalizes, deduplicates, stores in Supabase PostgreSQL.
2. **Resume Upload**: User uploads via frontend → FastAPI Resume Service stores file in Supabase Storage, extracts text, parses, generates embedding via OpenAI, stores vector in pgvector column.
3. **Job Matching**: FastAPI Matching Service queries Supabase PostgreSQL using pgvector ANN search, applies hybrid scoring, returns ranked jobs.
4. **Application Tracking**: User updates status via frontend → FastAPI records in Supabase PostgreSQL.
5. **Cover Letter Generation**: FastAPI AI Service calls OpenAI with resume + job description → returns generated text → stored in Supabase Storage; metadata in DB.
6. **Notifications**: Events published to Redis → Celery workers send email via SMTP or store in-app notifications in Supabase PostgreSQL.
7. **Realtime**: Supabase Realtime can push updates to frontend (optional).

## Integration Points

- **Frontend ↔ Backend**: REST API (JSON) over HTTPS; WebSocket for realtime features.
- **Backend ↔ Supabase**: PostgreSQL client (asyncpg) for DB operations; Supabase Auth via JWT verification; Supabase Storage SDK for file upload/download.
- **Backend ↔ Redis**: Redis client for caching, pub/sub, Celery broker.
- **Backend ↔ Apify**: HTTP API to start actors, poll for completion, fetch results.
- **Backend ↔ OpenAI**: HTTP API for completions and embeddings.

## Deployment View

- **Frontend**: Hosted on Vercel/Netlify or Docker container on Railway/Render.
- **Backend**: Docker container running FastAPI, deployed to Railway/Render or similar.
- **Supabase**: Managed cloud service (PostgreSQL, Auth, Storage, Realtime).
- **Redis**: Managed Redis (e.g., RedisCloud) or self-hosted.
- **CI/CD**: GitHub Actions builds Docker images, runs tests, pushes to registry, triggers deployment.

## Security Considerations

- Supabase Auth handles password hashing (argon2), email verification, OAuth providers.
- Row Level Security (RLS) policies enforce data access rules in PostgreSQL.
- Supabase Storage encrypts files at rest; signed URLs for secure access.
- Communication between services uses HTTPS; JWTs validated by backend.
- API rate limiting and input validation in FastAPI.

## Scalability

- Supabase PostgreSQL scales vertically; read replicas can be added for query load.
- Redis clustering for cache.
- Horizontal pod autoscaling for FastAPI workers based on CPU/QPS.
- Celery worker pool scales with queue depth.

## Evolution Path

- Migrate to Supabase Enterprise for advanced features.
- Consider migrating pgvector to dedicated vector DB if needed.
- Introduce feature flags, blue/green deployments.