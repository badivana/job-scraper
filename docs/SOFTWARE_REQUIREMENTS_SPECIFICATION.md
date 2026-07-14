# Software Requirements Specification

## Purpose

To provide a comprehensive description of the AI-Powered Job Finder system’s functional and non‑functional requirements, external interfaces, and constraints for designers, developers, testers, and stakeholders.

## Contents

1. Introduction  
   1.1 Purpose  
   1.2 Scope  
   1.3 Definitions, Acronyms, and Abbreviations  
   1.4 References  
   1.5 Overview  

2. Overall Description  
   2.1 Product Perspective  
   2.2 Product Functions  
   2.3 User Classes and Characteristics  
   2.4 Operating Environment  
   2.5 Design and Implementation Constraints  
   2.6 User Documentation  
   2.7 Assumptions and Dependencies  

3. External Interface Requirements  
   3.1 User Interfaces  
   2.2 Hardware Interfaces  
   2.3 Software Interfaces  
   2.4 Communications Interfaces  

4. System Features  
   4.1 User Management  
   4.2 Resume Handling  
   4.3 Job Ingestion  
   4.4 Job Search & Discovery  
   4.5 Job Matching  
   4.6 Job Interaction  
   4.7 Application Materials Generation  
   4.8 Notification System  
   4.9 Administration & Operations  

5. Nonfunctional Requirements  
   5.1 Performance  
   5.2 Safety  
   5.3 Security  
   5.4 Software Quality Attributes  
   5.5 Business Rules  

6. Other Requirements  

## 1. Introduction

### 1.1 Purpose
This SRS specifies the functional, performance, security, and interface requirements for the AI‑Powered Job Finder SaaS platform.

### 1.2 Scope
The system comprises a web‑based frontend (Next.js/React), a set of backend microservices (FastAPI), a PostgreSQL database with pgvector, Redis cache, background workers (Celery/APScheduler), and integration with Apify for scraping and OpenAI GPT for language generation.

### 1.3 Definitions, Acronyms, and Abbreviations
- **ATS** – Applicant Tracking System  
- **JWT** – JSON Web Token  
- **OAuth** – Open Authorization  
- **pgvector** – PostgreSQL extension for vector similarity search  
- **API** – Application Programming Interface  
- **UI/UX** – User Interface / User Experience  
- **NPS** – Net Promoter Score  
- **SLA** – Service Level Agreement  
- **CI/CD** – Continuous Integration / Continuous Deployment  
- **ETL** – Extract, Transform, Load  

### 1.4 References
- AI Powered Job Finder Architecture (AI_Powered_Job_Finder_Architecture.md)  
- Product Requirements Document (docs/PRODUCT_REQUIREMENTS.md)  
- Tech Stack (docs/TECH_STACK.md)  
- OpenAPI Specification (to be generated)  
- GDPR Regulation (EU) 2016/679  
- CCPA (California Consumer Privacy Act)  

### 1.5 Overview
The remainder of this document details the product perspective, functions, user classes, interface requirements, system features, and non‑functional constraints.

## 2. Overall Description

### 2.1 Product Perspective
The AI‑Powered Job Finder is a self‑contained web application that interacts with third‑party services (Apify, OpenAI, email providers) and stores user‑generated content in a private cloud.

### 2.2 Product Functions
- User registration, authentication, and profile management.  
- Resume upload, parsing, skill extraction, and storage.  
- Scheduled scraping of job postings from multiple sources via Apify.  
- Deduplication, cleaning, and storage of job data.  
- Full‑text and faceted job search.  
- Semantic job‑to‑resume matching using embeddings.  
- Application tracking (saved, applied, OA, interview, offer, rejected).  
- AI‑generated cover letters and recruiter outreach messages.  
- Email and in‑app notifications.  
- Administrative monitoring and management dashboards.

### 2.3 User Classes and Characteristics
| User Class | Description | Characteristics |
|------------|-------------|-----------------|
| Job Seeker | Primary end‑user seeking employment | Varies in technical skill; expects intuitive UI, fast results, data privacy |
| Career Coach | Secondary user assisting clients | Values reporting, export, and ability to view clients’ anonymized progress |
| Administrator | System operator responsible for health, security, and content | Requires access to logs, metrics, user management, and scraping controls |
| Guest | Unauthenticated visitor | Can view public marketing pages; must sign up to use core features |

### 2.4 Operating Environment
- **Web browsers**: Chrome, Firefox, Safari, Edge (latest‑2 versions)  
- **Operating systems**: Any OS supporting a modern browser  
- **Network**: Broadband or mobile 3G+/4G/5G; latency ≤ 150 ms to API gateway  
- **Third‑party services**: Apify (scraping), OpenAI (LLM/embeddings), email provider (SendGrid/SMTP), OAuth providers (Google, LinkedIn)  

