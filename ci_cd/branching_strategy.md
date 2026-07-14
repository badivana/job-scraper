# Branching Strategy

## Purpose

To define the branching model and workflow for managing code changes in the Git repository, ensuring a clear, repeatable process for feature development, bug fixes, and releases that integrates smoothly with CI/CD.

## Contents

- Overview
- Protected Branches
- Feature Branches
- Hotfix Branches
- Release Branches (optional)
- Pull Request Workflow
- Tagging and Releases
- Summary

## Overview

We employ a **trunk‑based development** approach with short‑lived feature branches. The `main` branch represents the current production‑ready state. All changes are integrated into `main` via pull requests (PRs) that must pass automated checks before merging. This strategy enables continuous integration and frequent deployments while keeping the codebase stable.

## Protected Branches

- **`main`**: The default branch. Direct pushes are prohibited. All changes must be submitted via a pull request that passes required status checks (build, tests, security scans) and receives at least one approval.
- **`dev`** (optional): If used as an integration staging branch, it is also protected and updated from `main` after a release or via scheduled merges. Feature branches may target `dev` for pre‑release testing, but ultimately changes flow to `main`.

## Feature Branches

- Naming: `feature/<short-description>` (e.g., `feature/add-social-login`).
- Created from the latest `main`.
- Should be short‑lived (ideally a few days) and focused on a single feature or bug fix.
- Developers push commits regularly and open a draft PR early to obtain feedback.
- Before merging, the branch must be rebased onto the latest `main` (or updated via merge) to avoid conflicts.
- After approval and successful CI, the PR is merged using the **Squash and merge** option to keep a clean linear history.

## Hotfix Branches

- Used for critical bugs that must be fixed in production immediately.
- Naming: `hotfix/<description>` (e.g., `hotfix/fix-payment-timeout`).
- Branched from the latest `main` (or from a release tag if applicable).
- After fixing, the branch is merged into `main` (and optionally into `dev` if it exists) following the same PR process.
- A release tag is created immediately after merging (see Release Process).

## Release Branches (Optional)

If the project chooses to use release branches for stabilization before a release:
- Naming: `release/vX.Y.Z` (e.g., `release/v1.2.0`).
- Branched from `main` when a feature freeze is declared.
- Only bug‑fix commits are allowed on the release branch.
- Once testing passes, the branch is merged into `main` and tagged with the version number.
- The release branch may also be merged back into `dev` (if used) to keep it updated.

## Pull Request Workflow

1. **Create**: From your feature branch, open a PR against `base: main` (or `dev` if applicable).
2. **Template**: Fill in the PR template (summary, motivation, testing notes, screenshots if UI).
3. **Checks**: Automated triggers run:
   - Linting (ESLint, Ruff, Prettier)
   - Type checking (tsc, mypy)
   - Unit tests
   - Security scans (Bandit, Safety, npm audit, pip‑audit)
   - Build Docker images (optional)
4. **Review**: At least one approving review from a team member (code owner if applicable).
5. **Update**: Address reviewer feedback by pushing new commits to the same branch.
6. **Merge**: Once all checks pass and approvals are granted, merge the PR using **Squash and merge**.
7. **Delete**: The source branch is automatically deleted after merge (recommended).

## Tagging and Releases

- Releases are marked with **annotated tags** in the format `vMajor.Minor.Patch` (e.g., `v1.2.0`).
- Tags are created only on the `main` branch after a successful merge that includes the release changes.
- The CI pipeline detects new tags and initiates the release workflow (building and publishing Docker images, creating GitHub Release with notes).
- Release notes are generated from the merged PR titles (or manually edited in the GitHub Release draft).

## Summary

- Maintain a clean, linear history on `main` via squash merges.
- Keep feature branches short‑lived and branched from `main`.
- Enforce branch protections and required CI checks on `main`.
- Use PRs for all changes, ensuring code review and automated testing.
- Tag releases explicitly and automate release delivery.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*