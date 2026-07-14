# Claude

## Purpose

This file provides instructions for the Claude Code assistant when working on the AI Job Finder SaaS project.

## Contents

- Project overview
- Technology stack
- Architecture summary
- Development guidelines
- Development workflow
- Engineering rules
- Repository ownership
- Context system
- Specification system
- Architecture governance
- Definition of done
- Task management
- Code review process

## Project Overview

### Vision
To empower job seekers with an intelligent platform that aggregates global job opportunities, matches them precisely to individual skills and aspirations, and streamlines the application process through automation and personalized assistance.

### Mission
Build a scalable, secure, and user‑centric SaaS that combines job‑wide data collection, AI‑driven résumé‑to‑job matching, and automated application‑material generation while respecting user privacy and providing a seamless experience.

### Goals
- Deliver a minimum viable product (MVP) that lets users upload a résumé, receive personalized job matches, track applications, and generate cover letters.
- Ensure the architecture is grounded in Supabase‑managed services (PostgreSQL with pgvector, Auth, Storage, Realtime) and keeps all business logic inside FastAPI.
- Maintain high code quality, test coverage, and observability and observability to support reliable evolution.
- Prepare the system for future growth (horizontal scaling, feature‑flagged rollouts, cost controls) while avoiding premature over‑engineering.

## Read Order for Claude

Before undertaking any task, Claude MUST read the following context files in this exact order:

1. `context/project-overview.md`
2. `context/architecture.md`
3. `context/code-standards.md`
4. `context/ui-context.md`
5. `context/ai-workflow-rules.md`
6. `context/progress-tracker.md`

After these, only the documentation relevant to the specific task should be consulted. This ensures a consistent foundation and prevents unnecessary context loading.

## Technology Stack

- **Frontend** – Next.js 15, React 18, TypeScript, Tailwind CSS, shadcn/ui (see `docs/UI_UX_GUIDELINES.md` and `frontend/README.md`).
- **Backend** – FastAPI (Python 3.12) with async SQLAlchemy, Pydantic v2, Celery workers (see `backend/README.md` and `docs/CODING_STANDARDS.md`).
- **Database** – Supabase‑managed PostgreSQL with pgvector extension, UUID primary keys, Row Level Security (see `docs/DATABASE_DESIGN.md`).
- **Authentication** – Supabase Auth (email/password, OAuth providers, MFA, JWT issuance, refresh‑token rotation) (see `docs/SECURITY.md`).
- **Storage** – Supabase Storage (private buckets for résumés, generated documents, avatars, assets) (see `docs/HIGH_LEVEL_DESIGN.md` §Integration Points).
- **AI** – OpenAI GPT‑4‑turbo / text‑embedding‑3‑small for generation and embeddings; prompts stored in `prompts/ai.md` (see `docs/AI_ENGINE.md`).
- **Scraping** – Apify actors orchestrated by Celery workers; deduplication and normalization handled in the Job Service (see `docs/SCRAPING_ENGINE.md`).
- **Infrastructure** – Docker containers, Redis (cache & Celery broker), optional Supabase Realtime for real‑time notifications (see `docs/DEPLOYMENT.md`).
- **Deployment** – GitHub Actions builds Docker images, pushes to a registry, and deploys via a chosen platform (Render, Railway, Kubernetes, etc.) (see `docs/DEPLOYMENT.md` and `ci_cd/github_actions.md`).
- **Testing** – pytest + pytest‑asyncio for backend unit/integration tests; frontend tests with Jest/Cypress; contract and security checks (see `docs/TESTING_STRATEGY.md`).
- **Observability** – Structured logging, Prometheus metrics, OpenTelemetry tracing, Grafana/Loki dashboards (see `docs/MONITORING_LOGGING.md`).

## Architecture Summary

The system follows a modular, service‑oriented architecture where the frontend (Next.js) communicates with a FastAPI backend over REST/JSON. Core business logic—job ingestion, résumé processing, matching, AI generation, notifications, and scheduling—lives in the backend services. Durable data is stored in Supabase PostgreSQL (enhanced with pgvector for vector similarity), while Supabase Auth handles user identity and Supabase Storage holds binary objects. Redis provides fast caching and acts as the Celery broker for background jobs. Optional Supabase Realtime can push updates (e.g., new matches) to the frontend. All inter‑service communication relies on well‑defined OpenAPI contracts (see `docs/API_SPEC.md`). For a detailed breakdown of components, data flow, scaling, security, and evolution path, consult the documents in `docs/` and `design/`.

