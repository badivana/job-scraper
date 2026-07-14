# High Level Design

## Purpose

To describe the high‑level architectural structure of the AI‑Powered Job Finder, including major components, their responsibilities, and the interactions between them.

## Contents

- Overview
- Architectural Style & Patterns
- Core Components
- Data Flow
- Technology Stack Rationale
- Integration Points
- Deployment View
- Scalability & Availability
- Security Considerations
- Interface Contracts
- Evolution Path

## Overview

The AI‑Powered Job Finder is a modular, service‑oriented web application that combines job‑scraping microservices, AI‑driven matching, and a responsive frontend. The system is split into loosely coupled services that communicate via well‑defined REST/JSON APIs (with optional WebSocket for real‑time notifications). Data durability is provided by PostgreSQL, enhanced with pgvector for semantic search, while Redis serves as a fast cache and message broker.

## Architectural Style & Patterns

- **Microservices**: Each business capability (auth, job, resume, ai, notifications, scheduler, worker) is an independently deployable service.
- **API‑First**: All service interactions are defined by OpenAPI specifications; internal and external consumers adhere to the same contracts.
- **Event‑Driven (lightweight)**: Background jobs are published to a Redis‑based task queue (Celery) or via PostgreSQL LISTEN/NOTIFY for simple workflows.
- **Layered Presentation**: Frontend follows a presentation‑view‑model layer; UI components are built with React and TypeScript.
- **Domain‑Driven Design**: Bounded contexts align with service boundaries (User, Job, Resume, Matching, Notification, etc.).
- **Cache‑Aside**: Services first check Redis for hot data; miss triggers DB fetch and population of cache.
- **Circuit Breaker**: Calls to external APIs (Apify, OpenAI) are guarded by resilience libraries (e.g., tenacity) to avoid cascading failures.

## Core Components

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| **API Gateway** (optional) | Edge termination, routing, rate limiting, auth validation | Traefik / NGINX / FastAPI middleware |
| **Supabase Auth** | Managed authentication (email/password, OAuth, MFA, JWT issuance, refresh tokens) | Supabase (managed)
| **User Service** | Profile management, preferences, role handling (extends Supabase auth.users) | FastAPI, PostgreSQL (users table with FK to auth.users)
| **Job Service** | Ingestion, deduplication, storage, retrieval of job postings | FastAPI, PostgreSQL, Apify integration |
| **Resume Service** | Upload, parsing, skill extraction, embedding generation, storage | FastAPI, PostgreSQL, OpenAI embeddings, file storage (S3/Supabase) |
| **Matching Service** | Semantic and hybrid job‑to‑resume matching, scoring, ranking | FastAPI, pgvector, Redis (caching top‑k) |
| **AI Service** | Prompt engineering, LLM calls for cover letters, emails, skill‑gap analysis | FastAPI, OpenAI GPT‑4‑turbo, prompt templates |
| **Notification Service** | Email templating, delivery, in‑app notifications, preference management | FastAPI, Jinja2, SMTP/SendGrid, Redis pub‑sub |
| **Scheduler Service** | Cron‑like triggering of scraping, matching refresh, batch jobs | APScheduler / Celery Beat |
| **Worker Service** | Long‑running tasks: scraping actors execution, data cleaning, embedding batch updates | Celery workers, Apify SDK |
| **Frontend (Next.js App)** | UI rendering, client‑state management, API consumption | Next.js 14, React 18, TypeScript, TailwindCSS, shadcn/ui |
| **Dashboard Service** (could be part of frontend) | Admin and user analytics views | Same as frontend, with extra admin routes |
| **File Storage** | Binary objects (resumes, generated PDFs, assets) | AWS S3 / Supabase Storage |
| **Search Index** | Primary search via PostgreSQL + pgvector; optional external Elasticsearch for future scale | PostgreSQL |
| **Cache Layer** | Session caches, API response caches, rate‑limit counters | Redis |
| **Observability Stack** | Logging, metrics, tracing, alerting | Loki/Prometheus/Grafana, OpenTelemetry |
| **CI/CD Pipeline** | Build, test, lint, security scan, Docker image push, deployment | GitHub Actions, Docker, Helm (if K8s) |

## Data Flow

1. **Job Ingestion**  
   - Scheduler triggers a scraping task for a source.  
   - Worker launches the corresponding Apify actor, monitors completion, retrieves JSON result.  
   - Job Service normalizes, deduplicates, and stores raw + cleaned records in PostgreSQL.  
   - New jobs are published to a `job_created` Redis channel for downstream matching refresh.

