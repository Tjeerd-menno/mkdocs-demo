# Implementation Plan: MkDocs Internal Product Documentation Site

**Branch**: `001-mkdocs-docs-site` | **Date**: 2026-02-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-mkdocs-docs-site/spec.md`

## Summary

Build a self-contained internal documentation site using MkDocs Material (Python) with versioned publishing via `mike`. Stoplight Elements web-component is vendored from npm (`@stoplight/elements@9.0.15`) and renders OpenAPI 3.x YAML committed alongside documentation. The site is deployed to Azure Static Web Apps, protected by Microsoft Entra ID at the platform level (no auth code in the site). GitHub Actions drives CI gating on pull requests and automated deploy on `main` push and `v*.*.*` tags.

## Technical Context

**Language/Version**: Python 3.12 (MkDocs toolchain) + Node 20 (lint/validation toolchain)
**Primary Dependencies**:
- `mkdocs-material` 9.x — theme + search + navigation features
- `mike` 2.x — versioned deployment management to Azure SWA / gh-pages
- `markdownlint-cli2` — Markdown quality gate (Node)
- `@quobix/vacuum` — OpenAPI 3.x schema validation (Node; fast, no cloud dependency; npm: `@quobix/vacuum`)
- `@stoplight/elements` 9.0.15 — API reference web component (vendored, not CDN)
- `azure/static-web-apps-deploy@v1` — GitHub Actions deploy action
- `gitleaks` — pre-commit secret scanning

**Storage**: Static files only; `mike` manages a `gh-pages` branch (or equivalent Azure SWA deployment artifact). Git history is the audit trail.

**Testing**: No unit test framework. Quality is enforced by:
1. `markdownlint-cli2 "docs/**/*.md"` — zero errors
2. `mkdocs build --strict` — zero warnings
3. `mkdocs-linkcheck` on built `site/` — zero broken internal links
4. `vacuum lint docs/reference/openapi/*.yaml` — valid OpenAPI 3.x
5. Post-deploy smoke script (bash) — HTTP checks on live URLs

**Target Platform**: Azure Static Web Apps (Standard tier recommended; supports custom auth). Ubuntu latest (GitHub Actions runners for CI/CD).

**Project Type**: Documentation-only static site (no application backend, no database).

**Performance Goals**:
- Markdown pages: < 3 s load (corporate wired, ≤ 5 concurrent users)
- API Reference page (Elements): < 8 s full render
- CI build + deploy: < 10 min from tag push to version visible in selector

**Constraints**:
- No runtime CDN dependencies (all assets vendored or built-in to host)
- No secrets in committed files or published artifacts
- `mkdocs build --strict` must pass (zero warnings)
- Entra ID auth is platform-enforced; site has zero auth code
- Audience ≤ 5 concurrent users; no scaling, no SLA commitment

**Scale/Scope**: ~10–50 Markdown pages per version; 1 OpenAPI YAML (single service); ≤ 10 published versions over the lifetime of the project.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

### Pre-Research Gate

| Principle | Check | Result |
|-----------|-------|--------|
| I. Markdown & Content Quality | All content in `.md` files; markdownlint enforced in CI; no placeholder text policy | ✅ PASS |
| II. Test Before Publish | CI gates: markdownlint, strict build, link check, OAS validation, secret scan, smoke test | ✅ PASS |
| III. UX Consistency | Nav hierarchy fixed in spec (FR-006); heading rules (FR-007); relative links (FR-008) | ✅ PASS |
| IV. Technical Doc Completeness | OpenAPI coverage requirements in FR-013; "Why before How" in constitutionSpec; release notes categories in spec | ✅ PASS |
| V. Versioning Discipline | mike + tag convention defined; `latest` = most recent tag; immutable snapshots | ✅ PASS |

**Gate result**: ✅ All principles satisfied. Proceeding to Phase 0 research.

### Post-Design Re-Check (Phase 1)

| Principle | Design Decision | Result |
|-----------|----------------|--------|
| I. Content Quality | `.markdownlint.json` defined in contracts; frontmatter schema defined in data-model | ✅ PASS |
| II. Test Before Publish | CI workflow contracts define all 5 blocking gates explicitly | ✅ PASS |
| III. UX Consistency | `mkdocs.yml` nav locked in contracts; Elements page uses Material layout shim | ✅ PASS |
| IV. Tech Doc Completeness | OpenAPI authoring guide in quickstart; coverage checklist in data-model | ✅ PASS |
| V. Versioning Discipline | `mike deploy` commands locked to `MAJOR.MINOR` identifier; patch-update logic documented | ✅ PASS |

**Post-design gate**: ✅ All principles satisfied.

## Project Structure

### Specification (this feature)

```text
specs/001-mkdocs-docs-site/
├── plan.md          ← this file
├── research.md      ← Phase 0 output
├── data-model.md    ← Phase 1 output
├── quickstart.md    ← Phase 1 output
├── contracts/       ← Phase 1 output
│   ├── mkdocs.yml.md
│   ├── markdownlint.json.md
│   ├── staticwebapp.config.json.md
│   ├── ci-gate.yml.md
│   └── ci-deploy.yml.md
└── checklists/
    └── requirements.md
```

### Repository Root (source code / deliverable)

```text
/                                     ← repository root
├── docs/
│   ├── index.md                      ← Home / Overview
│   ├── getting-started/
│   │   ├── index.md
│   │   ├── installation.md
│   │   └── quickstart.md
│   ├── concepts/
│   │   └── index.md
│   ├── how-to/
│   │   └── index.md
│   ├── reference/
│   │   ├── api.md                    ← Stoplight Elements host page
│   │   └── openapi/
│   │       └── openapi.yaml          ← committed OpenAPI 3.x spec
│   ├── release-notes/
│   │   └── index.md
│   └── assets/
│       ├── vendor/
│       │   ├── web-components.min.js ← @stoplight/elements 9.0.15
│       │   ├── styles.min.css        ← @stoplight/elements 9.0.15
│       │   └── VENDOR-VERSIONS.md   ← inventory of vendored assets + versions
│       └── stylesheets/
│           └── extra.css             ← minimal theme shim for Elements
├── hooks/
│   ├── validate_openapi.py           ← MkDocs hook: fail build if openapi.yaml absent
│   └── validate_frontmatter.py       ← MkDocs hook: reject undocumented frontmatter keys
├── scripts/
│   └── smoke-test.sh                 ← post-deploy smoke test
├── staticwebapp.config.json          ← Azure SWA auth + routing config
├── mkdocs.yml
├── .markdownlint.json
├── .pre-commit-config.yaml           ← gitleaks pre-commit hook (FR-021)
├── requirements.txt                  ← pinned Python deps
├── package.json                      ← pinned Node deps
├── package-lock.json
└── .github/
    └── workflows/
        ├── docs-ci.yml               ← PR gate (no deploy)
        └── docs-deploy.yml           ← deploy on main push + v* tag
```

**Structure Decision**: Documentation-only project (no `src/`, no `tests/` directories). All source is under `docs/`; all tooling config at the repository root. Single-project layout.

## Complexity Tracking

> No constitution violations. No complexity justification required.

## Implementation Milestones

### M1 — Repository Bootstrap

**Goal**: Runnable local site with correct folder structure, dependency pinning, and passing `mkdocs build --strict`.

**Tasks**:
1. Create folder structure per Project Structure above (all directories + placeholder `index.md` files).
2. Write `mkdocs.yml` per the contracts specification.
3. Write `requirements.txt` pinned: `mkdocs-material==9.5.x`, `mike==2.x.x`.
4. Write `package.json` + `package-lock.json` pinned: `markdownlint-cli2`, `@apideck-oss/vacuum`.
5. Write `.markdownlint.json` per the contracts specification.
6. Run `pip install -r requirements.txt` + `mkdocs build --strict` and confirm exit 0.
7. Run `npx markdownlint-cli2 "docs/**/*.md"` and confirm exit 0.

