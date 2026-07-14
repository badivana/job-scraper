# API Specification

## Purpose

To define the contract between the frontend, third‑party clients, and internal services. The API is documented using OpenAPI 3.0 (Swagger) and served at `/docs` (Swagger UI) and `/redoc` (ReDoc) in the FastAPI application.

## Contents

- Overview
- Authentication & Authorization
- Common Data Types
- Endpoint Groups
- Error Handling
- Versioning
- Security Considerations
- Example Requests & Responses
- How to Generate / Update the Spec

## Overview

The backend is built with FastAPI, which automatically generates an OpenAPI specification from the route definitions. The schema is versioned under `/api/v1/...`. All endpoints require a valid JWT issued by Supabase Auth (except the public documentation endpoints).

## Authentication & Authorization

- **Scheme**: `Bearer <JWT>`
- **Token Source**: Obtained via Supabase Auth (email/password, OAuth providers). The frontend stores the token in `localStorage` or a cookie and sends it in the `Authorization` header.
- **Validation**: The API verifies the token signature using Supabase’s JWKS endpoint (`https://<project>.supabase.co/auth/v1/keys`). It also checks the `exp` claim and that the token is not revoked (optional via a Redis‑based token blacklist).
- **Role Claims**: The token contains `role` (`anon` or `authenticated`). For endpoints that modify data, the backend additionally checks that the `sub` (user ID) matches the resource owner or that the user has an admin role (if applicable).
- **Endpoints Exempt from Auth**: `GET /docs`, `GET /redoc`, `GET /openapi.json`, `GET /health`.

## Common Data Types

| Type | Description | Example |
|------|-------------|---------|
| `UUID` | String in RFC4122 format | `"a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"` |
| `Timestamp` | ISO‑8601 UTC | `"2025-09-20T14:30:00Z"` |
| `JSONB` | Arbitrary JSON object | `{ "key": "value" }` |
| `Enum` | Pre‑defined string values | `"employment_type": "full-time"` |
| `Vector` | Array of floats (length 1536) | `[0.12, -0.34, … ]` (only used internally; not exposed in JSON) |
| `PageInfo` | Pagination metadata | `{ "limit": 20, "offset": 0, "total": 153 }` |

## Endpoint Groups

### Auth (proxy to Supabase)

The API does **not** implement its own auth endpoints; authentication is handled directly by Supabase. However, we provide convenience endpoints for token refresh and user metadata.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/auth/me` | Returns the authenticated user’s profile (joined from `auth.users` and `public.users`). Requires `Authorization: Bearer`. |
| `POST` | `/api/v1/auth/refresh` | Accepts a refresh token (httpOnly cookie) and returns new access and refresh tokens. |
| `POST` | `/api/v1/auth/logout` | Invalidates the refresh token (server‑side). |

### Users

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/users/{user_id}` | Retrieve a user’s public profile. |
| `PATCH` | `/api/v1/users/{user_id}` | Update profile fields (bio, location, avatar URL, etc.). |
| `GET` | `/api/v1/users/{user_id}/preferences` | Get notification & matching preferences. |
| `PATCH` | `/api/v1/users/{user_id}/preferences` | Update preferences. |

### Resumes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/resumes/upload` | Multipart/form‑data upload of PDF/DOCX. Returns resume ID and upload status. |
| `GET` | `/api/v1/resumes/{resume_id}` | Get resume metadata (excluding raw file). |
| `GET` | `/api/v1/resumes/{resume_id}/download` | Signed URL to download the original file (expires in 5 min). |
| `GET` | `/api/v1/resumes/{resume_id}/parse` | Returns parsed sections (JSON). |
| `POST` | `/api/v1/resumes/{resume_id}/reparse` | Trigger re‑extraction (e.g., after editing parsed fields). |
| `DELETE` | `/api/v1/resumes/{resume_id}` | Soft‑delete (mark `deleted_at`). |
| `GET` | `/api/v1/resumes` | List user’s resumes with pagination. |

### Jobs

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/jobs/search` | Full‑text + faceted search. Query params: `q`, `location`, `remote_only`, `salary_min`, `salary_max`, `employment_type`, `date_posted`, `sort`, `limit`, `offset`. |
| `GET` | `/api/v1/jobs/{job_id}` | Get a single job by ID. |
| `GET` | `/api/v1/jobs/{job_id}/similar` | Returns jobs similar to the given one (based on vector similarity). |
| `POST` | `/api/v1/jobs/{job_id}/save` | Save a job for the authenticated user. |
| `DELETE` | `/api/v1/jobs/{job_id}/save` | Unsave a job. |
| `POST` | `/api/v1/jobs/{job_id}/apply` | Record an application click (updates `applications` table). |
| `GET` | `/api/v1/jobs` | List recent jobs (admin only, or public with limit). |

### Matching

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/matching/{user_id}` | Get top‑N job matches for the user. Query params: `limit`, `offset`, `min_score`. |
| `GET` | `/api/v1/matching/{user_id}/score/{job_id}` | Returns detailed score breakdown for a specific job (debug). |

