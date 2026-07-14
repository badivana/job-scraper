# Environment Setup

## Purpose

To guide developers through setting up a local development environment for the AI‑Powered Job Finder project. This includes installing dependencies, configuring required services (Supabase, Redis, etc.), running the application, and running tests.

## Contents

- Prerequisites
- Quick Start (Docker‑Compose)
- Manual Setup (Optional)
- Configuring Supabase (Self‑hosted or Using Supabase CLI)
- Environment Variables
- Running the Application
- Running Tests
- Troubleshooting
- Frequently Asked Questions

## Prerequisites

| Tool | Minimum Version | Installation Link |
|------|----------------|-------------------|
| **Git** | 2.35+ | https://git-scm.com/ |
| **Node.js** | 20.x (LTS) | https://nodejs.org/ |
| **npm** | 10.x (comes with Node) | – |
| **Python** | 3.12.x | https://www.python.org/downloads/ |
| **pip** | 24.x (comes with Python) | – |
| **Docker Engine** | 24.x | https://docs.docker.com/engine/install/ |
| **Docker Compose** | v2 (plug‑in) | Install with Docker Desktop or standalone |
| **Make** (optional) | 4.3+ | GNU make |
| **OpenSSL** (for generating local certs if needed) | 3.0+ | Usually pre‑installed on macOS/Linux; Windows via WSL or Git Bash |

> **Note**: For Windows users, it is recommended to use **WSL2** (Ubuntu) to avoid path and permission issues.

### Verify Installation

Run the following commands in a terminal (PowerShell, CMD, bash, or zsh):

```bash
git --version
node --version
npm --version
python --version
pip --version
docker --version
docker compose version
```

All should return a version number without errors.

## Quick Start (Docker‑Compose)

The repository ships with a `docker-compose.yml` that starts all required services:

- **PostgreSQL 15** (with `pgvector`, `uuid-ossp`, `btree_gin` extensions)
- **Redis 7**
- **Mailhog** (SMTP debugger for emails)
- **(Optional) MinIO** (S3‑compatible mock for Supabase Storage, if you want to test storage locally)

### Step‑by‑Step

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/job-finder.git
   cd job-finder
   ```

2. **(Optional) Create a `.env` file**  
   Copy the example file and adjust if needed:

   ```bash
   cp .env.example .env
   ```

   The default `.env` already contains sensible defaults for local development (see the **Environment Variables** section below). You normally do **not** need to edit it for a first run.

3. **Start the stack**

   ```bash
   docker compose up --build
   ```

   Docker will pull/build the necessary images and start the containers. You should see logs for each service.

4. **Initialize the database** (run migrations)

   In a new terminal, execute:

   ```bash
   docker compose exec backend alembic upgrade head
   ```

   This will apply any pending Alembic migrations to the Postgres database.

5. **Seed data (optional)**  
   If there is a seed script, run it:

   ```bash
   docker compose exec backend python -m scripts.seed
   ```

   (Skip if not provided.)

6. **Access the applications**

   - **Frontend**: Open a browser to `http://localhost:3000` (Next.js dev server).
   - **Backend API Docs**: Visit `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc).
   - **Mailhog UI**: `http://localhost:8025` – view captured emails.
   - **(Optional) MinIO Console**: `http://localhost:9001` – login with `minioadmin` / `minioadmin`.

7. **Stop the stack**

   When finished, return to the terminal running `docker compose up` and press `Ctrl+C`, then run:

   ```bash
   docker compose down -v   # -v removes named volumes (clears data)
   ```

   Omit `-v` if you want to persist the database across restarts.

## Manual Setup (Optional)

If you prefer to run parts of the stack outside Docker (e.g., for faster hot‑reloading of the frontend or backend), you can follow these steps.

### Backend (FastAPI) – Manual

1. **Set up a virtual environment**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt   # if exists (includes pytest, etc.)
   ```

3. **Configure environment variables**  
   Create a `.env` file in the `backend/` directory (copy from root `.env.example` if needed) and fill:

   ```
   DEBUG=True
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
   REDIS_URL=redis://localhost:6379/0
   SUPABASE_URL=http://localhost:54321   # if using Supabase locally via supabase-cli (see below)
   SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
   APIFY_API_KEY=your_apify_key
   OPENAI_API_KEY=your_openai_key
   SMTP_HOST=localhost
   SMTP_PORT=1025
   SMTP_USER=
   SMTP_PASS=
   ```

4. **Run migrations**

   ```bash
   alembic upgrade head
   ```

5. **Start the backend**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`.

