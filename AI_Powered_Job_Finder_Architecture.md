# AI-Powered Job Finder Architecture

## Overview

An end-to-end platform that: - Scrapes jobs from multiple sources using
Apify - Matches jobs against a user's resume using AI - Displays jobs in
a modern dashboard - Tracks applications - Generates cover letters and
recruiter outreach

------------------------------------------------------------------------

# High-Level Architecture

``` text
                         Internet
                             │
                    ┌────────▼────────┐
                    │   Next.js App   │
                    │ React + TS      │
                    └────────┬────────┘
                             │
                     REST / WebSocket
                             │
                  ┌──────────▼──────────┐
                  │     FastAPI API     │
                  └───────┬─────┬────────┘
                          │     │
                  ┌───────▼─┐ ┌─▼─────────┐
                  │Auth/JWT │ │ AI Engine │
                  └─────────┘ └───────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
 ┌──────▼──────┐  ┌───────▼────────┐ ┌──────▼─────────┐
 │ Job Service │  │ Resume Matcher │ │ Apply Tracker  │
 └──────┬──────┘  └──────┬─────────┘ └──────┬─────────┘
        │                │                 │
     PostgreSQL      pgvector          PostgreSQL
        │
   ┌────▼────┐
   │  Redis  │
   └────┬────┘
        │
┌───────▼────────────────────────────┐
│ Background Workers (Celery/APS)    │
└──────────────┬─────────────────────┘
               │
        ┌──────▼────────────────────────────┐
        │             Apify                 │
        │ LinkedIn Jobs                     │
        │ Wellfound                         │
        │ Greenhouse                        │
        │ Lever                             │
        │ Indeed                            │
        │ Company Career Pages              │
        └───────────────────────────────────┘
```

------------------------------------------------------------------------

# Tech Stack

  Layer           Technology
  --------------- ----------------------------
  Frontend        Next.js, React, TypeScript
  UI              Tailwind CSS, shadcn/ui
  Backend         FastAPI
  ORM             SQLAlchemy
  Database        PostgreSQL
  Vector Search   pgvector
  Cache           Redis
  Scheduler       APScheduler / Celery
  AI              OpenAI GPT
  Scraping        Apify
  Storage         S3 / Supabase
  Auth            JWT / OAuth

------------------------------------------------------------------------

# Backend Services

    backend/
    ├── gateway/
    ├── auth-service/
    ├── job-service/
    ├── resume-service/
    ├── ai-service/
    ├── recruiter-service/
    ├── analytics-service/
    ├── notification-service/
    ├── scheduler/
    └── worker/

------------------------------------------------------------------------

# Frontend Structure

    frontend/
    ├── app/
    ├── components/
    ├── dashboard/
    ├── jobs/
    ├── companies/
    ├── resume/
    ├── analytics/
    ├── profile/
    ├── hooks/
    ├── lib/
    └── types/

------------------------------------------------------------------------

# Core Features

## Job Scraping

-   LinkedIn
-   Wellfound
-   Greenhouse
-   Lever
-   Indeed
-   Company Career Pages

## Dashboard

-   Search
-   Filters
-   Match score
-   Save jobs
-   Apply link
-   Company insights

## AI Features

-   Resume parsing
-   Skill extraction
-   Job matching
-   Cover letter generation
-   Cold email generation
-   Skill-gap analysis

## Application Tracking

Stages: 1. Saved 2. Applied 3. OA 4. Interview 5. Offer 6. Rejected

------------------------------------------------------------------------

# Database

    Users
    Jobs
    Companies
    Recruiters
    Resumes
    Skills
    Applications
    SavedJobs
    Notifications
    SearchHistory

------------------------------------------------------------------------

# Data Pipeline

    Apify
       ↓
    Raw JSON
       ↓
    Cleaner
       ↓
    Deduplication
       ↓
    Normalization
       ↓
    PostgreSQL
       ↓
    FastAPI
       ↓
    Next.js Dashboard

------------------------------------------------------------------------

# Future Enhancements

-   Resume ATS scoring
-   AI interview coach
-   Referral tracker
-   Daily job alerts
-   Chrome extension
-   Salary insights
-   Mobile app
-   Semantic job search
-   Duplicate job detection

------------------------------------------------------------------------

# Deployment

-   Docker
-   GitHub Actions
-   Railway / Render / AWS
-   PostgreSQL
-   Redis

This architecture is modular, scalable, and suitable for evolving from a
personal project into a production-ready SaaS.