2. **Resume Upload**  
   - User uploads file via frontend → Auth‑validated upload endpoint (Resume Service).  
   - Service stores the raw object in S3, extracts text, parses sections, normalizes skills.  
   - Embedding vector is generated via OpenAI and stored alongside the resume record.  
   - Updated resume triggers a `resume_updated` event; Matching Service may recompute matches for that user.

3. **Job Search & Matching**  
   - Frontend calls Job Service search API (full‑text + filters).  
   - For personalized matches, Frontend requests Matching Service with user ID.  
   - Matching Service retrieves user’s resume vector, queries pgvector for nearest jobs, applies hybrid scoring, returns ranked list.  
   - Results are cached in Redis for short‑term reuse (TTL 5 min).

4. **Application Tracking**  
   - User updates status via frontend → Job Service records transition in `applications` table with timestamps.  
   - Notification Service may send email/in‑app alert based on user preferences.

5. **Cover Letter Generation**  
   - User clicks “Generate” → AI Service receives resume text + job description, constructs LLM prompt, calls OpenAI, returns generated text.  
   - Result stored; user can download or regenerate.

6. **Notifications**  
   - Events (new match, status change) are published to Redis channels.  
   - Notification Service consumes, renders templates, dispatches via email or updates in‑app feed.

7. **Admin Operations**  
   - Admin Dashboard reads aggregated metrics from PostgreSQL (or materialized views) and Redis.  
   - Controls (e.g., trigger scrape) invoke Scheduler Service via API.

## Technology Stack Rationale

- **Next.js**: Hybrid static/server‑rendering, excellent SEO, built‑in routing, API routes if needed.  
- **React + TypeScript**: Strong typing, component reuse, large ecosystem.  
- **TailwindCSS + shadcn/ui**: Utility‑first styling with accessible primitives.  
- **FastAPI**: High‑performance async Python, automatic OpenAPI docs, data validation via Pydantic.  
- **PostgreSQL**: ACID‑compliant, rich extensions (pgvector, Listen/Notify), proven at scale.  
- **pgvector**: Enables efficient K‑NN search for embeddings without separate vector DB.  
- **Redis**: Low‑latency cache, pub/sub for lightweight events, durable queues via Redis‑based Celery.  
- **Celery/APScheduler**: Mature task queues with retry, scheduling, and monitoring.  
- **OpenAI GPT‑4‑turbo**: State‑of‑the‑art language generation and embedding models (cost‑effective via fine‑tuned usage).  
- **Apify**: Reliable, scalable scraping platform; avoids maintaining fragile scrapers.  
- **Docker**: Consistency across dev, test, prod; simplifies CI/CD.  
- **GitHub Actions**: Integrated with repository, supports workflow automation of‑fer‑self‑hosted runners for scalability.  
- **Observability Stack**: Loki/Prometheus/Grafana provide full‑stack monitoring; OpenTelemetry enables distributed tracing.  

## Integration Points

- **Apify** → Worker Service (starts actors, reads dataset).  
- **OpenAI** → AI Service (embeddings, completions).  
            - **OAuth Providers** → Supabase Auth (Google, GitHub, etc.) (handled by frontend).
- **Email Provider** → Notification Service (SMTP or HTTP API).  
            - **Object Storage** → Supabase Storage (resumes, generated documents, avatars, assets).
- **Payment Gateway** (future) → Billing Service (stubbed).  
- **Third‑Party ATS** (future) → Webhook endpoint in Job Service for application status sync.  

## Deployment View

### Development
- Docker Compose orchestrates all services locally with hot‑code reload for frontend.  
- SQLite may replace PostgreSQL for quick iteration (optional) – SQLite is only for local development/testing; production must use Supabase PostgreSQL.  

### Testing
- Separate compose file with test databases; Cypress for end‑to‑end, Jest for unit/frontend.  

### Staging / Production
- **Container Orchestration**: Kubernetes (managed: EKS, GKE, AKS) or Docker‑Swarm for simplicity.  
- **Ingress**: NGINX Ingress Controller with TLS termination.  
- **Service Mesh** (optional): Istio for traffic policies, mTLS.  
- **Databases**:  
  - Primary PostgreSQL (managed: Amazon RDS/Aurora, Cloud SQL, or self‑hosted with Patroni).  
  - Read replica(s) for analytics/reporting.  