### Frontend (Next.js) – Manual

1. **Install Node dependencies**

   ```bash
   cd ../app   # assuming repo root
   npm ci
   ```

2. **Create a `.env.local` file** (Next.js loads this automatically)

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL= (optional, if using Supabase client directly)
   NEXT_PUBLIC_ENABLE_REALTIME=false
   ```

3. **Start the dev server**

   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`.

### Using Supabase Locally (Optional)

If you prefer to run a **local Supabase stack** instead of relying on the bundled PostgreSQL only, you can use the Supabase Docker suite.

1. **Install Supabase CLI** (https://supabase.com/docs/guides/cli)

   ```bash
   # macOS (brew)
   brew install supabase/tap/supabase
   # Linux (script)
   curl -s https://supabase.com/cli | sh
   # Windows (scoop) or via npm:
   npm i -g supabase
   ```

2. **Initialize Supabase locally**

   ```bash
   supabase init
   ```

   This creates a `supabase/` folder with config.

3. **Start Supabase services**

   ```bash
   supabase start
   ```

   This will start:
   - Kong API gateway
   - GoTrue (auth)
   - PostgREST
   - Realtime server
   - Storage service
   - PostgreSQL (with extensions enabled)
   - Studio dashboard (normally on `http://localhost:54323`)

4. **Retrieve connection info**

   ```bash
   supabase status
   ```

   It will output something like:

   ```
   API URL: http://localhost:54321
   DB URL: postgres://postgres:postgres@localhost:54322/postgres
   ANON KEY: anon_key_...
   SERVICE_ROLE_KEY: service_role_key_...
   ```

5. **Update `.env`** (or backend `.env` and frontend `.env.local`) with the values above.

6. **Stop Supabase when done**

   ```bash
   supabase stop
   ```

   (This does not delete the data volume; `supabase start` will resume where you left off.)

> **Tip**: If you use the local Supabase stack, you can omit the separate PostgreSQL and Redis containers from `docker-compose.yml` (or keep Redis for caching). Adjust the compose file accordingly.

## Environment Variables

All services read configuration from environment variables. The table below lists the most important ones, their purpose, and example values for a local development setup.

| Variable | Scope | Description | Example (dev) |
|----------|-------|-------------|---------------|
| `DEBUG` | Backend | Enable debug mode (more verbose logging, auto‑reload). | `true` |
| `LOG_LEVEL` | All | Logging level (`trace`, `debug`, `info`, `warn`, `error`). | `info` |
| `ENVIRONMENT` | All | Deployment label (`development`, `staging`, `production`). | `development` |
| `DATABASE_URL` | Backend & Workers | PostgreSQL connection string. Format: `postgresql://[user]:[password]@[host]:[port]/[db]` | `postgresql://postgres:postgres@localhost:5432/postgres` |
| `REDIS_URL` | Backend & Workers | Redis connection string. | `redis://localhost:6379/0` |
| `SUPABASE_URL` | Backend & Workers (if using Supabase directly) | Base URL of Supabase REST API (e.g., `https://<project>.supabase.co`). | `http://localhost:54321` (local supabase) |
| `SUPABASE_ANON_KEY` | Frontend (optional) & Backend (if using anon) | Public anon key for Supabase client. | `anon_key_...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend & Workers | Privileged key that bypasses RLS (used by backend). | `service_role_key_...` |
| `APIFY_API_KEY` | Backend | Token for calling Apify API. | `apify_api_…` |
| `OPENAI_API_KEY` | Backend | Token for OpenAI API. | `sk-…` |
| `SMTP_HOST` | Workers | SMTP server for sending emails. | `localhost` (Mailhog) |
| `SMTP_PORT` | Workers | SMTP port. | `1025` |
| `SMTP_USER` | Workers | SMTP username (often `apikey` for Mailgun/SendGrid). | *(empty for Mailhog)* |
| `SMTP_PASS` | Workers | SMTP password or API key. | *(empty for Mailhog)* |
| `MAIL_FROM` | Workers | Sender address used in outgoing emails. | `no-reply@example.com` |
| `SENTRY_DSN` | All (optional) | DSN for error tracking. | *(empty in dev)* |
| `CELERY_BROKER_URL` | Workers | Usually same as `REDIS_URL`. | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Workers | Result backend (can be Redis or DB). | `redis://localhost:6379/1` |
| `MAX_CONTENT_LENGTH` | Backend | Max request body size in bytes for file uploads (e.g., 5 MB = 5242880). | `5242880` |
| `JWT_ALGORITHM` | Backend | Algorithm used to verify Supabase JWT (`RS256`). | `RS256` |
| `JWT_AUDIENCE` | Backend | Expected `aud` claim in JWT (`authenticated` or `service_role`). | `authenticated` |
| `NEXT_PUBLIC_API_URL` | Frontend | Base URL of the backend API (used by browser). | `http://localhost:8000` |
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend (optional) | If using Supabase client directly (e.g., for auth UI). | `http://localhost:54321` |
| `NEXT_PUBLIC_ENABLE_REALTIME` | Frontend | Set `true` to enable realtime subscription features. | `false` |
| `PORT_BACKEND` | Backend (if overriding) | Port for the Uvicorn server. | `8000` |
| `PORT_FRONTEND` | Frontend (if overriding) | Port for Next.js dev server (default 3000). | `3000` |

> **Note**: Variables prefixed with `NEXT_PUBLIC` are exposed to the browser; never put secret values there.

## Running the Application

### Using Docker‑Compose (Recommended for Consistency)

```bash
# Build and start all services
docker compose up --build

# In another terminal, apply DB migrations
docker compose exec backend alembic upgrade head

# (Optional) Load seed data
docker compose exec backend python -m scripts.seed

# Access:
#   Frontend: http://localhost:3000
#   Backend API docs: http://localhost:8000/docs
#   Mailhog: http://localhost:8025
```

### Manual (Backend + Frontend + External Services)

1. Ensure you have a running PostgreSQL (locally or via Supabase), Redis, and an SMTP mock (Mailhog) or real server.
2. Export environment variables (or have them in a `.env` file).
3. Start the backend:

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Start the frontend:

   ```bash
   cd ../app
   npm run dev
   ```

5. Use the application as described above.

### Running Tests

#### Backend Tests

```bash
cd backend
# Install test dependencies if not already installed
pip install -r requirements-test.txt   # if exists
# Run pytest
pytest
# To see coverage:
pytest --cov=app --cov-report=term-missing
```

#### Frontend Tests

```bash
cd ../app
# Install if needed (usually already done)
npm ci
# Run unit tests (Jest + React Testing Library)
npm test
# For watch mode:
npm test -- --watch
# To run with coverage:
npm test -- --coverage
```

#### End‑to‑End Tests (Playwright)

```bash
cd ../tests   # if e2e tests live in a top-level tests folder
# Install Playwright browsers (first time only)
npx playwright install
# Run tests
npx playwright test
# To open HTML report:
npx playwright show-report
```

#### Running Specific Test Suites

- Use `pytest -k "expressions"` to filter by name.
- Use `npm test -- -t "pattern"` for Jest.

#### Linting & Formatting

- **Backend**: `ruff check .`, `black --check .`, `mypy .`
- **Frontend**: `npm run lint` (`eslint`), `npm run format` (`prettier --check`)

## Troubleshooting

### Docker‑Compose Issues

- **Containers exit immediately**  
  Check logs: `docker compose logs <service>`. Common causes: missing env vars, port conflicts, failed database connection.
- **Port already in use**  
  Ensure no other service is using the same host port (e.g., another Postgres on 5432). Change the host port in `docker-compose.yml` (`"5433:5432"`).
- **Database migration fails**  
  Verify the `DATABASE_URL` points to the correct container (`db` service). Inside the container, the host is `db`.  
  Example: `postgresql://postgres:postgres@db:5432/postgres`.
- **Mailhog not capturing emails**  
  Ensure the worker/service is configured to use `SMTP_HOST=mailhog`, `SMTP_PORT=1025`.

### Backend Issues

- **ImportError: No module named '...'**  
  Make sure the virtual environment is activated and dependencies installed.
- **Database connection refused**  
  Confirm Postgres is reachable: `pg_isready -h localhost -p 5432 -U postgres`.  
  If using Docker, ensure the service name is correct (`db`).
- **Token validation fails**  
  Check that `SUPABASE_SERVICE_ROLE_KEY` is correct and corresponds to the same project as `SUPABASE_URL`.
- **Redis connection error**  
  Test with `redis-cli -h localhost -p 6379 ping`. Should return `PONG`.

### Frontend Issues

- **Module not found: Can't resolve '...'**  
  Run `npm ci` again to ensure node_modules are in sync.
- **HMR not working**  
  Verify you're running `npm run dev`, not `npm start` (production build).
- **Blank screen**  
  Open devtools console (F12) for errors; often due to missing `NEXT_PUBLIC_API_URL` or CORS issues.

### Testing Issues

- **Tests fail because of missing env vars**  
  Provide a `.env.test` file or export variables before running `pytest`/`npm test`.
- **Chromium not found (Playwright)**  
  Run `npx playwright install` once to download browsers.

### General Tips

- **Logs are your friend** – always check container logs (`docker compose logs -f <service>`).
- **Restarting services** – `docker compose restart <service>` often resolves transient glitches.
- **Disk space** – Docker images and volumes can consume space; periodically prune with `docker system prune -af --volumes` (careful, removes unused data).
- **Switching between local Supabase and external Supabase** – just change `SUPABASE_URL`/`SERVICE_ROLE_KEY` in `.env` and restart containers.

## Frequently Asked Questions (FAQ)

**Q: Do I need a paid Supabase plan for local development?**  
A: No. The provided `docker-compose.yml` includes a self‑hosted PostgreSQL with the required extensions (`pgvector`, `uuid-ossp`, `btree_gin`). If you want to test Supabase‑specific features (Auth, Storage, Realtime) you can use the free tier of Supabase (which is generous for development) or run the local Supabase stack via `supabase start`.

**Q: Can I use Yarn or pnpm instead of npm?**  
A: Yes. The project lockfile is `package-lock.json`, but `yarn install --frozen-lockfile` or `pnpm install --frozen-lockfile` will work. Just ensure you run the corresponding scripts (`yarn dev`, `pnpm dev`).

**Q: I see a CORS error when the frontend calls the backend.**  
A: Ensure the backend’s CORS middleware allows the frontend’s origin. In `core/middleware.py` (or similar), the `allow_origins` list should contain `http://localhost:3000` (and any other dev origins). Also confirm that you’re not accidentally calling `http://127.0.0.1:3000` while the server expects `localhost`.

**Q: My uploads fail with “file too large”.**  
A: Check `MAX_CONTENT_LENGTH` in the backend environment. Increase it if needed (e.g., `10485760` for 10 MB) and redeploy/re‑start the containers.

**Q: How do I reset the database to a clean state?**  
A: With Docker‑Compose, run `docker compose down -v` to remove volumes, then `docker compose up -d` and re‑run migrations. If you only want to drop and recreate the schema while keeping the volume, you can `docker compose exec backend psql -U postgres -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"` and then run migrations.

**Q: Where can I find the API documentation while developing?**  
A: When the backend is running, navigate to `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc). They are generated automatically from the FastAPI code.

**Q: I want to test email functionality without spamming real addresses.**  
A: The development setup includes Mailhog (`http://localhost:8025`). Configure the worker to use `SMTP_HOST=mailhog`, `SMTP_PORT=1025`. All emails will be captured and viewable in the Mailhog UI.

**Q: How do I upgrade a dependency safely?**  
A: For frontend, run `npm outdated`, then `npm install <package>@<desired>` and commit the updated `package-lock.json`. For backend, edit `requirements.txt` (or `requirements.in` if using `pip-tools`) and run `pip-compile` (if using) or `pip install -U <package>` then freeze again. Run the test suite to ensure nothing breaks.

**Q: Is there a way to run only the backend workers without the API?**  
A: Yes. You can start the container with an overridden command, e.g.:

   ```bash
   docker compose run --service-ports backend celery -A app.worker worker --loglevel=info
   ```

   Or define a separate service in `docker-compose.yml` that uses the same image but different command.

**Q: My machine is low on RAM; can I skip some services?**  
A: You can disable non‑essential services for lightweight mode: run only postgres, redis, backend, and frontend. Comment out `mailhog` and `minio` in `docker-compose.yml` if you don’t need email/storage previews. The app will still work; emails will be logged (if using a dummy SMTP) or fail silently if you haven’t configured a real SMTP.

**Q: How do I contribute a new feature?**  
A: Fork the repo, create a feature branch (`feat/your-feature`), implement, write tests, ensure lint passes, open a Pull Request against `main`. Follow the pull request template (if present) and address reviewer feedback.

**Q: Where do I ask for help?**  
A: Check the project’s `README.md` for links to community channels (Discord, Slack, or GitHub Discussions). For urgent issues, open a GitHub Issue with the label `help wanted` or `question`.

## Summary

You now have a fully functional local development environment that mirrors the production stack (PostgreSQL with pgvector, Supabase Auth & Storage, Redis, Celery workers, Next.js frontend, FastAPI backend). Use the Docker‑Compose method for the easiest, most reproducible setup, or opt for a manual configuration if you prefer tighter control over individual components. With the environment ready, you can proceed to implement features, run tests, and prepare for deployment.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*