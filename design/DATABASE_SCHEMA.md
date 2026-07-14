# Database Schema

This document outlines the database schema for the AI-Powered Job Finder using Supabase PostgreSQL. Refer to `DATABASE_DESIGN.md` for detailed definitions, constraints, indexes, and relationships.

## Tables Overview

- `users`
- `resumes`
- `jobs`
- `saved_jobs`
- `applications`
- `generated_documents`
- `notifications`
- `search_history`
- `audit_log`
- `scheduled_tasks`

Each table uses UUID primary keys, timestamps with timezone, and appropriate foreign key constraints. The schema leverages the `pgvector` extension for similarity search columns.

For the full DDL and explanatory notes, see `DATABASE_DESIGN.md`.