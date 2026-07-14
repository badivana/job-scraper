# Architecture Decision Records

This file records significant architectural decisions made for the AI-Powered Job Finder project. Each decision follows the format:

- **Decision**: A concise statement of the decision.
- **Reason**: The justification for the decision.
- **Alternatives Considered**: Other options that were evaluated.
- **Trade-offs**: The pros and cons of the chosen approach.
- **Date**: The date the decision was made (or last revised).

All decisions are recorded as of the project's documentation update date (2026-07-14) unless otherwise noted.

---

## ADR 001: Use Supabase as the Backend Platform

**Decision**: Use Supabase for managed PostgreSQL (with pgvector), Authentication, Storage, and Realtime services.

**Reason**: To reduce operational overhead by leveraging a managed backend that provides essential services (database, auth, file storage, realtime) with built-in security, scalability, and compliance features. This allows the team to focus on core product features rather than infrastructure management.

**Alternatives Considered**:
- Self-hosted PostgreSQL with separate Auth service (e.g., Auth0, Firebase Auth) and file storage (e.g., AWS S3).
- Using AWS/RDS with managed services for each component (RDS, Cognito, S3).
- Using Firebase/Firestore as a unified backend.
- Using a traditional self-managed stack (PostgreSQL, Redis, custom auth, MinIO for storage).

**Trade-offs**:
- **Pros**: Reduced DevOps burden, integrated services (auth rules integrated with Row Level Security), predictable pricing, built-in scalability, and compliance (GDPR ready).
- **Cons**: Vendor lock-in to Supabase, less control over low-level database tuning, potential cost at scale, and dependency on Supabase's feature roadmap.

---

## ADR 002: Use Next.js 15 with TypeScript for the Frontend

**Decision**: Build the frontend using Next.js 15, React 18, and TypeScript.

**Reason**: To leverage server-side rendering (SSR) and static site generation (SSO) for SEO and performance, strong TypeScript support for maintainability, and the growing ecosystem and community support.

**Alternatives Considered**:
- Create React App (CRA) with a separate Express server.
- Gatsby.js for static site generation.
- Remix.
- Pure React with Next.js-like features via custom setup.

**Trade-offs**:
- **Pros**: Excellent developer experience, built-in routing and optimization, SEO-friendly, incremental static regeneration (ISR), and API routes for simple backend needs.
- **Cons**: Slightly larger bundle size compared to minimal React setup, learning curve for new team members, and reliance on Vercel/Netlify for optimal deployment (though adaptable to other hosts).

---

## ADR 003: Use FastAPI for the Backend Service

**Decision**: Implement the backend API using FastAPI (Python 3.12) with async SQLAlchemy and Pydantic v2.

**Reason**: To achieve high performance with asynchronous request handling, automatic API documentation, data validation, and seamless integration with Python's data science and AI ecosystem.

**Alternatives Considered**:
- Django REST Framework (DRF).
- Flask with Flask-RESTful or Flask-RESTX.
- Node.js with Express or NestJS.
- Go with Gin or Echo.

**Trade-offs**:
- **Pros**: High performance (Starlette/Uvicorn), automatic OpenAPI docs, strong typing with Pydantic, easy integration with ML/AI libraries (e.g., OpenAI, sentence-transformers), and async support for I/O-bound tasks.
- **Cons**: Smaller ecosystem compared to Node.js/Django, fewer third-party packages for certain niche functionalities, and asynchronous learning curve for developers unfamiliar with async Python.

---

## ADR 004: Use Docker Containers for All Services

**Decision**: Containerize the frontend, backend, and worker services using Docker, with docker-compose for local development.

**Reason**: To ensure consistency across development, testing, and production environments, simplify dependency management, and enable scalable deployment orchestration.

**Alternatives Considered**:
- Running services directly on host/Virtual Machines (VMs).
- Using language-specific version managers (e.g., pyenv, nvm) without containers.
- Using package managers like Conda or Poetry for isolation.

**Trade-offs**:
- **Pros**: Environment reproducibility, isolation of dependencies, simplified CI/CD, and compatibility with orchestration platforms (Kubernetes, Docker Swarm).
- **Cons**: Slight overhead in disk usage and startup time, need to learn Docker concepts, and potential complexity in debugging containerized applications.

