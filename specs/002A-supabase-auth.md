# 002A-supabase-auth.md

## Objective
Configure Supabase Auth for the AI‑Powered Job Finder: enable email/password, Google, GitHub providers; set JWT parameters; customize email templates; set redirect URLs.

## Scope
- Enable authentication providers in Supabase dashboard.
- Configure JWT settings (expiration, audience, refresh token rotation).
- Customize email templates (confirmation, password reset, magic link) with branding.
- Set redirect URLs for OAuth callbacks and email verification links.
- Document required environment variables (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, etc.) for local development.

## Deliverables
1. Supabase project with Email/Password, Google, GitHub providers enabled.
2. JWT configuration: access token TTL 900 s, audience `authenticated`, refresh token rotation enabled.
3. Updated email templates (subject lines, body placeholders) matching product branding.
4. Redirect URLs configured (e.g., `http://localhost:3000/auth/callback` for dev; production URL for prod).
5. Updated `.env.example` and `LOCAL_SETUP.md` with instructions for developers to obtain and set these values.
6. No code changes required – configuration only via Supabase dashboard.

## Acceptance Criteria
- [ ] A new user can sign up via email/password and receives a confirmation email.
- [ ] The confirmation link redirects to the configured URL and verifies the email.
- [ ] Users can sign in with Google and GitHub accounts (OAuth flow).
- [ ] JWTs issued by Supabase have the expected claims (`sub`, `email`, `aud="authenticated"`, `exp`).
- [ ] The Supabase service role key is available as a secret for backend use.

## Estimated Effort
2‑4 hours (configuration via Supabase UI + documentation updates).

## Dependencies
- Phase 0 completed (Supabase project created, `.env.example` exists).

---