### 2.5 Design and Implementation Constraints
- Must follow the technology stack defined in docs/TECH_STACK.md.  
- Backend services must be containerizable (Docker) and orchestratable (Docker‑Compose or Kubernetes).  
- Database schema migrations must be backward‑compatible or provide migration scripts.  
- All secrets (API keys, DB passwords) must be injected via environment variables or a secret manager; never hard‑coded.  
- Code must adhere to the coding standards in docs/CODING_STANDARDS.md.  
- Accessibility: WCAG 2.1 AA compliance for UI components.  

### 2.6 User Documentation
- Online help center (FAQ, guides) hosted within the application.  
- API developer portal (if public endpoints are exposed).  
- Admin operations manual.  
- Data processing and privacy policy (see docs/legal/PRIVACY_POLICY.md).  

### 2.7 Assumptions and Dependencies
- Apify provides stable scraping actors for the listed sources; fallback to in‑house scrapers if needed.  
- OpenAI API remains available with sufficient rate limits for expected load.  
- Users consent to store and process their resume data for matching and generation purposes.  
- Adequate network bandwidth for fetching job descriptions and storing files in object storage.  

## 3. External Interface Requirements

### 3.1 User Interfaces
- **Web Application**: Responsive single‑page application built with Next.js, React, TypeScript, TailwindCSS, shadcn/ui.  
- **Accessibility**: ARIA labels, keyboard navigation, sufficient color contrast.  
- **Internationalization**: UI strings externalized for future i18n (initially English‑only).  
- **Error Handling**: Inline validation, toast notifications, graceful degradation for API failures.

### 3.2 Hardware Interfaces
- The system runs on commodity cloud virtual machines (or containers). No special hardware required.  
- Minimum recommended instance: 2 vCPU, 4 GB RAM for lightweight services; larger for worker nodes (CPU‑intensive scraping/LLM inference via API).  

### 3.3 Software Interfaces
| Interface | Provider | Protocol / Format | Purpose |
|-----------|----------|-------------------|---------|
| Apify Actor | Apify (Saas) | HTTP JSON | Trigger scraping jobs, Receive scraped data |
| OpenAI API | OpenAI | HTTPS JSON | Generate embeddings, chat completions for cover letters |
| Email Service | SendGrid / SES / Mailgun | SMTP / HTTP API | Send transactional and marketing emails |
| OAuth Providers | Google, LinkedIn | OAuth 2.0 (OpenID Connect) | Social login |
| Object Storage | AWS S3 / Supabase Storage | REST API (S3‑compatible) | Store raw resumes, generated documents |
| Payment Processor (future) | Stripe | HTTPS JSON | Subscriptions (out‑of‑scope for MVP) |

### 3.4 Communications Interfaces
- **Internal Service Communication**: REST/JSON over HTTP; gRPC considered for low‑latency streaming (not in MVP).  
- **Database**: PostgreSQL wire protocol (libpq) via SQLAlchemy ORM.  
- **Cache**: Redis protocol (RESP).  
- **Message Broker** (if using Celery): AMQP (Redis or RabbitMQ) for task distribution.  
- **WebSocket** (optional): Real‑time notifications to client (fallback to polling).  

## 4. System Features

### 4.1 User Management
- **Sign‑up / Login**: Email/password with verification, OAuth2 social login.  
- **Password Reset**: Token‑based email flow.  
- **Profile**: Editable fields; avatar upload (optional).  
- **Roles**: Standard user, Admin (flag in user table).  
- **Session Management**: JWT access token (15 min) + refresh token (7‑day rotating).  
- **Account Deletion**: GDPR‑right‑to‑be‑forgotten flow; purges personal data and anonymizes interactions.

### 4.2 Resume Handling
- **Upload**: Accept .pdf, .docx, max 5 MB; virus‑scan (ClamAV) optional.  
- **Storage**: Encrypted at rest (S3 SSE‑S3 or client‑side encryption).  
- **Extraction**: Text extraction via PDF‑miner / python‑docx; OCR fallback (Tesseract) for scanned PDFs.  
- **Parsing**: Rule‑based + spaCy NER to identify sections (experience, education, skills, certifications).  
- **Skill Normalization**: Mapping to ESCO/O*NET taxonomy via lookup table; fuzzy matching for variants.  
- **Embedding Generation**: Send cleaned resume text to OpenAI embedding model (text‑embedding‑3‑small) → store 1536‑dim vector in pgvector column.  
- **Edit & Re‑parse**: User can modify extracted fields; upon save, re‑generate embedding.  
- **Privacy**: Resume content visible only to owning user and admins (for support).  