---

## ADR 005: Use GitHub Actions for CI/CD

**Decision**: Implement Continuous Integration and Continuous Deployment pipelines using GitHub Actions.

**Reason**: To automate testing, building, and deployment directly from the repository, leveraging tight integration with GitHub and features like caching, secrets management, and environment protection.

**Alternatives Considered**:
- GitLab CI/CD.
- Jenkins.
- CircleCI.
- Travis CI.
- Custom scripts with SSH deployment.

**Trade-offs**:
- **Pros**: Seamless GitHub integration, free tier for public/private packages, matrix builds, self-hosted runners for custom environments, and extensive community support.
- **Cons**: Vendor lock-in to GitHub ecosystem, potential limitations on runner minutes for private repositories, and less flexibility compared to self-hosted solutions like Jenkins.

---

## ADR 006: Use Apify for Job Scraping

**Decision**: Utilize Apify actors to scrape job postings from various sources (LinkedIn, Indeed, company career pages, etc.).

**Reason**: To avoid building and maintaining fragile in-house scrapers, benefit from Apify's maintenance of adapters to site changes, and gain scalability through their cloud infrastructure.

**Alternatives Considered**:
- Developing custom scrapers using libraries like Scrapy, BeautifulSoup, or Puppeteer.
- Using other scraping-as-a-service platforms (e.g., ScraperAPI, Octoparse).
- Relying solely on job APIs (e.g., LinkedIn API, Indeed Publisher Program) where available.

**Trade-offs**:
- **Pros**: Reduced development and maintenance burden, high reliability due to Apify's anti-blocking measures, scalability, and access to many pre-built actors.
- **Cons**: Ongoing cost per scrape, less control over the scraping logic, potential data latency, and dependency on Apify's service availability and pricing.

---

## ADR 007: Use OpenAI GPT-4-turbo and text-embedding-3-small for AI Features

**Decision**: Leverage OpenAI's GPT-4-turbo model for text generation (cover letters, emails) and text-embedding-3-small for generating vector embeddings of résumés and job descriptions.

**Reason**: To utilize state-of-the-art large language models (LLMs) and embedding models that provide high-quality, coherent text generation and semantic understanding without the need for in-house model training or infrastructure.

**Alternatives Considered**:
- Open-source LLMs (e.g., Llama 2, Mistral) self-hosted on GPU infrastructure.
- Other proprietary APIs (e.g., Anthropic Claude, Cohere, Azure OpenAI).
- Traditional TF-IDF or BM25 text matching without embeddings.
- Fine-tuning a smaller model on domain-specific data.

**Trade-offs**:
- **Pros**: Cutting-edge performance, minimal infrastructure management, continuous model improvements from OpenAI, and strong multilingual support.
- **Cons**: Ongoing API costs, rate limits, potential latency, data privacy considerations (data sent to OpenAI), and vendor lock-in to a specific provider.

---

## ADR 008: Use Redis for Caching and Celery Broker

**Decision**: Employ Redis as an in-memory data store for caching frequently accessed data (e.g., embeddings, user preferences) and as the message broker for Celery.

**Reason**: To achieve low-latency data access for hot paths and reliable task queuing for background workers, leveraging Redis's speed, persistence options, and rich data structures.

**Alternatives Considered**:
- Using Memcached for caching and RabbitMQ/RQ for task queuing.
- Using a single PostgreSQL instance for both caching and queuing (via LISTEN/NOTIFY or periodic polling).
- Using Amazon ElastiCache (Redis) or Azure Cache for Redis in cloud environments.

**Trade-offs**:
- **Pros**: High performance, support for complex data types (hashes, sets, lists), built-in replication and persistence (AOF/RDB), and wide client library support.
- **Cons**: Adds another moving part to the architecture, requires monitoring and tuning, and potential data loss if persistence is not configured correctly (mitigated by using AOF).

---

## ADR 009: Use Celery for Background Task Processing