**Deliverables**: Passing `mkdocs build --strict`; passing markdownlint; site navigable locally via `mkdocs serve`.

**Validation**: Open `http://localhost:8000` — all nav sections present; Material theme renders; no browser console errors.

---

### M2 — Stoplight Elements Integration

**Goal**: API reference page renders the local `openapi.yaml` from vendored assets, with no external network requests.

**Tasks**:
1. Download `web-components.min.js` and `styles.min.css` from `@stoplight/elements@9.0.15` on unpkg and place in `docs/assets/vendor/`.
2. Write `docs/assets/vendor/VENDOR-VERSIONS.md` recording package name, version, and source URL for each file.
3. Add vendored assets to `extra_javascript` and `extra_css` in `mkdocs.yml`.
4. Write `docs/reference/api.md` using the `<elements-api>` web component (see contracts).
5. Write a minimal but valid `docs/reference/openapi/openapi.yaml` (OpenAPI 3.1, at least one path, one response).
6. Validate YAML: `npx vacuum lint docs/reference/openapi/openapi.yaml`.
7. Serve locally and verify:
   a. Elements sidebar loads all operations.
   b. DevTools Network tab shows zero requests to external domains (unpkg, CDN, fonts.googleapis.com, etc.).
8. Write `docs/assets/stylesheets/extra.css` with minimal shim (ensure Elements fills its container, no overflow).