### 4.3 Job Ingestion
- **Scheduled Tasks**: Cron‑like triggers (APScheduler) per source (e.g., every 2 h for LinkedIn, daily for company pages).  
- **Apify Integration**: Call Apify API to start a pre‑built actor; receive run‑ID; poll for completion; download result dataset (JSON).  
- **Deduplication**: Compute hash of (URL, normalized title, company); also use fuzzy token‑set ratio > 90% as duplicate.  
- **Cleaning**: Strip HTML, normalize whitespace, extract salary via regex patterns, detect remote/hybrid/onsite flags.  
- **Storage**: Raw JSON blob in `jobs_raw` table; cleaned record in `jobs` table with indexed columns (title, company, location, remote_flag, salary_min/max, posted_at).  
- **Incremental Load**: Store latest processed timestamp per source to avoid re‑scraping entire history.  
- **Error Handling**: Retry with exponential backoff; dead‑letter queue for persistent failures; alert admin.  

### 4.4 Job Search & Discovery
- **Full‑Text Search**: PostgreSQL `tsvector` + `tsquery` on title, description, skills, company.  
- **Faceted Filters**:  
  - Location: city, state, country, remote‑only toggle.  
  - Salary: min/max (integer), optionally“not disclosed”.  
  - Employment type: full‑time, part‑time, contract, internship, temporary.  
  - Experience level: entry, mid, senior, executive (derived from title keywords).  
  - Date posted: last 24h, 7d, 30d, any.  
  - Company size / industry (if available).  
- **Sorting**: Relevance (full‑text rank + match score), date (newest first), salary (high to low).  
- **Pagination**: Limit/offset; keyset pagination for deep pages.  
- **Saved Searches**: User can store query parameters; optionally enable email alerts for new matches.  

### 4.5 Job Matching
- **Vector Search**: Approximate nearest neighbor (ANN) using pgvector ivfflat index; retrieve top‑k (e.g., 100) candidates.  
- **Hybrid Scoring**: Final score = α·cosine_similarity + β·keyword_match + γ·recency_decay + δ·location_preference. Weights configurable per user (default α=0.4, β=0.3, γ=0.2, δ=0.1).  
- **Keyword Match**: Jaccard similarity between resume skill set and job skill entities (extracted via NER or simple dictionary).  
- **Recency Decay**: exponential decay based on days since posting (half‑life 14 days).  
- **Location Preference**: Boolean match or distance‑based scaling if user specifies radius.  
- **Exclusion**: Filter out jobs already in user’s saved/applied/hidden lists unless “show previously seen” enabled.  
- **Result Presentation**: Job card with title, company, location, salary badge, match‑score progress bar, “Save”, “Apply”, “Hide” buttons. Tooltip shows detailed match breakdown.  

### 4.6 Job Interaction
- **Save Job**: Insert row into `saved_jobs` (user_id, job_id, note, timestamp).  
- **Application Status**: Enum `application_status` with values: saved, applied, oa, interview, offer, rejected, withdrawn.  
- **Status Transition**: User can move job forward/backward; each transition logs timestamp and optional note.  
- **Applied Tracking**: Optional external URL click tracking; if integrated with ATS via webhook, status updates can be automatic (future).  
- **Notes & Attachments**: Free‑form text field per job; ability to upload additional documents (e.g., tailored resume).  
- **Hide / Remove**: Move to hidden set (not shown in recommendations) or delete from saved list.  

### 4.7 Application Materials Generation
- **Prompt Construction**:  
  - Cover Letter: `{system: "You are a professional cover letter writer."} {user: "Write a tailored cover letter for the following resume and job description. Keep it to one page, professional tone."} \n\nResume: {resume_summary}\n\nJob Description: {job_description}`  
  - Cold Email: Similar but shorter, ask to generate a concise outreach message to recruiter/hiring manager.  
- **LLM Parameters**: Model `gpt-4o-mini` (or `gpt-4-turbo`), temperature 0.7, max_tokens 500 (cover letter), 150 (email).  
- **Post‑Processing**: Strip markdown, ensure plain text; optionally convert to PDF via `weasyprint` or browser print‑to‑PDF.  
- **Storage**: Generated text stored in `generated_documents` table; PDF version stored in object storage with signed URL for download.  
- **Versioning**: Each generation creates a new record; user can view history and revert.  
- **Rate Limiting**: Per‑user daily quota (e.g., 50 generations) to control LLM cost.  