**Decision**: Use Celery as the distributed task queue to handle asynchronous operations such as job scraping, embedding generation, resume processing, and notification dispatch.

**Reason**: To decouple long-running or resource-intensive tasks from the request-response cycle, enabling better scalability, fault tolerance, and resource utilization.

**Alternatives Considered**:
- Using RQ (Redis Queue) for simpler Python-based queuing.
- Building a custom task queue with Redis or PostgreSQL.
- Using cloud-native solutions like AWS SQS + Lambda or Google Cloud Pub/Sub + Cloud Functions.
- Using synchronous processing with timeout-based user notifications (not preferred for scalability).

**Trade-offs**:
- **Pros**: Mature Python ecosystem, supports scheduling (Celery Beat), retries, routing, and monitoring (via Flower). Integrates well with Redis as a broker.
- **Cons**: Adds operational complexity (monitoring workers, managing queues), potential overhead for very simple tasks, and requires careful configuration of concurrency and timeouts.

---

## ADR 010: Use pgvector for Vector Similarity Search in PostgreSQL

**Decision**: Store résumé and job embeddings as `vector(1536)` columns in PostgreSQL and use the pgvector extension with an IVFFLAT index for efficient Approximate Nearest Neighbor (ANN) search.

**Reason**: To perform fast, scalable semantic search directly within the primary database, avoiding the need for a separate vector database and simplifying data consistency and transactional guarantees.

**Alternatives Considered**:
- Using a dedicated vector database (e.g., Pinecone, Milvus, Weaviate, Qdrant).
- Using PostgreSQL with the `hnsw` extension (if available) or experimenting with other ANN indexes.
- Performing similarity search in the application layer after fetching candidate sets (less efficient at scale).

**Trade-offs**:
- **Pros**: ACID transactions, single source of truth for data, familiarity with PostgreSQL operators for operational overhead, seamless integration with relational data (e.g., filtering by job metadata before vector search), and mature ecosystem with monitoring and backup tools.
- **Cons**: May not match the ultra-low latency or massive scale of purpose-built vector databases, requires tuning of index parameters (lists, probes), and memory usage scales with dataset size.

---

## ADR 011: Use UUIDs as Primary Keys

**Decision**: Use Universally Unique Identifiers (UUIDs) as the primary key for all database tables.

**Reason**: To ensure global uniqueness across distributed systems (e.g., when merging data from multiple sources), avoid exposing sequential IDs for security reasons, and simplify sharding or replication scenarios.

**Alternatives Considered**:
- Using auto-incrementing integers (SERIAL/BIGSERIAL).
- Using composite natural keys (e.g., job URL + source).
- Using snowflake-inspired IDs (e.g., Twitter Snowflake, Sonyflake).

**Trade-offs**:
- **Pros**: Globally unique, resistant to enumeration attacks, suitable for distributed generation (e.g., offline sync), and no need for coordination on inserts.
- **Cons**: Larger storage size (16 bytes vs 4/8 bytes for int), slightly slower indexing, and less human-readable in debugging.

---

## ADR 012: Implement Row Level Security (RLS) for Data Access Control

**Decision**: Enable Row Level Security (RLS) on all tables containing user-specific data and enforce policies using `auth.uid()` from Supabase Auth.

**Reason**: To delegate authorization logic to the database layer, ensuring that data access restrictions are enforced consistently protected regardless of the application endpoint or service accessing the data.

**Alternatives Considered**:
- Implementing access control solely in the application service layer.
- Using database views or stored procedures to encapsulate access logic.
- Relying on network-level isolation (e.g., separate databases per tenant) – not applicable for multi-tenant SaaS.

**Trade-offs**:
- **Pros**: Centralized authorization, defense-in-depth (even if application layer is compromised, RLS still protects data), automatic enforcement for direct database access, and integration with Supabase Auth.
- **Cons**: Slight query complexity, potential performance overhead on complex policies, and requires careful policy design to avoid accidental data leakage.

---

## ADR 013: Use JWT for Authentication with Supabase Auth

**Decision**: Authenticate users via JSON Web Tokens (JWT) issued by Supabase Auth, validating tokens using the Supabase JWKS.

