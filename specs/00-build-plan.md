# Build Plan: AI-Powered Job Finder SaaS

This document outlines the implementation phases for the AI-Powered Job Finder SaaS project. Each phase is broken down into implementation units estimated to take 2-6 hours. The plan is designed to be incremental, delivering working functionality at the end of each phase.

## Phase 0: Project Setup and Infrastructure

**Objective**: Establish the development environment, CI/CD pipeline, and foundational infrastructure.

**Deliverables**:
- GitHub repository initialized with branch protection rules.
- Development environment setup guide (LOCAL_SETUP.md).
- Supabase project initialized with Auth, Storage, and PostgreSQL (with pgvector extension).
- Redis instance (local Docker for dev, managed for prod).
- Docker Compose for local development (backend, frontend, Redis).
- GitHub Actions workflow for CI (lint, test, build) and CD (staging deployment).
- Basic project structure for frontend (Next.js) and backend (FastAPI).
- README with setup instructions.

**Dependencies**: None (foundational phase).

**Estimated Effort**: 20-30 hours (broken into 2-6 hour units).

**Verification Checklist**:
- [ ] Repository cloned and dependencies installed.
- [ ] Supabase project accessible; can sign up via Auth UI.
- [ ] Docker compose starts all services (backend, frontend, Redis).
- [ ] GitHub Actions runs on push to main and passes lint/unit tests.
- [ ] API health endpoint (`/health`) returns 200.
- [ ] Frontend loads and shows a placeholder page.

## Phase 1: User Authentication and Profile

**Objective**: Implement user registration, login, profile management, and role-based access.

**Deliverables**:
- Supabase Auth integrated with email/password and OAuth (Google, GitHub).
- Email verification flow (token sent, link clicks to verify).
- Password reset via email token.
- User profile page (view and edit: name, headline, location, bio, links).
- Role attribute in user metadata (user/admin) and middleware to protect routes.
- Basic API endpoints for profile CRUD.

**Dependencies**: Phase 0 (Supabase project ready).

**Estimated Effort**: 25-35 hours.

**Verification Checklist**:
- [ ] User can sign up with email/password and receive verification email.
- [ ] Email verification link activates account and redirects to onboarding.
- [ ] User can log in with email/password and OAuth providers.
- [ ] Password reset flow works end-to-end.
- [ ] Authenticated user can view and edit profile; changes persist.
- [ ] Admin role can access admin-only routes (to be built in later phases).
- [ ] API returns 401 for unauthenticated requests to protected endpoints.

## Phase 2: Resume Handling

**Objective**: Enable users to upload resumes, extract text, parse sections, normalize skills, and store embeddings.

**Deliverables**:
- Resume upload (PDF/DOCX, up to 5MB) to Supabase Storage.
- Text extraction using appropriate libraries (PyPDF2, python-docx).
- Resume parsing into sections (contact, summary, experience, education, skills, certifications).
- Skill extraction and normalization to a taxonomy (e.g., ESCO, O*NET) using NLP or lookup.
- Store parsed resume data in PostgreSQL (JSONB or normalized tables).
- Generate embedding for the resume using OpenAI text-embedding-3-small and store in pgvector column.
- API endpoints for upload, parsing status, and retrieving parsed resume.
- Frontend upload component with progress bar and preview of extracted fields (editable).
- Error handling for unsupported file types, extraction failures, and size limits.

**Dependencies**: Phase 0 (Supabase Storage, PostgreSQL), Phase 1 (authenticated user).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] User can upload a PDF or DOCX resume (<5MB) and see upload progress.
- [ ] Extracted text is displayed and divided into sections correctly.
- [ ] Skills are extracted and mapped to known taxonomy (e.g., "Python" -> "Programming Languages").
- [ ] Parsed data is saved and can be retrieved via API.
- [ ] Resume embedding is stored as a vector (1536 dimensions) in the user's record.
- [ ] User can edit parsed fields and save changes.
- [ ] Invalid files (wrong type, too large, corrupted) show appropriate error messages.
- [ ] Original file is stored in Supabase Storage and accessible via signed URL.

## Phase 3: Job Ingestion Infrastructure

**Objective**: Set up the job ingestion pipeline using Apify actors, Celery workers, and data storage.

