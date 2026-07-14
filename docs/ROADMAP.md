# Roadmap

## Purpose

To communicate the planned evolution of the AI‑Powered Job Finder platform, outlining major milestones, feature groupings, and tentative timelines. The roadmap is a living document; priorities may shift based on user feedback, market conditions, and technical discoveries.

## Contents

- Vision Timeline
- Phase 0: Foundations (Months 0‑2)
- Phase 1: Core MVP (Months 3‑6)
- Phase 2: Matching & AI Enhancements (Months 7‑10)
- Phase 3: Collaboration & Analytics (Months 11‑14)
- Phase 4: Scalability & Enterprise (Months 15‑18)
- Ongoing Activities
- Review & Adjustment Cadence

## Vision Timeline

| Horizon | Goal |
|---------|------|
| **0‑6 months** | Launch a usable MVP that lets users upload a résumé, search/job match, save jobs, and track applications. |
| **6‑12 months** | Introduce AI‑generated cover letters, email alerts, and basic analytics dashboard. |
| **12‑18 months** | Add team/collaboration features, advanced analytics (funnel, ATS integration), and enterprise‑grade security & compliance. |
| **18‑24 months** | Expand to international markets, introduce mobile app, and explore premium monetization (subscriptions, recruiter insights). |

## Phase 0: Foundations (Months 0‑2)

**Objective**: Set up development infrastructure, core data models, and authentication.

- ✅ Project repository initialized with linting, formatting, CI.
- ✅ Define Supabase project (Postgres, Auth, Storage).
- ✅ Implement database schema (users, resumes, jobs, applications).
- ✅ Build basic authentication flow (Supabase Auth, JWT verification).
- ✅ Create containerized dev environment (Docker‑Compose).
- ✅ Set up CI pipeline (GitHub Actions: lint, test, build).
- ✅ Design basic UI wireframes (login, signup, home, resume upload).
- ✅ Implement frontend login/register pages.
- ✅ Create REST endpoints for user profile and resume upload/storage.

**Deliverables**:
- Working auth + profile management.
- Resume upload to Supabase Storage with metadata stored.
- Health check endpoints.

## Phase 1: Core MVP (Months 3‑6)

**Objective**: Enable job search, matching, saving, and basic application tracking.

- Integrate Apify for scheduled job ingestion (LinkedIn, Wellfound, etc.).
- Normalize and deduplicate jobs; store raw and cleaned records in Supabase Postgres.
- Implement vector embeddings for jobs (nightly batch) and pgvector index.
- Resume embedding generation on upload (via OpenAI API).
- Matching endpoint: ANN search + hybrid scoring (default weights).
- Frontend: Job search page with filters, match score badges, save button.
- Saved jobs list and basic Kanban board (Saved → Applied → OA → Interview → Offer → Rejected).
- Application status transitions recorded with timestamps.
- Notification scaffold: email alerts for new matches (via SMTP/SendGrid).
- Basic admin dashboard: view counts, recent jobs, system health.

**Deliverables**:
- Users can find jobs, see a match %age, save jobs, track application status.
- Email notifications for new high‑match jobs.
- Operational monitoring dashboard.

## Phase 2: Matching & AI Enhancements (Months 7‑10)

**Objective**: Improve match relevance, introduce AI‑generated application materials, and refine UX.

- Refine matching weights via A/B testing; expose weight sliders in settings.
- Add keyword‑based boosting (skill overlap) and location preference.
- Implement recency decay (half‑life configurable).
- Introduce “skill‑gap analysis” AI feature.
- Cover letter and cold email generation endpoints (OpenAI GPT‑4‑turbo).
- Frontend: Buttons to generate cover letter / email per job; preview and download.
- History of generated documents per user/job.
- Enhance UI: job card with match breakdown tooltip, drag‑and‑drop resume upload.
- Improve notification preferences (frequency, channels, quiet hours).
- Add webhook support for Apify (if available) to reduce polling latency.
- Begin analytics collection: impressions, clicks, application conversions.

