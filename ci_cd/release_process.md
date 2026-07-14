# Release Process

## Purpose

To define the steps and responsibilities for releasing a new version of the AI-Powered Job Finder application, ensuring a consistent, traceable, and reliable delivery of software to production environments.

## Contents

- Overview
- Release Types
- Preparation
- Versioning
- Changelog Generation
- Tagging
- Build and Push Artifacts
- Deployment
- Post‑Release Activities
- Rollback Procedure
- Communication

## Overview

We follow a **semantic versioning** scheme (MAJOR.MINOR.PATCH). Releases are triggered from the `main` branch after all changes have been merged and validated. The process can be manual (triggered via a GitHub Actions workflow dispatch) or automatic (e.g., on push to `main` with a version tag). This document outlines a manual release flow that provides explicit gates for quality assurance.

## Release Types

| Type | When to Use | Version Change | Example |
|------|-------------|----------------|---------|
| **Patch** | Bug fixes, small improvements, security patches | `Z` in `X.Y.Z` increments | 1.2.3 → 1.2.4 |
| **Minor** | New features that are backward‑compatible | `Y` increments | 1.2.3 → 1.3.0 |
| **Major** | Breaking changes, API incompatibilities, major architectural shifts | `X` increments | 1.2.3 → 2.0.0 |

## Preparation

1. **Ensure `main` is up‑to‑date**  
   Verify that the local `main` branch reflects the remote and that there are no uncommitted changes.
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Run full test suite locally (optional but recommended)**  
   ```bash
   pytest
   # or use the CI environment via workflow_dispatch
   ```

3. **Check for any failing or flaky tests** – resolve before proceeding.

4. **Review open pull requests** – ensure that all intended changes for this release are merged into `main`.

5. **Confirm that the `CHANGELOG.md` has been updated** for the upcoming release (see below).

## Versioning

Decide the version bump based on the changes included since the last release.

- Use semantic versioning guidelines.
- Update the version in the relevant places:
  - `pyproject.toml` or `setup.py`/`version.py` (if applicable).
  - `package.json` (if the frontend version should sync; optional).
  - Docker image tags will use the Git SHA, but the release tag itself is the version number.

For simplicity, we often keep the version only in `CHANGELOG.md` and rely on Git tags for release identification. If your build process reads a version file, update it accordingly.

## Changelog Generation

We keep a `CHANGELOG.md` at the repository root following the **Keep a Changelog** format.

1. Ensure that all changes since the last release are documented under an `Unreleased` section.
2. When preparing a release, copy the `Unreleased` section under a new heading with the version and release date (YYYY‑MM‑DD).
   Example:
   ```markdown
   ## [1.2.4] - 2026-07-20
   ### Added
   - New OAuth provider (GitHub).
   ### Changed
   - Improved matching algorithm latency.
   ### Fixed
   - Fixed resume upload timeout for large files.
   ```
3. Clear the `Unreleased` section (or move its contents to the new version block) and prepare a fresh `Unreleased` section for future changes.

## Tagging

1. Create an annotated GPG‑signed tag (recommended) or a lightweight tag.
   ```bash
   # Set your GPG key if needed
   git tag -a v1.2.4 -m "Release v1.2.4"
   # To sign:
   # git tag -s v1.2.4 -m "Release v1.2.4"
   ```
2. Push the tag to the remote:
   ```bash
   git push origin v1.2.4
   ```

## Build and Push Artifacts

The CI pipeline automatically responds to a new tag:

- The workflow triggered on `push` with tags `v*.*.*` will:
  1. Checkout the tagged commit.
  2. Run lint, type checks, and unit tests.
  3. Build Docker images for frontend, backend, and worker.
  3. Tag the images with the commit SHA and also with the version (e.g., `ghcr.io/org/frontend:v1.2.4`).
  4. Push the images to the container registry (GHCR or Docker Hub).
  5. Generate and upload the SBOM (Software Bill of Materials) if applicable.
  6. Create a GitHub Release with the tag name, using the content from `CHANGELOG.md` for the release notes.
  7. (Optional) Deploy to a staging environment for smoke test.
  8. (Optional) Notify the release channel (Slack, email) upon completion.

If you prefer a manual approach, you can trigger the workflow via ` workflow_dispatch` after pushing the tag.

## Deployment

By default, the release process does **not** automatically deploy to production. Instead:

1. **Staging Verification**  
   After the tag is pushed, a staging environment (if configured) is updated automatically (or manually) to the new images. Run smoke tests (health check, login, search, match) to validate the release.

2. **Production Promotion**  
   Once satisfied, promote the release to production:
   - **Kubernetes**: Update the image tags in the Deployment manifests (or use ArgoCD/Flux if GitOps).
   - **ECS/Fargate**: Update the task definition with the new image revision.
   - **Cloud Run**: Deploy the instance**: Deploy the new container version.
   - **Manual**: If using VMs, pull the new image and restart the service.

   The promotion can be done via a separate workflow (`deploy-production`) that requires manual approval or via a protected environment in GitHub Actions.

3. **Post‑Deploy Smoke Test**  
   Run a brief set of end‑to‑end checks against the production endpoint (e.g., using `curl` or a synthetic monitor) to confirm basic functionality.

## Post‑Release Activities

1. **Announce the Release**  
   - Post in the team’s Slack channel, mailing list, or release notes portal.
   - Include a summary of new features, bug fixes, and any breaking changes.
   - Provide links to the GitHub Release page and the updated documentation.

2. **Update Documentation**  
   - Ensure that the online documentation (e.g., hosted on GitHub Pages or a separate site) reflects any changes.
   - Version‑specific documentation can be kept in branches like `docs/v1.2` if needed.

3. **Monitor Metrics**  
   - Watch key performance indicators (request latency, error rates, queue lengths) for any anomalies.
   - Check business metrics (active users, match rates, email delivery rates) if available.

4. **Log the Release**  
   - Record the release in an internal release tracker or wiki, noting the date, version, SHA, and any incidents.

## Rollback Procedure

If a critical issue is discovered after deployment:

1. **Identify the Problem**  
   Determine whether the issue is due to the new release, infrastructure, or external dependencies.

2. **Attempt Mitigation**  
   - Feature flag: disable the problematic functionality if possible.
   - Hotfix: apply a quick workaround (e.g., restart service, scale resources).

3. **Rollback to Previous Version**  
   - If the issue cannot be mitigated and is caused by the new release:
     - **Kubernetes**: Roll out the previous Deployment revision (`kubectl rollout undo deployment/<name>`) or manually set the image tag back to the previous version.
     - **ECS**: Update the service to use the previous task definition revision.
     - **Other**: Redeploy the previously known good container version.

   Ensure that database migrations are forward‑only; rolling back the code does not downgrade the schema. If a migration introduced a breaking change that requires data migration, a rollback may need to restore the database from a backup taken before the upgrade.

4. **Communicate**  
   Inform stakeholders of the rollback, the reason, and the expected time to recovery.

5. **Investigate and Patch**  
   After stabilizing, create a patch release (incrementing the Z version) that addresses the root cause.

## Communication

- **Internal**: Use the team’s Slack channel, email distribution list, or project management tool to announce the start of a release, deployment windows, and post‑release summaries.
- **External (if applicable)**: Update public status pages, send release notes to customers, or publish a blog post for major releases.
- **Incidents**: If the release leads to an incident, follow the incident response protocol (see `docs/INCIDENT_RESPONSE.md` if exists).

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*