- **Cache**: Redis Cluster (managed: Elasticache, Azure Redis, or Redis‑Enterprise).  
- **Object Storage**: AWS S3 (or compatible) with lifecycle policies.  
- **Secrets**: AWS Secrets Manager / HashiCorp Vault / Kubernetes Secrets.  
- **Monitoring**: Prometheus Operator scraping service endpoints; Grafana dashboards; Loki for logs.  
- **Alerting**: Alertmanager routing to Slack/email.  
- **CI/CD**: GitHub Actions builds Docker images, pushes to registry, ArgoCD / Flux for GitOps deployment or simple kubectl rollout.  
- **Blue‑Green / Canary**: Implemented via Kubernetes Deployments with `strategy: rollingUpdate` and feature flags (LaunchDarkly or home‑grown).  

## Scalability & Availability

- **Horizontal Pod Autoscaling**: Based on CPU utilization and custom metrics (queue length).  
- **Database Scaling**:  
  - Read replicas for query‑heavy workloads (search, matching).  
  - Connection pooling via PgBouncer.  
  - Partitioning of `jobs` table by date (monthly) for archival.  
- **Cache Sharding**: Redis Cluster spreads keys across nodes.  
- **Worker Scaling**: Number of Celery workers tuned to I/O‑bound scraping vs CPU‑intensive embedding batch jobs.  
- **Rate Limiting**: Gateway enforces per‑IP and per‑user limits; external API calls use token bucket.  
- **Failure Isolation**: Circuit breakers prevent overload of Apify/OpenAI; fallback to cached results or degraded UI (show latest known jobs).  
- **Data Replication**: PostgreSQL streaming replication with synchronous commit for critical transactions (e.g., user creation).  
- **Backup Strategy**: Daily logical dump (pg_dump) + continuous WAL archiving; point‑in‑time recovery tested quarterly.  
- **Disaster Recovery**: Multi‑AZ deployment; automated failover via PatronI or cloud‑managed HA.  

## Security Considerations

- **Transport Security**: TLS 1.2+ everywhere; enforce HSTS.  
- **Authentication**: Handled by Supabase Auth (includes password hashing, MFA via TOTP).
- **Authorization**: RBAC enforced at API gateway and service layers.  
- **Input Validation**: Pydantic models; sanitize HTML to prevent XSS.  
- **Output Encoding**: Context‑aware escaping in Jinja2 and React (dangerouslySetInnerHTML avoided).  
- **Secrets Management**: No hard‑coded credentials; injected via environment or secret store.  
- **Dependency Scanning**: `safety` and `bandit` in CI; Dependabot for updates.  
- **API Rate Limiting**: Protect against abuse; integrate with Fail2Ban‑like behavior.  
- **Logging Sanitization**: Mask PII, tokens, passwords.  
- **Vulnerability Testing**: Regular DAST (OWASP ZAP) and manual pen‑test before major releases.  
- **Data Privacy**: GDPR‑ready flows for access, rectification, erasure; data minimization (store only needed fields).  
- **Secure Headers**: CSP, X‑Frame‑Options, X‑Content‑Type‑Options, Referrer‑Policy.  

## Interface Contracts

Each service exposes an OpenAPI 3.0 document (generated from FastAPI routes). Key contracts include:

- **Auth API**: `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`  
- **User API**: `/users/{id}`, `/users/{id}/preferences`  
- **Job API**: `/jobs/search`, `/jobs/{id}`, `/jobs/{id}/apply`  
- **Resume API**: `/resumes/upload`, `/resumes/{id}`, `/resumes/{id}/embed`  
- **Matching API**: `/matching/{user_id}?limit=20&offset=0`  
- **AI API**: `/ai/cover-letter`, `/ai/cold-email`, `/ai/skill-gap`  
- **Notification API**: `/notifications/prefs`, `/notifications/recent`  
- **Admin API**: `/admin/users`, `/admin/scraping/{source}/run`  

Internal service‑to‑service calls use the same contracts; versioning via `/v1/...` path.

## Evolution Path

- **Monolith‑to‑Micro‑Services**: Start with a modular monolith (single repo, distinct packages); split into separate Docker services as load increases.  
- **Vector Search Upgrade**: Evaluate dedicated vector DB (Milvus, Weaviate, Pinecone) if pgvector limits are reached.  
- **Streaming Architecture**: Replace periodic scraping with real‑time webhooks from Apify (if supported).  
- **Feature Flags**: Introduce LaunchDarkly or Unleash for gradual rollouts.  
- **ML Ops**: Containerize custom models (skill taxonomy embedding) and serve via Triton or SageMaker endpoints.  
- **Global Distribution**: Deploy frontend via CDN (Cloudflare, Vercel) for edge caching; backend regions behind global load balancer.  
- **Analytics**: Add Snowflake/BigQuery for OLAP workloads; DBT for transformations.  

---  
*Document Version: 1.0*  
*Last Updated: 2026‑07‑14*