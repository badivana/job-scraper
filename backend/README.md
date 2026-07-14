# Backend Service

## Purpose

This document provides guidance on setting up, running, and developing the backend service for the AI-Powered Job Finder. The backend is a FastAPI application that handles business logic, data persistence, and integration with external services.

## Contents

- Overview
- Prerequisites
- Installation
- Environment Variables
- Running the Application
- Running Tests
- Database Migrations
- API Documentation
- Project Structure
- Contributing

## Overview

The backend implements the core functionality of the Job Finder platform:
- Job ingestion via Apify
- Resume upload, parsing, and embedding generation
- Job‑resume matching using pgvector similarity search
- AI‑powered cover letter, cold email, and skill‑gap generation
- Notification delivery (email and in‑app)
- Scheduling and background task management (Celery)
- Administrative utilities

It communicates with Supabase (PostgreSQL with pgvector, Auth, Storage), Redis, Apify, and OpenAI.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git
- (Optional) Docker and Docker Compose for containerized development
- A Supabase project with the `pgvector`, `uuid-ossp`, and `btree_gin` extensions enabled
- A Redis instance (local or managed)
- API keys for Apify and OpenAI

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/job-finder.git
   cd job-finder/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Copy the example environment file and fill in the required values:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase URL, service role key, Redis URL, Apify token, OpenAI key, etc.
   ```

## Environment Variables

The following environment variables are read by the application (see `.env.example` for a template):

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode (auto‑reload, verbose logs) | `true` |
| `LOG_LEVEL` | Logging level (`trace`, `debug`, `info`, `warn`, `error`) | `info` |
| `ENVIRONMENT` | Deployment label (`development`, `staging`, `production`) | `development` |
| `DATABASE_URL` | PostgreSQL connection string (Supabase) | `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres` |
| `REDIS_URL` | Redis connection string | `redis://:password@host:6379/0` |
| `SUPABASE_URL` | Supabase REST endpoint (optional if using only DB) | `https://xyzcompany.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (bypasses RLS) | `service_role_...` |
| `APIFY_API_TOKEN` | Token for Apify API | `apify_api_...` |
| `OPENAI_API_KEY` | Token for OpenAI API | `sk-...` |
| `SMTP_HOST` | SMTP server for email | `smtp.sendgrid.net` |
| `SMTP_PORT` | SMTP port (usually 587) | `587` |
| `SMTP_USER` | SMTP username | `apikey` |
| `SMTP_PASS` | SMTP password or API key | `SG.xxx` |
| `MAIL_FROM` | Sender address for outgoing emails | `no-reply@jobfinder.example.com` |
| `SENTRY_DSN` | Optional Sentry DSN for error tracking | `https://xxx@o1.ingest.sentry.io/123456` |
| `CELERY_BROKER_URL` | Usually same as `REDIS_URL` | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Result backend (can be Redis or DB) | `redis://localhost:6379/1` |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes (e.g., 5 MB = 5242880) | `5242880` |
| `JWT_ALGORITHM` | JWT verification algorithm (`RS256`) | `RS256` |
| `JWT_AUDIENCE` | Expected `aud` claim (`authenticated` or `service_role`) | `authenticated` |
| `PORT` | Port for the Uvicorn server (default 8000) | `8000` |

## Running the Application

### Development Mode (with auto‑reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive documentation is at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Mode

For production, use a proper ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
```

### Using Docker Compose

A `docker-compose.yml` is provided at the repository root. To start the backend alongside the required services:

```bash
cd ..
docker compose up --build
```

Then apply migrations:

```bash
docker compose exec backend alembic upgrade head
```

## Running Tests

### Unit Tests

```bash
# Ensure test dependencies are installed
pip install -r requirements-test.txt   # if separate file exists
pytest
```

To see coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

### Integration Tests

Integration tests rely on a running PostgreSQL and Redis instance. You can use the Docker Compose test override:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

Please refer to the `tests/` directory for details.

## Database Migrations

We use Alembic for schema migrations. Migration scripts are stored in `alembic/versions/`.

To create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "describe change"
```

To apply pending migrations:

```bash
alembic upgrade head
```

To rollback the last migration:

```bash
alembic downgrade -1
```

In production, migrations should be applied as part of the deployment process.

## API Documentation

When the server is running, the interactive API documentation is available at:
- Swagger UI: `http://<host>:<port>/docs`
- ReDoc: `http://<host>:<port>/redoc`

The OpenAPI JSON schema can be retrieved at:
`http://<host>:<port>/openapi.json`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app creation and middleware
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/        # API route modules (users.py, resumes.py, jobs.py, etc.)
│   ├── core/                   # Configuration, logging, security, exception handlers
│   │   ├── config.py
│   │   ├── logging.py
 
```

(Continue the structure as needed; the above is a sample.)

## Contributing

Please read `CONTRIBUTING.md` (located in the repository root) for details on our code of conduct and the process for submitting pull requests.

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Make your changes.
4. Ensure tests pass and linting is clean.
5. Commit your changes (`git commit -am 'Add amazing feature'`).
6. Push to the branch (`git push origin feature/amazing-feature`).
7. Open a pull request against the `main` branch.

Kindly adhere to the coding standards defined in `docs/CODING_STANDARDS.md`.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*