**Deliverables**:
- Celery worker configured with Redis broker.
- Apify integration: configuration for predefined actors (LinkedIn, Indeed, etc.) or generic scraper.
- Scheduler (Celery Beat) to run scraping jobs at defined intervals (e.g., every 6 hours).
- Normalization pipeline: deduplication by URL/hash, fuzzy matching on title/company.
- Cleaned job data stored in PostgreSQL (raw JSON and normalized fields).
- Basic API endpoint to list jobs (for testing) with pagination.
- Error handling and retry logic for failed Apify runs.
- Admin interface (basic) to trigger manual scrape and view job counts.

**Dependencies**: Phase 0 (Redis, Docker), Phase 1 (auth for admin endpoints).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] Celery worker starts and consumes jobs from Redis queue.
- [ ] Apify actor can be triggered via API (or scheduler) and returns job data.
- [ ] Raw job data is stored in the `raw_jobs` table.
- [ ] Normalization removes exact duplicates and merges near-duplicates (fuzzy title/company).
- [ ] Cleaned jobs appear in the `jobs` table with expected fields (title, company, location, etc.).
- [ ] API endpoint `/jobs` returns paginated list of jobs.
- [ ] Manual scrape trigger via admin endpoint works and updates job count.
- [ ] Failed Apify runs are retried up to 3 times and logged.

## Phase 4: Job Search and Discovery

**Objective**: Implement job search with filtering, sorting, and saved searches.

**Deliverables**:
- Full-text search over title, description, company, and skills (using PostgreSQL ILIKE or trigram, or pgvector for semantic search later).
- Faceted filters: location (city, remote, hybrid), salary range, experience level, employment type, date posted.
- Sorting options: relevance (text search score), date (newest first), salary (high to low).
- Save search functionality: user can name a search and get email alerts for new matches.
- Email alert service (using Supabase email or integrated service like SendGrid) for new matching jobs.
- Frontend search page with search bar, filter panels, results grid, and pagination.
- Job detail page showing full description, match score (placeholder), and apply/save buttons.
- Loading states and error handling.

**Dependencies**: Phase 3 (jobs available in database).

**Estimated Effort**: 35-45 hours.

**Verification Checklist**:
- [ ] Search bar returns jobs matching keywords in title, description, company.
- [ ] Filters refine results correctly (e.g., selecting "Remote" shows only remote jobs).
- [ ] Sorting changes order as expected (newest first, highest salary).
- [ ] Saved search can be created with a name and alert frequency.
- [ ] Email alert is sent when a new job matches saved search (test via manual job insertion).
- [ ] Search results page shows job title, company, location, date, and match score placeholder.
- [ ] Clicking a job navigates to its detail page with full description.
- [ ] Pagination works correctly (next/prev buttons, page numbers).
- [ ] Empty state shows helpful message when no jobs match.

## Phase 5: Job Matching

**Objective**: Implement AI-driven job matching using resume embeddings and job description embeddings.

**Deliverables**:
- Generate embeddings for job descriptions (using OpenAI text-embedding-3-small) and store in `jobs` table (vector column).
- Compute cosine similarity between user resume embedding and job description embedding via pgvector.
- Combine similarity score with keyword match boost (exact skill matches) and recency decay (newer jobs score higher).
- Expose match score (0-100%) and breakdown (skills 40%, title 30%, location 20%, recency 10%) via API.
- Allow users to adjust weights for matching factors via UI settings (sliders that persist).
- Exclude already saved/applied jobs from recommendations unless user opts-in.
- Frontend: display match score badge on job cards and detailed breakdown on job detail page.
- Update search results to order by match score when relevance sort is selected.

**Dependencies**: Phase 2 (resume embeddings), Phase 3 (job descriptions), Phase 4 (search infrastructure).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] Job descriptions have vector embeddings stored in the database.
- [ ] Match score is computed as cosine similarity + keyword boost + recency decay.
- [ ] Changing weight sliders updates the match score in real time (on job detail or search results).
- [ ] Saved/applied jobs are excluded from recommendations by default (toggle to include).
- [ ] Match score breakdown shows contributions from each factor.
- [ ] Jobs are ordered by match score when sorting by relevance.
- [ ] Edge cases handled: missing resume embedding defaults to keyword-only scoring.

## Phase 6: Job Interaction and Application Tracking

**Objective**: Allow users to save jobs, track application status, and manage their job pipeline.

**Deliverables**:
- Save job to "Saved" list with optional note (stored in `user_jobs` table).
- Application status Kanban board: columns for Saved, Applied, OA (Online Assessment), Interview, Offer, Rejected.
- Drag-and-drop to move jobs between columns; timestamp recorded on status change.
- Ability to add notes per status change.
- One-click apply: records click timestamp and redirects to external application URL.
- Custom application stages: admin can define additional stages (beyond default) for their account.
- Filter board by status, date added, and keyword search.
- Frontend: Kanban board (using a library like react-beautiful-dnd or custom), save job button on job card/detail.