## Development Guidelines

- Follow the coding standards in `docs/CODING_STANDARDS.md`.
- Write tests according to `docs/TESTING_STRATEGY.md`.
- Keep the frontend UI/UX consistent with `docs/UI_UX_GUIDELINES.md`.
- Store all secrets in environment variables or secret managers; never hard‑code credentials.
- Use Supabase Auth for authentication; validate incoming JWTs against the Supabase JWKS.
- Store embeddings in PostgreSQL `vector(1536)` columns and query them with pgvector operators.
- Leverage Celery workers for background tasks (scraping, parsing, embedding batches, notifications).
- Document any architectural change (e.g., new service, schema modification) and update the relevant markdown files.
- After each meaningful implementation step, update `context/progress-tracker.md`.
- Never bypass Supabase Auth or directly access the Supabase storage API without going through the backend services.
- Do not introduce local file storage; all binaries must go through Supabase Storage.
- Do not duplicate business logic across services; favor composition and shared utility modules.
- Adhere to SOLID principles and prefer composition over inheritance.
- Keep functions small, focused, and easily testable.
- Run `npm run build` and the full test suite before considering a task complete.

## Development Workflow

1. **Idea** – Capture the concept or requirement.
2. **Architecture** – Ensure the idea fits within the existing architecture; raise an architecture change request if needed.
3. **Documentation** – Update or create relevant specification documents (e.g., in `docs/` or `design/`).
4. **Architecture Review** – Submit the change for review (by a peer or through the architectural governance process) to confirm consistency.
5. **Implementation Planning** – Break the work into manageable units (2‑6 hours each) and record them in `context/progress-tracker.md`.
6. **Specification** – Write detailed specs if necessary (e.g., API contracts, data models).
7. **Implementation** – Write the code following the coding standards.
8. **Testing** – Run unit, integration, and end‑to‑end tests; verify coverage.
9. **Review** – Perform self‑review, then request peer review.
10. **Optimization** – Refactor for performance, readability, and maintainability without changing behavior.
11. **Deployment** – Deploy to a staging environment, run smoke tests.
12. **Release** – Promote to production via the approved release process (e.g., GitHub tag, CI/CD pipeline).

After each stage, update `context/progress-tracker.md` to reflect progress.

## Engineering Rules

- Never implement without a specification.
- Never silently modify architecture.
- Never duplicate business logic.
- Never bypass FastAPI.
- Never bypass Supabase Auth.
- Never use local file storage.
- Always use Supabase Storage.
- Always use pgvector.
- Always use SQLAlchemy.
- Always use Alembic.
- Always write tests.
- Always document architectural changes.
- Always update progress-tracker.md after meaningful work.
- Prefer composition over inheritance.
- Follow SOLID principles.
- Keep functions small and focused.

## Repository Ownership

- `context/` – Contains project‑level context files (overview, architecture, code standards, UI context, AI workflow rules, progress tracker, glossary, decisions). Owned by the architecture/maintainance team.
- `docs/` – All design, requirement, and operational documentation. Owned by documentation leads.
- `design/` – Diagrams, flow charts, token definitions, ERD, sequence diagrams, etc. Owned by design/architecture team.
- `prompts/` – Prompt templates for AI services. Owned by ML/AI team.
- `tasks/` – Backlog items, phase breakdowns. Owned by product/project management.
- `specs/` – Detailed feature specifications (when created). Owned by feature owners/product analysts.
- `backend/` – All server‑side code (FastAPI, services, workers, migrations). Owned by backend engineering team.
- `frontend/` – All client‑side code (Next.js, React, TypeScript, Tailwind). Owned by frontend engineering team.
- `database/` – SQL scripts, migration strategies, backup plans, seed data. Owned by database/database‑engineering team.
- `ai/` – Utilities for embedding, model wrappers, AI‑specific helpers. Owned by ML team.
- `scraping/` – Apify integration, retry logic, scheduler configs. Owned by data acquisition team.
- `testing/` – Test fixtures, scripts, test data. Owned by QA/test engineering team.
- `assets/` – Images, icons, fonts, branding assets. Owned by design/UI team.
- `legal/` – Policies, terms, privacy, cookie notices. Owned by legal/compliance team.
- `ci_cd/` – CI/CD pipeline definitions (GitHub Actions, branching, release process). Owned by DevOps/platform team.
- `.github/` – GitHub‑specific workflows, issue templates, etc. Owned by DevOps/repository admins.