**Deliverables**: `docs/reference/api.md` renders Elements; OAS validation passes; no CDN requests.

**Validation**: Browser DevTools → Network → filter by external hostnames returns no results when offline mode is applied to external domains.

---

### M3 — Versioning Setup

**Goal**: `mike` configured; first manual publish of `dev` and `1.0` versions works; version selector appears.

**Tasks**:
1. Confirm `mike` in `requirements.txt`; configure `extra.version.provider: mike` in `mkdocs.yml`.
2. Set `mkdocs.yml` `site_url` appropriately for Azure SWA (can be empty for now; set in deploy step).
3. Test local mike publish:
   ```bash
   mike deploy dev
   mike deploy --update-aliases 1.0 latest
   mike serve
   ```
   Verify version selector shows `1.0` (latest) and `dev` at `http://localhost:8000`.
   Note: `mike deploy dev` must NOT include `--update-aliases latest` — per FR-018, `latest` is updated only by tag pushes, not by `dev`/`main` publishes.
4. Confirm immutability: re-publish `1.0` updates the alias; does not create a duplicate entry.
5. Document the publish commands in `quickstart.md`.

**Deliverables**: Version selector functional; `versions.json` contains `1.0` and `dev`.

**Validation**: Switch between `dev` and `1.0` in selector; content matches the expected source state for each.

---

### M4 — Azure Static Web Apps Configuration

**Goal**: `staticwebapp.config.json` protects all routes with Entra ID; deploy action wired up with required secret.

**Tasks**:
1. Write `staticwebapp.config.json` per the contracts specification (all routes require `"authenticated"` role; 401 redirects to `/.auth/login/aad`).
2. **Tenant restriction** (recommended — do not skip): configure a custom Entra ID provider with an app registration to restrict access to your specific tenant. Add the `auth` block to `staticwebapp.config.json` per the contracts specification.
3. Create the Azure Static Web Apps resource in Azure and retrieve the deployment token.
4. Add deployment token as repository secret: `AZURE_STATIC_WEB_APPS_API_TOKEN`.
5. Note the Azure SWA hostname and set as `site_url` in the deploy workflow (not in `mkdocs.yml`).

**Deliverables**: `staticwebapp.config.json` committed; Azure SWA resource created; secret configured.

**Validation**: Manually trigger the deploy workflow and confirm the site is reachable only after Entra ID sign-in in a private browser window.

---

### M5 — GitHub Actions CI Pipeline

**Goal**: All quality gates run on every pull request; no deploy occurs from CI workflow.

**Tasks**:
1. Write `.github/workflows/docs-ci.yml` per the contracts specification. Gates (in order):
   - `gitleaks` secret scan (or `truffleHog` as fallback)
   - `markdownlint-cli2 "docs/**/*.md"`
   - `vacuum lint docs/reference/openapi/*.yaml`
   - `mkdocs build --strict`
   - Link check on built `site/` (using `lychee` or `mkdocs-linkcheck`)
2. Add branch protection rule on `main` requiring this workflow to pass.
3. Test gate by:
   - Introducing a deliberate markdownlint violation → confirm CI fails.
   - Introducing a broken internal link → confirm CI fails.
   - Introducing invalid OpenAPI YAML → confirm CI fails.
   - Then reverting each → confirm CI passes.

**Deliverables**: `.github/workflows/docs-ci.yml` committed; branch protection enabled; all 3 negative tests confirmed.

**Validation**: Open a PR with each type of violation described above and observe the CI failure. All gates must be independently verifiable.