**Dependencies**: Phase 1 (user auth), Phase 3 (jobs), Phase 4 (search/save).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] User can save a job from search results or job detail page.
- [ ] Saved job appears in the "Saved" column of the Kanban board.
- [ ] User can add a note when saving; note is displayed and editable.
- [ ] Drag-and-drop moves job to another column (e.g., Saved → Applied) and updates timestamp.
- [ ] Clicking "Apply" records timestamp and redirects to the job's application URL.
- [ ] Custom stages can beadded via admin settings (if implemented in this phase or later) and appear in the board.
- [ ] Board filters work: show only "Applied" jobs, or jobs added in the last week.
- [ ] Empty state for each column provides guidance.
- [ ] Data persists across sessions and is tied to the authenticated user.

## Phase 7: Application Materials Generation

**Objective**: Generate tailored cover letters and recruiter outreach messages using LLMs.

**Deliverables**:
- Cover letter generation: LLM prompt combines resume summary, job description, and user tone (professional, enthusiastic, etc.).
- Cold email/LinkedIn message generation: short, personalized note to recruiter/hiring manager.
- Integration with OpenAI GPT-4-turbo (temperature 0.7 for creativity).
- Editing and regenerating: user can edit generated text and request a new version.
- Version history: save multiple versions per job (cover letter and message).
- Storage: generated documents saved as PDF/DOCX in Supabase Storage (optional) or as text in database.
- Frontend: modal or side panel for generation, edit, and save; download buttons for PDF/DOCX.
- Metadata: link generated materials to user and job for retrieval.

**Dependencies**: Phase 1 (auth), Phase 2 (resume data), Phase 3 (job data), Phase 6 (job interaction).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] "Generate Cover Letter" button opens modal with loading state.
- [ ] Generated cover letter is tailored to the job and resume (mentions specific skills/experience).
- [ ] User can edit the generated text and regenerate with a click.
- [ ] Each version is saved and accessible via version dropdown.
- [ ] Generated cover letter can be downloaded as PDF or DOCX.
- [ ] Similar flow for cold email/LinkedIn message (shorter length).
- [ ] Generated items are linked to the job and user in the database.
- [ ] Error handling for LLM API failures (shows retry option, fallback message).

## Phase 8: Notification System

**Objective**: Implement email and in-app notifications for job matches and application updates.

**Deliverables**:
- Email alerts for new jobs matching user's saved searches or profile (scheduled daily/weekly).
- In-app notification bell with dropdown showing unread count and recent notifications.
- Notification types: new job match, application status change (if integrated with ATS webhook, else manual), weekly digest.
- User preferences page to configure notification channels (email, in-app) and frequency.
- Backend jobs (Celery) to send emails and update notification tables.
- Frontend: bell icon in header, dropdown list, mark as read/delete functionality.
- Email templates using a templating engine (e.g., Jinja2) for consistency.

**Dependencies**: Phase 1 (auth), Phase 4 (search/saved searches), Phase 5 (matching for job alerts), Phase 6 (application status for notifications).

**Estimated Effort**: 25-35 hours.

**Verification Checklist**:
- [ ] User can enable/disable email notifications and set frequency (daily, weekly).
- [ ] In-app bell shows red dot when there are unread notifications.
- [ ] Clicking bell shows dropdown with recent notifications (new job match, etc.).
- [ ] Notification for new job match includes job title, company, and link to job.
- [ ] User can mark notification as read or delete it.
- [ ] Weekly digest email sent at configured time with top matches.
- [ ] Email contains unsubscribe link and preferences link.
- [ ] Test email delivery via external service (e.g., Mailtrap) in development.

## Phase 9: Administration and Operations

**Objective**: Build admin dashboard for platform oversight and manual operations.

**Deliverables**:
- Admin-only routes protected by role middleware.
- Dashboard overview: user count, job count, scraping job status, system health (CPU, memory, latency).
- User management: list users, view roles, deactivate/activate users.
- Scraping job monitors: list of configured scrapers, last run status, next scheduled run, manual trigger button.
- System health: display logs (recent errors), error rates, query performance metrics.
- Data export: admin can request CSV/JSON export of user data (for compliance) via email.
- Frontend: responsive admin pages using shadcn/ui tables and charts.
- Audit log: track admin actions (login, user changes, manual triggers) for security.