## Context System

The following context files must exist in `context/` and are required reading for every task:

- `project-overview.md` – Vision, mission, goals, core user flow, features, scope, success criteria.
- `architecture.md` – High‑level architectural decisions, stack, boundaries, storage model, auth/access model, invariants.
- `code-standards.md` – Language‑specific and general coding conventions, file organization, API rules, data handling.
- `ui-context.md` – Visual design tokens, typography, spacing, layout patterns, icon usage, component library guidance.
- `ai-workflow-rules.md` – Rules for developing AI features (prompt handling, evaluation, safety, scoping, protected files).
- `progress-tracker.md` – Living record of what has been completed, in‑progress, next up, open questions, architecture decisions, session notes.

If any of the above files are missing, they must be created with appropriate placeholder content. Additionally, the following optional but recommended context files should be present:

- `glossary.md` – Defines domain‑specific terms, acronyms, and jargon.
- `decisions.md` – Records architectural and product decisions (date, context, decision, rationale, consequences).

Responsibility: The project owner or architecture lead ensures these files are created and kept up‑to‑date; contributors must not modify them unless updating the respective domain.

## Specification System

If a `specs/` directory does not exist, create it. Inside `specs/` maintain a master build plan:

- `00-build-plan.md` – Top‑level document that splits the project into implementation phases. Each phase contains a list of implementation units, each sized roughly 2–6 hours of work. The file does **not** contain detailed specs; those live in per‑feature specification files (e.g., `01-user-auth.md`, `02-resume-upload.md`, etc.) which are referenced from the plan when needed.

## Architecture Governance

Every proposed architecture change must be documented with the following items before approval:

- **Reason** – Why the change is needed (problem statement, performance issue, new requirement).
- **Business value** – Expected impact on users, revenue, cost, or strategic goals.
- **Affected documents** – List of markdown/files that will need updates (e.g., `docs/DATABASE_DESIGN.md`, `context/architecture.md`, etc.).
- **Migration strategy** – Steps to migrate existing data or deploy the change with zero/low downtime (e.g., backward‑compatible schema change, feature flag, blue/green deployment).
- **Risks** – Potential downsides, failure modes, security implications, rollback complexity.
- **Benefits** – Quantifiable or qualitative improvements.
- **Rollback procedure** – Precise steps to revert the change and restore previous state.

Once approved, the change must be recorded in `CHANGELOG.md` (under the appropriate version) with a short summary and link to the detailed architecture decision record (if using ADRs). All architecture changes must go through the same review process as code changes (pull request with required approvals).

## Definition of Done

An implementation is considered complete only when all of the following are true:

- [x] Build passes (`npm run build` and backend `pip install` + `pytest` succeed).
- [x] Lint passes (ESLint, Tailwind lint, Ruff, Prettier checks with no errors).
- [x] Tests pass (unit, integration, end‑to‑end; coverage meets thresholds defined in `docs/TESTING_STRATEGY.md`).
- [x] Documentation updated (any affected `docs/`, `design/`, `context/`, or `specs/` file reflects the change).
- [x] Progress tracker updated (`context/progress-tracker.md` reflects completed work, any new open questions or architecture decisions are logged).
- [x] Architecture unchanged *or* any architectural change has been documented and approved per the Architecture Governance section.
- [x] No TODO comments remain in the codebase.
- [x] No dead or unreachable code.
- [x] Security review completed (no hard‑coded secrets, input validation, output encoding, proper authZ/authN).
- [x] Performance reviewed (no obvious regressions; benchmarks or profiling performed if the change is performance‑sensitive).
- [x] Logging added (appropriate structured log statements with relevant context).
- [x] Error handling implemented (graceful degradation, meaningful error messages, proper HTTP status codes).
- [ ] (Optional) Any feature‑flag or configuration changes are documented and communicated.

## Task Management

Work is tracked in the `tasks/` directory, organized by phase (e.g., `tasks/phase1.md`). Each task file contains high‑level objectives; individual implementation units should be captured in `context/progress-tracker.md`.

## Code Review

All changes must be reviewed for correctness, security, and performance before merging. Use the GitHub pull‑request process; ensure that the corresponding documentation updates accompany code changes.

---
*Document version: 1.0*  
*Last updated: 2026-07-14*