---

### M6 — GitHub Actions Deploy Pipeline

**Goal**: Automated publishing on `main` push (→ `dev`) and `v*.*.*` tag push (→ `MAJOR.MINOR` + `latest`).

**Tasks**:
1. Write `.github/workflows/docs-deploy.yml` per the contracts specification:
   - On `main` push: `mike deploy --push --update-aliases dev`
   - On `v*.*.*` tag push: extract `MAJOR.MINOR`, run `mike deploy --push --update-aliases $VERSION latest`
   - Deploy Azure SWA via `azure/static-web-apps-deploy@v1`
2. Write `scripts/smoke-test.sh`:
   - GET `<base-url>/versions.json` → assert version string present in response body
   - GET `<base-url>/<version>/index.html` → assert HTTP 200
   - GET `<base-url>/<version>/reference/api/index.html` → assert HTTP 200
   - GET `<base-url>/<version>/reference/openapi/openapi.yaml` → assert HTTP 200
   - GET `<base-url>/<version>/assets/vendor/web-components.min.js` → assert HTTP 200
   - Any failure → exit 1
3. Wire `smoke-test.sh` as a deploy-workflow step after `azure/static-web-apps-deploy`.
4. Test end-to-end:
   - Push to `main` → confirm `dev` alias updated
   - Push `v1.0.0` tag → confirm `1.0` version appears; `latest` alias updated
   - Push `v1.0.1` tag → confirm `1.0` alias updated in place (not a new `1.0.1` entry)

**Deliverables**: `.github/workflows/docs-deploy.yml` + `scripts/smoke-test.sh` committed; end-to-end publish verified.

**Validation**: Three tag push tests described above all behave as expected. Smoke test exits 0 on successful deploy.

---

### M7 — First Canonical Release

**Goal**: First real-content release published, searchable, and validated by a reviewer using the acceptance-criteria checklist in the spec.

**Tasks**:
1. Author initial content scaffolding (Getting Started, Concepts index, first How-to guide, Release Notes index with `v1.0` entry in BREAKING/NEW/FIXED format).
2. Update `openapi.yaml` to represent the real API (or a representative subset).
3. Verify all 8 success criteria from `spec.md` are met:
   - SC-001: fresh clone → local preview in < 5 min
   - SC-002: page load < 3 s
   - SC-003: Elements render < 8 s
   - SC-004: tag push → version in selector within 10 min
   - SC-005: zero broken internal links
   - SC-006: 100% PRs gated
   - SC-007: zero CDN URLs in `site/`
   - SC-008: (post-launch metric; baseline must be measured before go-live)
4. Run the acceptance-criteria checklist from the engineering spec (all 19 items).
5. Tag `v1.0.0` and publish.

**Deliverables**: Live site accessible to internal users at Azure SWA URL with Entra ID protection; `v1.0.0` in version selector; all 19 AC items checked.

**Validation**: A reviewer (not the author) runs through all 19 acceptance criteria and signs off.

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Stoplight Elements fetches fonts/icons from external CDN at runtime | Medium | High (breaks air-gapped requirement) | Verify with DevTools Network immediately after M2. If external fetches detected, extract URLs from bundled CSS, download resources, and serve locally via `extra_css` / `extra_javascript` overrides. |
| Entra ID built-in provider allows any Microsoft account, not just internal tenant | High | High (security boundary) | Use custom Entra ID provider config with app registration (documented in M4 Task 2). Do not ship with the default provider. |
| `mike` conflicts with Azure SWA deployment model (mike expects a git-backed deploy target; SWA uses artifact upload) | Medium | Medium | `mike` writes versioned output to a local dir; the deploy action then uploads that dir. Use `mike --no-redirect --update-aliases` and set `output_location` to the mike output folder. If incompatible, switch to a simple `mkdocs build` per-version script that produces the same directory structure. |
| Large OpenAPI spec (> 1 MB) causes Elements to render slowly | Low | Low (internal, ≤ 5 users) | Guidance in quickstart: split spec by service boundary; remove verbose examples. No automated enforcement needed. |
| `markdownlint-cli2` or `vacuum` version drift between developer machines and CI | Medium | Low | Pinned in `package-lock.json`; CI and local both use `npm ci`. Never use `npm install` for these tools. |
