from pathlib import Path

files = [
    "README.md",
    "CLAUDE.md",

    "docs/PROJECT_BRIEF.md",
    "docs/PRODUCT_REQUIREMENTS.md",
    "docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md",
    "docs/HIGH_LEVEL_DESIGN.md",
    "docs/LOW_LEVEL_DESIGN.md",
    "docs/SYSTEM_ARCHITECTURE.md",
    "docs/DATABASE_DESIGN.md",
    "docs/API_SPEC.md",
    "docs/AI_ENGINE.md",
    "docs/SCRAPING_ENGINE.md",
    "docs/MATCHING_ENGINE.md",
    "docs/SECURITY.md",
    "docs/DEPLOYMENT.md",
    "docs/UI_UX_GUIDELINES.md",
    "docs/ROADMAP.md",
    "docs/CHANGELOG.md",
    "docs/TECH_STACK.md",
    "docs/CODING_STANDARDS.md",
    "docs/TESTING_STRATEGY.md",
    "docs/MONITORING_LOGGING.md",
    "docs/ENVIRONMENT_SETUP.md",
    "docs/RISK_REGISTER.md",
    "docs/PERFORMANCE_GUIDELINES.md",
    "docs/SCALABILITY_PLAN.md",

    "design/ER_DIAGRAM.md",
    "design/SEQUENCE_DIAGRAMS.md",
    "design/COMPONENT_DIAGRAM.md",
    "design/CLASS_DIAGRAM.md",
    "design/DATA_FLOW_DIAGRAM.md",
    "design/USER_FLOW.md",
    "design/WIREFRAMES.md",
    "design/DESIGN_TOKENS.md",
    "design/DATABASE_SCHEMA.md",
    "design/API_FLOW.md",
    "design/SCREEN_FLOW.md",
    "design/STATE_DIAGRAM.md",

    "prompts/backend.md",
    "prompts/frontend.md",
    "prompts/database.md",
    "prompts/ai.md",
    "prompts/scraping.md",
    "prompts/testing.md",
    "prompts/deployment.md",
    "prompts/review.md",
    "prompts/architecture.md",
    "prompts/security.md",
    "prompts/optimization.md",
    "prompts/refactoring.md",

    "tasks/phase1.md",
    "tasks/phase2.md",
    "tasks/phase3.md",
    "tasks/phase4.md",
    "tasks/phase5.md",
    "tasks/phase6.md",
    "tasks/phase7.md",
    "tasks/phase8.md",
    "tasks/phase9.md",
    "tasks/phase10.md",
    "tasks/bug_fixes.md",
    "tasks/production.md",

    "backend/README.md",
    "backend/ARCHITECTURE.md",

    "frontend/README.md",
    "frontend/ARCHITECTURE.md",

    "infrastructure/docker.md",
    "infrastructure/kubernetes.md",
    "infrastructure/terraform.md",

    "database/migration_plan.md",
    "database/seed_strategy.md",
    "database/backup_strategy.md",

    "ai/prompt_library.md",
    "ai/embedding_strategy.md",
    "ai/evaluation.md",

    "scraping/actors.md",
    "scraping/sources.md",
    "scraping/retry_strategy.md",

    "testing/unit_tests.md",
    "testing/integration_tests.md",
    "testing/e2e_tests.md",
    "testing/performance_tests.md",
    "testing/security_tests.md",

    "ci_cd/github_actions.md",
    "ci_cd/release_process.md",
    "ci_cd/branching_strategy.md",

    "assets/logo.md",
    "assets/branding.md",
    "assets/color_palette.md",
    "assets/typography.md",
    "assets/icons.md",

    "legal/privacy_policy.md",
    "legal/terms.md",
    "legal/cookies.md",
]

for file in files:
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(
f"""# {path.stem.replace('_',' ').title()}

## Purpose

TODO

---

## Contents

TODO
""",
encoding="utf-8")

print(f"Created {len(files)} files.")