**Reason**: To leverage a secure, industry-standard token-based authentication mechanism that integrates seamlessly with Supabase's user management and supports stateless validation across services.

**Alternatives Considered**:
- Using opaque session tokens with server-side storage (e.g., Redis sessions).
- Using API keys for service-to-service authentication.
- Using Mutual TLS (mTLS) for service-to-service authentication.
- Developing a custom authentication system (e.g., using Django Allauth or Firebase Auth).

**Trade-offs**:
- **Pros**: Stateless scalability, reduced server-side storage for sessions, standard format with ample library support, and ability to include custom claims (e.g., roles).
- **Cons**: Token revocation complexity (mitigated by short-lived tokens and refresh token rotation), need to securely manage signing keys (handled by Supabase), and token size overhead.

---

## ADR 014: Adopt a Modular Monolith Architecture with a Clear Path to Microservices

**Decision**: Structure the backend as a modular monolith (separate modules for auth, job, resume, AI, notifications, etc.) with well-defined interfaces, intending to migrate to microservices only if scaling demands require it.

**Reason**: To simplify initial development, testing, and deployment while maintaining the ability to scale out specific services independently in the future.

**Alternatives Considered**:
- Starting with a microservices architecture from day one.
- Using a strict layered architecture (presentation, business logic, data access) without domain-based modules.
- Adopting a serverless architecture (e.g., AWS Lambda) for all backend functions.

**Trade-offs**:
- **Pros**: Reduced operational complexity (single deployable unit, simpler testing), easier refactoring within monolith, clear module boundaries for future extraction, and avoidance of network latency between services.
- **Cons**: Potential for accidental coupling if modules are not well-enforced, scaling requires scaling the entire monolith (mitigated by internal modular scaling and eventual microservice extraction), and initial perception of being less "cloud-native".

---

## ADR 015: Use Tailwind CSS and shadcn/ui for Styling and Component Library

**Decision**: Implement the frontend UI using Tailwind CSS for utility-first styling and shadcn/ui for accessible, unstyled component primitives.

**Reason**: To accelerate UI development with a consistent design system, ensure accessibility compliance (via Radix-based components), and enable rapid iteration through utility classes.

**Alternatives Considered**:
- Using a traditional CSS framework (Bootstrap, Material-UI, Ant Design).
- Writing custom CSS or CSS modules without a utility-first approach.
- Using a design system library like Chakra UI or Radix UI Primitives directly.
- Utilizing inline styles or CSS-in-JS solutions (e.g., Styled Components, Emotion).