### 4.8 Notification System
- **Email**:  
  - New job matches (based on saved search threshold & frequency).  
  - Application status change (if user manually updates or webhook received).  
  - Weekly digest: top 5 matches, application stats.  
  - Password reset, verification, marketing opt‑in (separate subscription).  
- **In‑App**:  
  - Bell icon with red dot for unread notifications.  
  - Dropdown list showing latest 10 notifications; mark as read/delete.  
  - Real‑time via WebSocket (optional) or polling every 30 s.  
- **Preferences**: User can enable/disable each channel, set quiet hours, adjust frequency.  
- **Template Service**: Jinja2 templates for email bodies; support plain‑text and HTML versions.  

### 4.9 Administration & Operations
- **Dashboard Views**:  
  - User Management: list, search, ban/unban, role change.  
  - Scraping Health: per‑source last run status, duration, error count, lag.  
  - System Metrics: request latency, error rates, queue depth, cache hit ratio.  
  - Data Statistics: total users, jobs stored, resumes uploaded, messages sent.  
- **Controls**:  
  - Trigger manual scrape for a source.  
  - Flush Redis cache.  
  - Trigger re‑embedding batch for all resumes (e.g., after model change).  
  - Export audit logs (CSV/JSON).  
- **Access Control**: RBAC; only users with role `admin` can access admin routes.  
- **Audit Log**: Immutable append‑only log of significant actions (login, data export, config change) stored in separate table.  

## 5. Nonfunctional Requirements

### 5.1 Performance
| Metric | Target | Measurement |
|--------|--------|--------------|
| Page Load (Home) | < 2 s on 3G | Lighthouse / WebPageTest |
| API Latency (95th pct) | < 500 ms | Prometheus histograms |
| Vector Search (k=100) | < 200 ms | pgbench‑like test |
| Concurrent Users | 10 k simulated | Locust / k6 |
| Job Ingestion Lag | ≤ 30 min from source posting | Timestamp diff |

### 5.2 Safety
- No safety‑critical functions; the system is informational.  
- Ensure that generated content does not contain hate speech, harassment, or illegal advice (moderate via OpenAI content filter + profanity list).  

### 5.3 Security
- **Authentication**: Handled via Supabase Auth (secure password storage with argon2id, enforces minimum 12‑character strength, rate‑limited login attempts, MFA optional).
- **Transport**: TLS 1.2+ everywhere; HSTS max‑age 31536000.  
- **Session**: JWT signed with RS256; private key stored in secret manager.  
- **Authorization**: Middleware checks role/scopes for each endpoint.  
- **Data Protection**:  
  - At‑rest: AES‑256 (S3 SSE‑KMS or application‑level encryption).  
  - In‑transit: TLS.  
- **Secrets Management**: Environment variables or HashiCorp Vault / AWS Secrets Manager.  
- **Input Validation**: Strict schema validation (pydantic) for all inbound data.  
- **Output Encoding**: HTML escape for user‑generated content rendered in templates.  
- **Logging**: No PII in logs; mask emails, tokens.  
- **Vulnerability Scanning**: Automated SAST/DAST in CI pipeline; periodic third‑party pen test.  
- **Compliance**: Designed for GDPR (right to access, rectification, erasure) and CCPA.  

### 5.4 Software Quality Attributes
- **Maintainability**: Modular architecture, clear interfaces, ≥ 80 % unit test coverage.  
- **Scalability**: Horizontal pod autoscaling based on CPU & queue length.  
- **Availability**: Target 99.9 % uptime (excluding scheduled maintenance).  
- **Portability**: Docker images run on any OCI‑compliant runtime; Helm charts for K8s.  
- **Testability**: Dependency injection; mockable external services.  

### 5.5 Business Rules
- A user may have at most one active resume (primary) but can store multiple versions.  
- Job postings older than 90 days are archived (soft‑delete) and excluded from default search unless “show archived” toggled.  
- Free tier limits: 10 resume uploads, 50 job matches/day, 10 AI generations/day. Paid tiers remove limits.  
- No scraping of sites that disallow crawling per `robots.txt` without explicit permission.  

## 6. Other Requirements
- **Legal**: Terms of Service and Privacy Policy must be accepted upon registration.  
- **Accessibility**: WCAG 2.1 AA compliance for all user‑facing pages.  
- **Localization**: Strings externalized; UTF‑8 support throughout.  
- **Portability**: Deployable to AWS, Azure, GCP, or on‑premises Kubernetes.  
- **Internationalization**: Ready for future language packs (date, number, currency formats).  
- **Operational**: Runbooks for common tasks (db backup/restore, cert renewal, log rotation).  

---  
*Document Version: 1.0*  
*Last Updated: 2026‑07‑14*