**Dependencies**: Phase 1 (auth/roles), Phase 3 (scraping infrastructure), Phase 0 (monitoring setup).

**Estimated Effort**: 30-40 hours.

**Verification Checklist**:
- [ ] Non-admin users redirected away from admin pages.
- [ ] Admin dashboard shows at-a-glance metrics (users, jobs, active scrapers).
- [ ] User list can be searched and sorted; admin can change role or deactivate.
- [ ] Scraping job list shows last run status (success/failure) and allows manual run.
- [ ] Manual scrape triggers a Celery task and updates last run timestamp.
- [ ] System health page shows recent error logs and basic performance metrics.
- [ ] Data export request emails a download link to admin (secure, time-limited link).
- [ ] Audit log records admin actions with timestamp and user.

## Phase 10: Non-functional Improvements and Polish

**Objective**: Enhance performance, security, observability, and prepare for production.

**Deliverables**:
- Performance: add database indexes (on search/filter columns), implement Redis caching for frequent queries (user profile, recent jobs), optimize API response times.
- Security: implement OWASP Top 10 protections (input validation, output encoding, secure headers), ensure GDPR/CCPA compliance (data deletion requests, privacy policy update), regular dependency scanning.
- Observability: structured logging (JSON) to stdout, Prometheus metrics endpoint (request latency, error rates, job queue depth), health checks (`/ready`, `/live`), consider integrating with a logging/loki and prometheus/grafana setup.
- Testing: unit tests for backend services (pytest), integration tests for key flows (job search, resume upload), end-to-end tests (Cypress) for critical user journeys, load testing (k6) for peak loads.
- Documentation: update API specs, architecture diagrams, and user guides.
- Final bug bash and polish based on feedback from earlier phases.
- Prepare production deployment manifests (Docker Compose, Helm charts if using Kubernetes, or platform-specific configs).

**Dependencies**: All previous phases.

**Estimated Effort**: 40-50 hours (broader, encompassing many small tasks).

**Verification Checklist**:
- [ ] Page load time < 2s on simulated 3G (using Lighthouse).
- [ ] API 95th percentile latency < 500ms under load.
- [ ] Security scan (e.g., OWASP ZAP) shows no critical/high vulnerabilities.
- [ ] All critical user journeys have end-to-end tests passing.
- [ ] Documentation updated and accessible (e.g., `/docs` for API, `/help` for user guide).
- [ ] Backup and restore procedure tested (Supabase provides, but verify).
- [ ] Deployment to staging environment successful and smoke tests pass.
- [ ] Ready for production: monitoring alerts configured, disaster recovery plan documented.

## Phase 11: Bug Fixes and Polish (Optional, based on feedback)

**Objective**: Address any remaining issues from testing and user feedback.

**Deliverables**:
- Bug fixes identified during internal QA or beta testing.
- Minor UI/UX improvements based on user feedback.
- Performance tweaks if needed.
- Documentation updates for any last-minute changes.

**Dependencies**: All previous phases.

**Estimated Effort**: 10-20 hours (as needed).

**Verification Checklist**:
- [ ] All critical and high-priority bugs resolved.
- [ ] Regression test suite passes on staging.
- [ ] Stakeholder sign-off on MVP readiness.

## Phase 12: Production Release

**Objective**: Release the MVP to production and monitor post-launch.

**Deliverables**:
- Production deployment via approved CI/CD pipeline (blue/green or canary).
- Smoke tests in production to verify core functionality.
- Monitoring dashboards set up for key metrics (traffic, error rates, latency).
- Runbook for common operational issues (scale up, database backup, failed job restart).
- Communication plan for launch (email, social media).
- Post-launch review meeting to assess metrics and plan next iteration.

**Dependencies**: Phase 10 (production readiness).

**Estimated Effort**: 10-20 hours (excluding ongoing monitoring).

**Verification Checklist**:
- [ ] Deployment to production successful with zero downtime.
- [ ] Smoke tests pass in production (login, search, resume upload).
- [ ] Monitoring alerts configured and tested (e.g., high error rate triggers alert).
- [ ] Runbook documented and accessible to on-call team.
- [ ] Launch announcement sent to waiting list and promoted on social channels.
- [ ] First week post-launch: monitor key metrics (sign-ups, job matches, application submissions).

---
*Note: Each phase is designed to be completed in 1-2 weeks of full-time work, broken down into 2-6 hour tasks. Adjustments can be made based on team size and dependencies. The plan ensures a working, incrementally improving product at the end of each phase.*