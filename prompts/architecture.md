# Architecture Prompt

Use this prompt to generate a high-level architecture description for the AI-Powered Job Finder system.

```
You are an expert software architect. Describe the high-level architecture of a SaaS platform that scrapes job postings from multiple sources, matches them to user resumes using AI, provides a dashboard for tracking applications, and generates cover letters and outreach emails. Include the following components:

- Frontend: Next.js 15 with TypeScript, Tailwind CSS, shadcn/ui
- Backend: FastAPI (Python 3.12) with async SQLAlchemy, Pydantic v2
- Platform Services: Supabase (PostgreSQL with pgvector extension, Auth, Storage, Realtime)
- Caching & Queue: Redis (as broker for Celery and cache)
- Background Processing: Celery workers (job ingestion, resume processing, embedding batches, notifications)
- External Services: Apify (job scraping), OpenAI (LLM & embeddings), Email provider (SMTP/API)
- Dev & CI: Docker, GitHub Actions

Explain the data flow from job ingestion to resume embedding to matching, how authentication and authorization are handled via Supabase Auth and Row Level Security, and highlight scaling considerations (read replicas, worker autoscaling, caching). Also note security boundaries (HTTPS, JWT validation, least privilege).

Provide the answer in clear markdown with sections: Overview, Components, Data Flow, Security, Scaling, and Deployment Considerations.
```