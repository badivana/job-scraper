# Screen Flow

## Purpose

To illustrate the navigation hierarchy and possible transitions between the principal screens (pages/routes) of the frontend application, helping designers, developers, and product managers understand how users move through the application.

## Contents

- Overview
- Main Navigation Structure
- Auth Flow Screens
- Core Feature Screens
- Modal & Overlay Flows
- Error & Edge‑Case Screens
- Responsive Adaptation
- Relation to User Journey Examples

## Overview

The frontend is built with Next.js 15 (App Router). Routes are defined as folders under `app/` (or `pages/` if using the Pages Router). The screen flow diagram captures the most common routes a user can traverse, grouped by feature area.

## Main Navigation Structure

- **Root (`/`)** – Home / Job Search page (displays search bar, filters, featured jobs, quick links).
- **`/jobs/[id]`** – Job Detail view (shows full description, match score breakdown, apply/save buttons).
- **`/resumes`** – Resume Hub (upload, view existing resumes, parse status).
- **`/resumes/[id]`** – Resume Detail (view parsed data, skills, option to re‑parse or delete).
- **`/applications`** – Application Kanban board (columns: Saved, Applied, OA, Interview, Offer, Rejected, Withdrawn).
- **`/messages`** – Notifications / In‑app messages (unread badge, list, detail view).
- **`/profile`** – Edit profile (personal info, links, preferences, notification settings).
- **`/settings`** – Application settings (privacy, data export, account deletion, linked OAuth providers).
- **`/auth/login`** – Sign‑in page (email/password, social buttons).
- **`/auth/register`** – Sign‑up page (email verification flow).
- **`/auth/verify-email`** – Email verification landing page (after clicking link).
- **`/auth/reset-password`** – Password reset request form.
- **`/auth/reset-password/[token]`** – Password reset form with token.
- **`/admin/*`** – (Only for users with `admin` or `service_role`) Admin dashboard: user management, scrape triggers, system metrics.
- **`/not-found`** – 404 page.
- **`/error`** – Generic error page (500).

## Auth Flow Screens

1. **Landing Page** (`/` or a dedicated landing) – shows value proposition, sign‑in / sign‑up links.
2. **Sign‑In** (`/auth/login`) – email + password fields, “Forgot password?” link, social login buttons (Google, GitHub).
3. **Sign‑Up** (`/auth/register`) – email, password, confirm password, optional profile fields; submits to Supabase Auth; upon success, sends verification email.
4. **Email Verification** – After clicking the link in the email, the user is routed to `/auth/verify-email` (shows success message and redirects to home).
5. **Forgot Password** – `/auth/reset-password`: user enters email → receives reset link.
6. **Reset Password** – `/auth/reset-password/[token]`: user sets new password → redirected to login.

## Core Feature Screens

### Home / Job Search (`/`)
- Input for free‑text query, dropdowns for location, radius, remote toggle, salary range, date posted, job type, experience level.
- “Search” button triggers API call to `/jobs/search`.
- Results displayed as a grid of job cards (each card shows title, company, location, salary badge, match‐score mini‑progress bar, apply/save icons).
- Infinite scroll or pagination controls at the bottom.

### Job Detail (`/jobs/[id]`)
- Header: job title, company logo, location, employment type badge, remote/hybrid/onsite indicator.
- Salary range (if available).
- Full description (rendered from HTML/markdown).
- Match score section: overall percentage + breakdown bars (skills, title, location, recency).
- Buttons: “Save”, “Unsave”, “Apply” (links to external `apply_url` and records click in `applications` table).
- “Generate Cover Letter” / “Generate Cold Email” buttons (invoke AI endpoints).
- “Share” and “Report” links.

### Resume Hub (`/resumes`)
- Upload area (drag‑&‑drop or browse) accepting PDF/DOCX up to 5 MB.
- List of existing resumes (most recent first): shows file name, upload date, parsed status, file size, actions (View, Re‑parse, Delete).
- Empty state illustration with guidance.

### Resume Detail (`/resumes/[id]`)
- File preview (if PDF) or download link.
- Extracted text (collapsible).
- Parsed sections: Summary, Experience (list of positions), Education, Skills, Certifications.
- Skills shown with confidence bars and option to edit/remove individual skill assignments.
- Button to “Re‑parse with latest model” (triggers background task).
- Download original file button.

### Application Kanban (`/applications`)
- Columns: Saved → Applied → OA (Online Assessment) → Interview → Offer → Rejected → Withdrawn (configurable).
- Each card shows job title, company, date moved into column, optional notes.
- Drag‑and‑drop moves a card between columns, updating the `applications` table timestamp and status.
- Clicking a card opens a slide‑out/detail view with full job info and ability to add/edit notes.
- Top‑right filter: show only applications from the last 30 days, 90 days, all.
- Empty state Illustrations for each column (e.g., no saved jobs yet).