**Trade-offs**:
- **Pros**: Highly customizable, encourages consistent spacing and theming, eliminates CSS specificity wars, strong integration with PostCSS and next/just-in-time (JIT) compilation, and access to a growing community of shadcn/ui extensions.
- **Cons**: Requires learning utility-first concepts, potential for lengthy class strings (mitigated by tailwind's `@apply` and component extraction), and reliance on class names for styling (less intuitive for designers unfamiliar with Tailwind).

---

## ADR 016: Implement Hybrid Job Matching Score (Vector + Keyword + Recency + Location)

**Decision**: Calculate job match scores using a weighted combination of cosine similarity (vector embeddings), Jaccard similarity (skill overlap), exponential recency decay, and location preference.

**Reason**: To capture both semantic meaning (via embeddings) and exact keyword matches, while prioritizing recent opportunities and respecting user location preferences, resulting in more relevant and personalized job recommendations.

**Alternatives Considered**:
- Using pure vector similarity (cosine distance only).
- Using traditional BM25/TF-IDF text matching.
- Using a learning-to-rank (LTR) model trained on user interactions.
- Using a rule-based system with hard thresholds without machine learning components.

**Trade-offs**:
- **Pros**: Balances relevance and explainability, tunable weights per user, effective cold-start performance (works without historical interaction data), and incorporates multiple signals known to affect job search satisfaction.
- **Cons**: Requires tuning of weights (α, β, γ, δ), increases computational complexity per candidate, and may not capture complex user preferences as well as a learned model (mitigated by allowing weight customization and planning for future LTR integration).

---

## ADR 017: Use Hash-Based and Fuzzy Deduplication for Job Ingestion

**Decision**: Deduplicate incoming job postings using an exact hash (title + company + URL) and a fallback fuzzy match (token set ratio > 90) on title and company for near-duplicates.

**Reason**: To efficiently eliminate exact duplicates while catching near-duplicates that arise from minor variations in job titles or reposting, ensuring a clean and non-redundant job feed.

**Alternatives Considered**:
- Using only exact hash deduplication.
- Using only fuzzy matching (e.g., MinHash, SimHash).
- Relying on source-specific deduplication (trusting the provider to not send duplicates).
- Using vector similarity of job descriptions for deduplication (computationally expensive).

**Trade-offs**:
- **Pros**: High precision for exact duplicates, good recall for near-duplicates with reasonable performance, simple to implement and understand, and low computational overhead.
- **Cons**: Fuzzy matching may miss duplicates with significant phrasing variations or may incorrectly merge distinct jobs with similar titles (mitigated by high threshold and manual review options), and does not account for semantic duplication (addressed by optional vector-based duplicate detection in future enhancements).

---

## ADR 018: Store Raw Job JSON for 30 Days, Cleaned Jobs Indefinitely with Soft Delete After 90 Days

**Decision**: Retain raw JSON payloads from Apify for 30 days to allow reprocessing if needed, keep cleaned job records indefinitely, and softly delete (mark as `archived`) jobs that have been inactive for over 90 days.

**Reason**: To balance storage costs with the need for data reprocessing, historical analysis, and compliance, while ensuring the active job database remains performant.

**Alternatives Considered**:
- Deleting raw JSON immediately after ingestion.
- Storing raw JSON indefinitely.
- Using hard deletion for old jobs.
- Moving old jobs to a separate archive table or database.

**Trade-offs**:
- **Pros**: Enables recovery from ingestion errors, supports audit trails and debugging, reduces storage costs over time via soft deletes, and maintains simplicity with a single table plus a flag.
- **Cons**: Slightly higher storage cost due to retained raw data (mitigated by 30-day TTL), and requires application logic to respect the `archived` flag in queries.

---

## ADR 019: Use Structured Logging (JSON) with Redaction of Sensitive Data

**Decision**: Implement structured logging in JSON format using a library like `structlog`, ensuring that personally identifiable information (PII) and secrets are redacted before output.

**Reason**: To facilitate log aggregation, searching, and analysis with tools like ELK or Loki, while maintaining security and privacy by not leaking sensitive data in logs.

**Alternatives Considered**:
- Using plain text logging with custom formatting.
- Using keyword-based logging without structure.
- Relying solely on metrics and tracing without detailed logs.
- Using syslog format.

**Trade-offs**:
- **Pros**: Machine-readable, easy to parse and filter, consistent fields for correlation, and compatibility with modern log management platforms.
- **Cons**: Slightly larger log size due to JSON overhead, requires discipline to avoid logging sensitive fields, and may need adjustment for developers used to plaintext logs.

---

## ADR 020: Expose Prometheus Metrics and Distributed Tracing via OpenTelemetry

**Decision**: Instrument the application to export Prometheus-compatible metrics (via `prometheus-fastapi-instrumentator`) and distributed traces (via OpenTelemetry) to enable observability.

**Reason**: To gain insights into system performance, error rates, latency, and dependencies, supporting proactive monitoring, alerting, and debugging in production.

**Alternatives Considered**:
- Using only logs for observability (no metrics/tracing).
- Using vendor-specific APM agents (e.g., Datadog APM, New Relic).
- Using StatsD instead of Prometheus.
- Using Zipkin or Jaeger directly without OpenTelemetry abstraction.

**Trade-offs**:
- **Pros**: Vendor neutrality, rich ecosystem (Grafana, Prometheus, Alertmanager), correlation between traces, metrics, and logs, and ability to choose backends later.
- **Cons**: Initial instrumentation overhead, potential cardinality explosion in metrics if not careful (e.g., high-cardinality labels), and learning curve for setting up and managing the observability stack.

---
*End of ADR Log*