**Deliverables**:
- AI‑assisted application materials.
- Transparent match scoring with tunable weights.
- Improved relevance and user control over matching.

## Phase 3: Collaboration & Analytics (Months 11‑14)

**Objective**: Enable teamwork (career coaches, recruiters) and deeper insights.

- Introduce **Organization** model: users can belong to a team or coaching practice.
- Role extensions: `coach`, `recruiter` (read‑only access to assigned users’ anonymized data).
- Shared dashboards: coaches see their clients’ match rates, application volumes.
- Export functionality: GDPR‑compliant data export (JSON/CSV) for users and advisors.
- Advanced analytics dashboard:
  - Funnel views (search → save → apply → interview → offer).
  - Skill demand trends (from job descriptions).
  - Geographic heat maps.
  - Time Series.
- Integrate with third‑party ATS via optional webhook (for status sync) – stretch goal.
- Add in‑app messaging (between user and coach) using Supabase Realtime.
- Implement data retention policies (purge old raw scraped json after 30 days).
- Continue improving matching with user feedback (explicit “thumbs up/down” on job relevance).

**Deliverables**:
- Collaboration features for coaches and recruiters.
- Analytics dashboard for users and advisors.
- Data export capabilities.

## Phase 4: Scalability & Enterprise (Months 15‑18)

**Objective**: Prepare the platform for high scale, regulated environments, and monetization.

- Performance tuning:
  - Enable Supabase read replicas for scaling query load.
  - Optimize pgvector indexes (IVFFlat probes, lists).
  - Horizontal pod autoscaling for backend/frontend based on CPU & queue length.
  - Worker scaling via KEDA on Redis queue length.
- Introduce **Rate Limiting & Quotas** (Free vs Paid tiers):
  - Free tier: limited resume uploads, daily AI generations.
  - Pro tier: unlimited, priority support, API access.
- Implement **Billing** integration (Stripe) for subscription management.
- Enhance security:
  - Enforce MFA for admins and optionally for users.
  - Conduct third‑party penetration test; remediate findings.
  - Add advanced audit logging (immutable append‑only table).
  - Data loss prevention: encrypt sensitive fields at application level (optional).
- Improve observability:
  - Distributed tracing (OpenTelemetry) across services.
  - Real‑time dashboards (Grafana) with SLA alerts.
- Prepare for multi‑region deployment:
  - Test failover to secondary Supabase region (if available).
  - Implement DNS‑based traffic routing (via Cloudflare or similar).
- Optimize CI/CD: parallel builds, container image signing, SBOM generation.

**Deliverables**:
- Platform capable of handling tens of thousands of concurrent users.
- Tiered pricing model with billing integration.
- Enterprise‑ready security and compliance controls.

## Ongoing Activities

- **User Feedback Loop**: Weekly review of in‑app prompts and support tickets.
- **Bug Triage**: Weekly grooming of GitHub Issues.
- **Security Scans**: Automated dependency scanning (Dependabot, pip‑audit) and quarterly SAST/DAST.
- **Performance Benchmarking**: Monthly load‑testing with k6/Locust.
- **Documentation Updates**: Keep API spec, architecture, and developer guides in sync.
- **Community & Outreach**: Blog posts, webinars, case studies.

## Review & Adjustment Cadence

- **Monthly**: Product leadership reviews progress against OKRs; adjust next month’s priorities.
- **Quarterly**: Executive review of roadmap; re‑estimate effort based on velocity.
- **Ad‑hoc**: Major incidents or market shifts trigger immediate re‑prioritization.

## Appendix: Rough Estimates (Person‑Months)

| Phase | Estimated Effort (PM) |
|-------|-----------------------|
| 0 – Foundations | 8 |
| 1 – Core MVP | 12 |
| 2 – Matching & AI | 10 |
| 3 – Collaboration | 10 |
| 4 – Scalability & Enterprise | 12 |
| **Total** | **52** |

*Note*: Estimates assume a small, cross‑functional team (2 FE, 2 BE, 1 DevOps, 1 QA/UI).

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*