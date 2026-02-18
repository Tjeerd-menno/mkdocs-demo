---
description: Development guidelines for the MkDocs internal documentation site (001-mkdocs-docs-site)
applyTo: "**"
---

# mkdocs-demo Development Guidelines

Auto-generated from feature plan `001-mkdocs-docs-site`. Last updated: 2026-02-18

## Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | MkDocs toolchain runtime |
| `mkdocs-material` | 9.x | Site theme + search + navigation |
| `mike` | 2.x | Versioned deployment (`MAJOR.MINOR` aliases) |
| Node.js | 20 LTS | Lint/validation toolchain runtime |
| `markdownlint-cli2` | pinned in package.json | Markdown quality gate |
| `@apideck-oss/vacuum` | pinned in package.json | OpenAPI 3.x schema validation |
| `@stoplight/elements` | 9.0.15 (vendored) | API reference web component |
| `gitleaks-action` | v2 | Secret scanning in CI |
| `lychee` | via lycheeverse/lychee-action | Link checking |
| `azure/static-web-apps-deploy` | v1 | Deployment to Azure Static Web Apps |

## Repository Structure

```text
/
├── docs/                          ← all Markdown content
│   ├── index.md
│   ├── getting-started/
│   ├── concepts/
│   ├── how-to/
│   ├── reference/
│   │   ├── api.md                 ← Stoplight Elements host page
│   │   └── openapi/openapi.yaml   ← committed OpenAPI 3.x spec
│   ├── release-notes/
│   └── assets/vendor/             ← vendored JS + CSS (no CDN at runtime)
├── scripts/smoke-test.sh
├── staticwebapp.config.json       ← Azure SWA auth (Entra ID)
├── mkdocs.yml
├── .markdownlint.json
├── requirements.txt               ← pinned Python deps
├── package.json                   ← pinned Node deps
└── .github/workflows/
    ├── docs-ci.yml                ← PR quality gates
    └── docs-deploy.yml            ← deploy on main push + v* tag
```

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt
npm ci

# Local preview
mkdocs serve

# Pre-commit checks (all must pass before PR)
npx markdownlint-cli2 "docs/**/*.md"
npx vacuum lint docs/reference/openapi/*.yaml
mkdocs build --strict
```

## Authoring Rules

- **Frontmatter**: Only `title`, `description`, `hide` keys permitted in any `.md` file.
- **Headings**: Exactly one H1 per page; never skip heading levels.
- **Links**: Always relative Markdown links for internal cross-references (no absolute URLs).
- **Custom HTML**: Only `<elements-api>` is permitted (on `reference/api.md` only).
- **No placeholders**: "TBD", "TODO", "Coming soon" are forbidden in merged content.
- **OpenAPI**: YAML only (not JSON); multiline descriptions use `|` block scalar.

## Versioning Rules

- `mike` publishes `MAJOR.MINOR` identifiers only (e.g., `1.2` for `v1.2.0` and `v1.2.1`).
- `latest` alias = most recently published stable tag (NOT main branch).
- `dev` alias = main branch HEAD (updated on every push to main).
- Once published, a numbered version snapshot is immutable.

## CI Quality Gates (all blocking)

1. `gitleaks` secret scan
2. `markdownlint-cli2 "docs/**/*.md"`
3. `vacuum lint docs/reference/openapi/*.yaml`
4. `mkdocs build --strict`
5. `lychee --offline` internal link check

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
