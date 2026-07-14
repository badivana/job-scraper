# 0>
<parameter=content>
# 002C-frontend-auth.md

## Objective
Add authentication support to the Next.js frontend: Supabase client initialization, middleware (or route guards) to protect pages, login/logout UI, and handling of tokens/session via cookies.

## Scope
- Create a singleton Supabase client (`lib/supabaseClient.js`) using the anon key.
- Implement Next.js middleware (`middleware.ts`) that runs on every request, checks for a valid Supabase session (via the cookie), and redirects unauthenticated users to `/login`.
- Build login page (`pages/login.tsx`) with email/password form and OAuth buttons (Google, GitHub).
- Build registration page (`pages/register.tsx`) (optional – can be handled via login page toggle).
- Implement logout action (API route or client‑side call to Supabase `signOut`) that clears cookies and redirects to login.
- Provide a protected wrapper component (`withAuth`) or use `getServerSideProps` to fetch user data for dashboard‑style pages (future phases).
- Ensure that the app works with the same cookie‑based session that the backend expects (httpOnly, Secure, SameSite‑Strict) – the frontend will read the cookie via Supabase JS client.
- Add necessary environment variables to `.env.example` (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
- Update `LOCAL_SETUP.md` with instructions for running the frontend and confirming auth flow.

## Deliverables
1. `lib/supabaseClient.js` – exports `createClient()` that returns a Supabase instance.
2. `middleware.ts` at the project root (or `src/middleware.ts` if using src folder) that:
   - Calls `supabase.auth.getUser()`.
   - If no user and the requested path is not in the public whitelist (`/login`, `/register`, `/auth/*`, `/_next/*`, `/api/*`), redirects to `/login`.
   - Otherwise calls `NextResponse.next()`.
3. `pages/login.tsx`:
   - Form with email, password, "Log in" button.
   - On submit, calls `supabase.auth.signInWithPassword`.
   - On success, redirects to a protected page (e.g., `/dashboard` placeholder) or reloads.
   - Shows generic error messages to avoid email enumeration.
   - Buttons for "Sign in with Google" and "Sign in with GitHub" that trigger `supabase.auth.signInWithOAuthProvider`.
4. `pages/register.tsx` (optional) similar to login but using `signUp`.
5. `pages/api/auth/logout.ts` (or a client‑side handler) that calls `supabase.auth.signOut()` and clears cookies, then redirects to `/login`.
6. Example protected page (e.g., `pages/dashboard.tsx`) that uses `getServerSideProps` to redirect if no session, else displays user email.
7. Updates to `next.config.js` if needed (none).
8. Updated `package.json` (ensure `@supabase/supabase-js` is installed; if not, add it).
9. Documentation updates in `LOCAL_SETUP.md` for setting `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

## Acceptance Criteria
- [ ] Visiting a protected page (e.g., `/dashboard`) while unauthenticated redirects to `/login`.
- [ ] After submitting valid credentials on `/login`, the user is redirected to the intended protected page (or a default landing page).
- [ ] Invalid credentials show a generic error (`"Invalid email or password"`).
- [ ] Clicking Google/GitHub buttons initiates the OAuth flow and, upon successful authentication, logs the user in.
- [ ] Logging out clears the session and redirects to `/login`.
- [ ] Accessing `/login` or `/register` while already authenticated redirects to the default protected page (optional but nice).
- [ ] The frontend works together with the backend: a request to `/api/v1/auth/me` (or any protected endpoint) with the cookie/bearer token succeeds.
- [ ] No authentication state leaks into the browser DevTools as plain text tokens (cookies are httpOnly).

## Estimated Effort
4‑6 hours (setup of client, middleware, login/logout pages, basic protected page, documentation).

## Dependencies
- Phase 0 (Next.js 15+ bootstrapped, TypeScript, Tailwind).
- 002A‑supabase‑auth.md (Supabase configured with providers and JWT).
- 002B‑backend‑auth.md (backend expects the same cookie/header strategy; frontend supplies cookie).

---