### Messages / Notifications (`/messages`)
- Tabbed view: “All”, “Unread”.
- List ordered by newest first; each item shows icon (envelope for email, bell for in‑app), sender (System or Job Match), short preview, timestamp.
- Unread items highlighted (bold background).
- Clicking an item opens a modal or side drawer with full content.
- Bulk actions: Mark all as read, Delete selected.
- Settings link: “Notification Preferences” → leads to `/settings#notifications`.

### Profile (`/profile`)
- Sections: Personal Info (full name, avatar upload, bio, location, links).
- Preferences toggles: Email notifications (instant/daily/weekly), push notifications, data sharing consent.
- “Export My Data” button (generates GDPR export via `/api/v1/me/export`).
- “Delete Account” button (triggers confirmation flow, then calls deletion endpoint).

## Modal & Overlay Flows

- **Login/Sign‑Up Modal**: Can appear as a modal from the header for quick access (uses same routes but rendered in a dialog).
- **Job Apply Confirmation**: After clicking Apply, a modal confirms the external URL and offers to open it in a new tab or copy to clipboard.
- **Generate AI Content Modal**: Shows a spinner while the LLM works, then displays the result with options to Regenerate, Edit, Copy, Download (PDF).
- **Delete Confirmation**: Standard “Are you sure?” dialog with Cancel / Confirm buttons (destructive action red).
- **Filter Panel**: Slide‑out from right on desktop, full‑screen modal on mobile for refining search/filter criteria.
- **Help/Tooltips**: Small pop‑overs on hover/focus for icons with explanatory text (e.g., “What does match score mean?”).

## Error & Edge‑Case Screens

- **404 Not Found**: Shown when navigating to a non‑existent route; includes a search bar to get back on track.
- **500 Server Error**: Generic error page with a suggestion to refresh or contact support; logs the incident via Sentry.
- **Validation Errors**: Inline form errors (red text under fields) and toast notifications for non‑field errors.
- **Empty States**: Each list/view has an illustrative empty state with a clear call‑to‑action (e.g., “No saved jobs yet – start searching”).
- **Loading Skeletons**: Placeholder UI while data is being fetched (skeletons for cards, lists, skeletons for text blocks).

## Responsive Adaptation

- **Mobile (< 640 px)**: Bottom navigation bar (Home, Applications, Messages, Profile) or a hamburger menu opening a side drawer with the full nav list.
- **Tablet (640‑1023 px)**: Top navigation may collapse into a combo of icons + optional text; side drawer optionally available.
- **Desktop (≥ 1024 px)**: Full horizontal navigation bar (left: logo/search, center: search bar, right: user avatar + menu).

## User Journey Examples

### Typical Job Seeker Flow
1. **Landing** → **Sign‑Up** → **Email Verify** → **Home**.
2. **Home**: Enter “frontend developer” + location “Remote” → search.
3. **Results**: Scan cards, click a job → **Job Detail**.
4. **Job Detail**: Review match score, read description, click **Save** (bookmark).
5. **Repeat** steps 2‑4 for a few more jobs, building a saved list.
6. **Navigate to** `/resumes` → **Upload** a PDF resume → wait for parsing.
7. **Return to Home** → search again; now matches display personalized scores.
8. **Open a high‑score job** → click **Generate Cover Letter** → review, edit, download.
9. **Go to** `/applications` → drag saved job from “Saved” column to “Applied” (records click).
10. **Later**, update status to “OA”, then “Interview”, etc., as progress occurs.
11. **Check** `/messages` periodically for match notifications or system updates.
12. **Visit** `/profile` to adjust notification preferences (e.g., weekly digest only).
13. **Logout** when done.

### Recruiter / Admin Flow (if applicable)
1. **Login** → **Admin Dashboard**.
2. **View** system health: job ingest lag, user growth, match rates.
3. **Trigger** a manual scrape for a specific source (e.g., LinkedIn) via a button.
4. **Monitor** the Celery queue size and worker logs via integrated Grafana panel.
5. **Review** new sign‑up trends and possibly adjust feature flags (via Supabase `feature_flags` table) or notification preferences globally.

## Relation to User Flow & Wireframes

The screen flow complements the **User Flow** document (which focuses on end‑to‑end goals like “Find and apply to a job”) and the **Wireframes** (which give low‑fidelity sketches of each screen). Together they provide a complete picture of navigation, layout, and behavior.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*