### Application Materials (AI)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/ai/cover-letter` | Input: `{ resume_id, job_id }`. Output: generated cover letter text. |
| `POST` | `/api/v1/ai/cold-email` | Input: `{ resume_id, job_id }`. Output: short outreach email. |
| `POST` | `/api/v1/ai/skill-gap` | Input: `{ resume_id, job_id }`. Output: list of missing skills with suggestions. |
| `GET` | `/api/v1/ai/{doc_type}/{doc_id}` | Retrieve generated document metadata. |
| `GET` | `/api/v1/ai/{doc_type}/{doc_id}/download` | Signed URL for PDF/DOCX version. |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/notifications` | List user’s notifications (unread first). |
| `PATCH` | `/api/v1/notifications/{notif_id}/read` | Mark as read. |
| `DELETE` | `/api/v1/notifications/{notif_id}` | Delete notification. |
| `POST` | `/api/v1/preferences/notifications` | Update notification preferences (frequency, channels). |

### Admin

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/admin/stats` | System usage statistics (requires `role: admin` claim). |
| `POST` | `/api/v1/admin/scraping/{source}/run` | Trigger a manual scrape for a source (LinkedIn, Wellfound, etc.). |
| `GET` | `/api/v1/admin/scraping/{source}/status` | Get last run status, latency, error count. |
| `POST` | `/admin/maintenance/reindex` | Rebuild pgvector indexes (maintenance window). |
| `GET` | `/admin/logs` | Paginated audit log (admin only). |

## Error Handling

All errors return a JSON object:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable description",
    "details": [ { "field": "email", "issue": "invalid format" } ] // optional
  }
}
```

HTTP status codes follow REST conventions:
- `200` – Success
- `201` – Created
- `400` – Bad request (validation)
- `401` – Unauthorized (missing/invalid token)
- `403` – Forbidden (insufficient permissions)
- `404` – Not found
- `409` – Conflict (e.g., duplicate resource)
- `422` – Unprocessable entity (schema validation)
- `429` – Too Many Requests (rate limit)
- `500` – Internal server error
- `502` – Bad gateway (external API failure)
- `503` – Service unavailable (temporary overload)

## Versioning

The API is versioned in the URL path (`/api/v1/...`). Breaking changes increment the version number (v2). Minor backward‑compatible changes (adding fields, optional parameters) stay within v1.

## Security Considerations

- All endpoints enforce HTTPS; HSTS is enabled.
- Rate limiting: anonymous IP – 60 req/min; authenticated user – 300 req/min; AI endpoints – 30 req/min per user.
- Input validation via Pydantic models; output encoding prevents XSS.
- No sensitive data (passwords, tokens) is logged; logs are scrubbed.
- CORS restricted to the frontend domain(s).
- Trusted proxy headers only if behind a known load balancer.

## Example Requests & Responses

### Register (via Supabase Auth – client side)

```http
POST https://<project>.supabase.co/auth/v1/signup
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "strongPassword123"
}
```

Response includes `access_token` and `refresh_token`.

### Get User Profile

```http
GET /api/v1/auth/me
Authorization: Bearer <jwt>
```

```json
{
  "id": "11111111-2222-3333-4444-555555555555",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "avatar_url": "https://.../avatars/xxx.png",
  "bio": "Software engineer …",
  "location": "New York, NY",
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-06-10T12:34:56Z"
}
```

### Search Jobs

```http
GET /api/v1/jobs/search?q=software%20engineer&remote_only=true&limit=10
Authorization: Bearer <jwt>
```

```json
{
  "items": [
    {
      "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
      "title": "Software Engineer",
      "company": "TechCorp",
      "location": { "city": "Remote", "country": "USA" },
      "salary_min": 90000,
      "salary_max": 120000,
      "employment_type": "full-time",
      "remote_flag": true,
      "posted_date": "2025-09-18T09:15:00Z",
      "apply_url": "https://techcorp.com/jobs/123",
      "match_score": 87
    }
  ],
  "page": { "limit": 10, "offset": 0, "total": 157 }
}
```

### Generate Cover Letter

```http
POST /api/v1/ai/cover-letter
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "resume_id": "11111111-2222-3333-4444-555555555555",
  "job_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
}
```

```json
{
  "generated_text": "Dear Hiring Manager,\nI am excited to apply for the Software Engineer role at TechCorp…",
  "format": "plain",
  "token_usage": { "prompt_tokens": 540, "completion_tokens": 210 }
}
```

## How to Generate / Update the Spec

The OpenAPI JSON/YAML is generated automatically by FastAPI from the route definitions and Pydantic models.

To export:
```bash
uvicorn app.main:app --export-openapi-json openapi.json
```

Or retrieve from the running service:
```bash
curl -s https://api.example.com/openapi.json > openapi.json
```

When adding new endpoints, ensure:
- Pydantic models include proper Field descriptions.
- Docstrings on route functions become the endpoint description.
- Tag the router appropriately for grouping in Swagger UI.

Commit the generated `openapi.json` to the repository under `docs/openapi.json` for reference, but the source of truth remains the code.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*