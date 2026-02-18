# Tasks: MkDocs Internal Product Documentation Site

**Feature**: `001-mkdocs-docs-site` | **Generated**: 2026-02-18
**Input**: `specs/001-mkdocs-docs-site/` — plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

## Format: `[ID] [P?] [Story?] Description — file path`

- **[P]**: Parallelizable — different file from concurrent tasks, no dependency on an incomplete sibling task
- **[US#]**: User story this task implements
- **No test phases** — spec does not request TDD; quality is enforced by CI gates built into each phase

---

## Phase 1: Setup

**Purpose**: Repository scaffold — correct directory structure and placeholders so later tasks never create directories.

- [x] T001 Create full directory tree and placeholder `index.md` files per Project Structure in plan.md — `docs/`, `docs/getting-started/`, `docs/concepts/`, `docs/how-to/`, `docs/reference/`, `docs/reference/openapi/`, `docs/release-notes/`, `docs/assets/vendor/`, `docs/assets/stylesheets/`, `scripts/`, `.github/workflows/`
- [x] T002 [P] Write `.gitignore` — exclude `site/`, `__pycache__/`, `.venv/`, `node_modules/`, `.env` — `.gitignore`

**Checkpoint**: All directories exist; `git status` shows tracked placeholder files only.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Toolchain and configuration files that every user story depends on. Nothing works until this phase is complete.

**⚠️ CRITICAL**: No user story work can begin until Phase 2 is complete.

- [x] T003 Write `requirements.txt` with pinned deps: `mkdocs-material==9.5.*`, `mike==2.*` — `requirements.txt`
- [x] T004 [P] Write `package.json` and generate `package-lock.json` with pinned: `markdownlint-cli2`, `@quobix/vacuum` — `package.json`, `package-lock.json`
- [x] T005 [P] Write `.markdownlint.json` per contracts/markdownlint.json.md — MD013 (120 chars), MD024 siblings_only, MD033 allowlist includes `elements-api`, MD041, MD007 — `.markdownlint.json`
- [x] T006 [P] Write `mkdocs.yml` skeleton (site_name, theme: material, docs_dir, nav stubs) per contracts/mkdocs.yml.md — `mkdocs.yml`
- [x] T007 Run `pip install -r requirements.txt && npm ci && mkdocs build --strict` and `npx markdownlint-cli2 "docs/**/*.md"` — both must exit 0 before proceeding
- [x] T007a Write `scripts/smoke-test.sh` per contracts/ci-deploy.yml.md — 5 HTTP checks (versions.json, index.html, reference/api/index.html, openapi.yaml, web-components.min.js); any non-200 → exit 1; reads `DOCS_BASE_URL` env var; mark executable (`chmod +x`) — `scripts/smoke-test.sh` *(constitution Principle II: smoke test MUST be authored before content phases)*
- [x] T007b Write `.pre-commit-config.yaml` — configure `gitleaks` pre-commit hook for local secret scanning; add `pre-commit install` step to `docs/getting-started/installation.md` stub — `.pre-commit-config.yaml` *(satisfies FR-021: pre-commit hooks enforce secret scanning locally, not just in CI)*
- [x] T007c Write `hooks/validate_openapi.py` MkDocs hook — on build start, assert `docs/reference/openapi/openapi.yaml` exists; if absent, raise `SystemExit` with a clear error message; register under `hooks:` in `mkdocs.yml` — `hooks/validate_openapi.py` *(satisfies edge case: missing OpenAPI YAML must fail the build with a clear error)*
- [x] T007d Write `hooks/validate_frontmatter.py` MkDocs hook — on each page read, parse YAML frontmatter and assert all keys are in the permitted set (`title`, `description`, `hide`); fail the build if unknown keys are present; register under `hooks:` in `mkdocs.yml` — `hooks/validate_frontmatter.py` *(satisfies FR-003: undocumented frontmatter keys must be rejected by a lint step)*

**Checkpoint**: Foundation ready — `mkdocs build --strict` exits 0; markdownlint exits 0; `.pre-commit-config.yaml` installed locally; `scripts/smoke-test.sh` stub present.

---

## Phase 3: User Story 1 — Read Versioned Product Docs (Priority: P1) 🎯 MVP

**Goal**: A navigable, versioned static site with the correct IA hierarchy and a working `mike` version selector. An internal engineer can select a version, browse all nav sections, search content, and follow cross-references within the same version.

**Independent Test**: `mike serve` shows version selector with `1.0` and `dev`; all nav sections render; site search returns results; relative cross-reference links resolve without 404.

- [ ] T008 [US1] Expand `mkdocs.yml` with full nav hierarchy (Home → Getting Started → Concepts → How-to Guides → Reference → Release Notes), Material theme features (search, navigation.tabs, toc), and markdown extensions per contracts/mkdocs.yml.md — `mkdocs.yml`
- [ ] T009 [P] [US1] Write `docs/index.md` — H1 title, overview paragraph, links to Getting Started and Reference — `docs/index.md`
- [ ] T010 [P] [US1] Write `docs/getting-started/index.md` — section overview and navigation pointers — `docs/getting-started/index.md`
- [ ] T011 [P] [US1] Write `docs/concepts/index.md` — section overview explaining "Why before How" structure — `docs/concepts/index.md`
- [ ] T012 [P] [US1] Write `docs/how-to/index.md` — section overview, first how-to guide stub with relative cross-reference to Getting Started — `docs/how-to/index.md`
- [ ] T013 [P] [US1] Write `docs/release-notes/index.md` with `v1.0` entry using BREAKING / NEW / FIXED schema from data-model.md — `docs/release-notes/index.md`
- [ ] T014 [US1] Add `mike` versioning plugin to `mkdocs.yml`: `plugins: - mike`, `extra.version.provider: mike`, `extra.version.default: latest` — `mkdocs.yml`
- [ ] T015 [US1] Run local mike publish: `mike deploy dev` (no `--update-aliases latest` — dev must NOT set latest), then `mike deploy --update-aliases 1.0 latest`, then `mike serve` — verify version selector shows `1.0` (latest) and `dev` *(N1: aligns with FR-018: latest is updated only by tag pushes)*
- [ ] T016 [US1] Confirm immutability: republish `1.0` via `mike deploy 1.0` and verify `versions.json` has no duplicate `1.0` entries; document publish commands in `docs/getting-started/installation.md` stub

**Checkpoint**: `mike serve` renders version selector with `1.0` and `dev`; navigation, search, and relative cross-references all work.

---

## Phase 4: User Story 2 — Browse API Reference (Priority: P2)

**Goal**: The API Reference page renders the locally committed `openapi.yaml` via Stoplight Elements with zero CDN fetches. Engineers can browse operations, view schemas, and see examples — offline-capable.

**Independent Test**: Load `/reference/api/` locally with DevTools → Network → no requests to external hostnames (unpkg, fonts.googleapis.com, cdn.jsdelivr.net, etc.); Elements sidebar shows all operations from `openapi.yaml`; `vacuum` lint exits 0.

- [ ] T017 [US2] Download and vendor `@stoplight/elements@9.0.15` from unpkg: `web-components.min.js` (2.09 MB) and `styles.min.css` (298 kB) into `docs/assets/vendor/` — `docs/assets/vendor/web-components.min.js`, `docs/assets/vendor/styles.min.css`
- [ ] T018 [US2] Write `docs/assets/vendor/VENDOR-VERSIONS.md` recording package name `@stoplight/elements`, version `9.0.15`, source URL for each file, and download date — `docs/assets/vendor/VENDOR-VERSIONS.md`
- [ ] T019 [US2] Add vendored assets to `mkdocs.yml`: `extra_javascript: [assets/vendor/web-components.min.js]`, `extra_css: [assets/vendor/styles.min.css, assets/stylesheets/extra.css]` — `mkdocs.yml`
- [ ] T020 [P] [US2] Write `docs/reference/openapi/openapi.yaml` — valid OpenAPI 3.1.0, `info`, at least one path with GET, `200` and `4xx` responses with schemas, one parameter with example, no `x-internal: true` operations on the first path — `docs/reference/openapi/openapi.yaml`
- [ ] T021 [US2] Validate OpenAPI spec: `npx vacuum lint docs/reference/openapi/openapi.yaml` — must exit 0 — fix any violations before proceeding
- [ ] T022 [US2] Write `docs/reference/api.md` with `<elements-api>` web component: `apiDescriptionUrl="../openapi/openapi.yaml"`, `hideInternal="true"`, `tryItCredentialsPolicy="omit"`, `router="hash"` — `docs/reference/api.md`
- [ ] T023 [US2] Add API page to `mkdocs.yml` Reference nav section: `Reference: [api.md, openapi/openapi.yaml]` — `mkdocs.yml`
- [ ] T024 [P] [US2] Write `docs/assets/stylesheets/extra.css` — minimal shim ensuring `elements-api` fills its container, no overflow, consistent with Material theme colours — `docs/assets/stylesheets/extra.css`
- [ ] T025 [US2] Verify offline rendering: serve site locally, open API Reference page, apply DevTools Network throttle to block external domains — confirm Elements renders fully with zero external requests; document verification result in `docs/assets/vendor/VENDOR-VERSIONS.md`

**Checkpoint**: `vacuum` exits 0; API Reference page renders all operations; DevTools Network shows zero external CDN requests.

---

## Phase 5: User Story 3 — Local Developer Preview (Priority: P2)

**Goal**: A documentation author can go from `git clone` to a local preview in < 5 minutes. Live reload works. Broken links are caught locally before CI. The API Reference renders locally with no CDN traffic.

**Independent Test**: Fresh `git clone` → follow `docs/getting-started/installation.md` → `mkdocs serve` accessible at `http://localhost:8000` within 30 s; edit a `.md` file → browser auto-refreshes; `mkdocs build --strict` with a deliberate broken link exits non-zero.

- [ ] T026 [US3] Write `docs/getting-started/installation.md` — full developer setup guide covering: Python 3.12, Node 20, `pip install -r requirements.txt`, `npm ci`, `mkdocs serve`, pre-commit check commands — `docs/getting-started/installation.md`
- [ ] T027 [US3] Write `docs/getting-started/quickstart.md` — authoring guide: frontmatter rules, heading rules, relative links only, no placeholder text, OpenAPI YAML authoring, vendored asset update procedure, publish commands, and **gitleaks pre-commit hook failure UX**: when gitleaks fires locally, the terminal shows `WARN[YYYY-MM-DDTHH:MM:SS] leaks found: N`; to resolve, remove or vault the secret, then retry `git commit`; if the detection is a false positive, document the suppression with `# gitleaks:allow` inline comment — `docs/getting-started/quickstart.md`
- [ ] T028 [US3] Verify live reload: run `mkdocs serve`, edit `docs/index.md`, confirm browser refreshes without manual restart — note any issues in installation.md
- [ ] T029 [US3] Verify broken-link detection: add a deliberate broken internal link to `docs/index.md`, run `mkdocs build --strict` — confirm non-zero exit; revert the file; confirm `mkdocs build --strict` exits 0

**Checkpoint**: `docs/getting-started/installation.md` accurately describes a < 5-minute setup path; live reload and broken-link detection both verified.

---

## Phase 6: User Story 4 — CI/CD Publish on Release Tag (Priority: P3)

**Goal**: Pushing a `v1.2.0` tag automatically publishes an immutable `1.2` snapshot and updates the `latest` alias — no manual steps. All quality gates block bad PRs. Azure SWA enforces Entra ID before serving any content.

**Independent Test**: Push test `v0.9.0` tag to staging → `0.9` appears in `versions.json` and the live site; push `v0.9.1` → `0.9` entry updates in place; push to main → only `dev` updates; gate violations each block CI independently.

- [ ] T030 [P] [US4] Write `staticwebapp.config.json` per contracts/staticwebapp.config.json.md — all `/*` routes require `authenticated` role; 401 redirects to `/.auth/login/aad`; custom `azureActiveDirectory` provider block with tenant restriction; `navigationFallback` to `index.html` — `staticwebapp.config.json`
- [ ] T031 [P] [US4] Write `.github/workflows/docs-ci.yml` per contracts/ci-gate.yml.md — 5 sequential gates: gitleaks → markdownlint → vacuum → mkdocs build --strict → lychee internal (blocking); lychee external (warning); concurrency: cancel-in-progress — `.github/workflows/docs-ci.yml`
- [ ] T032 [P] [US4] Write `.github/workflows/docs-deploy.yml` skeleton per contracts/ci-deploy.yml.md — triggers (`push` to `main`; `push` with `tags: v*.*.*`), version resolution from ref logic, `mike deploy --no-redirect --update-aliases`, `azure/static-web-apps-deploy@v1` with `skip_app_build: true`; **exclude smoke-test step** (added in T033) — `.github/workflows/docs-deploy.yml`
- [ ] T033 [P] [US4] Add the smoke-test step to `.github/workflows/docs-deploy.yml`: wire `scripts/smoke-test.sh` (authored in T007a) as a post-deploy job step; pass `DOCS_BASE_URL` repository variable as env var; confirm step runs after the SWA deploy action — `.github/workflows/docs-deploy.yml`
- [ ] T034 [US4] Create Azure Static Web Apps resource in Azure portal (Standard tier); retrieve the deployment token
- [ ] T035 [US4] Register Entra ID app in Azure AD with tenant restriction; add `clientId`, `clientSecret`, `tenantId` to `staticwebapp.config.json` auth block per contracts/staticwebapp.config.json.md app registration steps
- [ ] T036 [US4] Add `AZURE_STATIC_WEB_APPS_API_TOKEN` as GitHub Actions repository secret; add `DOCS_BASE_URL` (Azure SWA hostname) as GitHub Actions repository variable
- [ ] T037 [US4] Enable branch protection on `main`: require `docs-ci` workflow to pass; require at least 1 review; block force-push
- [ ] T038 [US4] Test CI gate — markdownlint: push branch with a line exceeding 120 chars in a `.md` file → confirm `markdownlint-cli2` step fails; revert → confirm CI passes
- [ ] T039 [US4] Test CI gate — broken link: push branch with a broken relative link in `docs/index.md` → confirm lychee step fails; revert → confirm CI passes
- [ ] T040 [US4] Test CI gate — invalid OpenAPI: push branch with a YAML syntax error in `openapi.yaml` → confirm vacuum step fails; revert → confirm CI passes
- [ ] T041 [US4] End-to-end deploy test — main push: push a commit to main → confirm `dev` alias updates in deployed site's version selector within 10 minutes
- [ ] T042 [US4] End-to-end deploy test — tag publish: push `v1.0.0` tag → confirm `1.0` version entry appears in version selector; `latest` alias points to `1.0`; smoke-test exits 0
- [ ] T043 [US4] End-to-end deploy test — patch update: push `v1.0.1` tag → confirm `1.0` alias updates in place; no `1.0.1` entry appears in selector; `1.1` (if published) is unchanged

**Checkpoint**: All 3 negative CI gate tests fail as expected; 3 end-to-end deploy tests behave as expected; Entra ID blocks anonymous access in a private browser window.

---

## Phase 7: Polish & First Release

**Purpose**: Real content, acceptance criteria sign-off, and the live `v1.0.0` release.

- [ ] T044 [P] Author final content for Getting Started section — replace all skeleton pages with complete, non-placeholder text; verify `markdownlint` passes — `docs/getting-started/`
- [ ] T045 [P] Update `docs/reference/openapi/openapi.yaml` to represent real API endpoints per FR-013 (all parameters, request/response schemas, at least one error response per path, x-internal flags where needed) — `docs/reference/openapi/openapi.yaml`
- [ ] T046 Verify all 8 success criteria from spec.md: SC-001 (< 5 min setup), SC-002 (< 3 s page load), SC-003 (< 8 s Elements render), SC-004 (< 10 min tag-to-visible), SC-005 (zero broken links), SC-006 (100% PRs gated), SC-007 (zero CDN URLs in `site/`), SC-008 (baseline metric logged for 3-month check)
- [ ] T047 Run acceptance criteria review against `specs/001-mkdocs-docs-site/spec.md` — verify all FR-001–FR-025, all 4 NFR sections, and all SC-001–SC-008 are met; have a reviewer (not the author) sign off; log any failures as tracked issues before tagging *(the 19-item checklist in `ai-docs/engineering-spec.md` predates clarification and is superseded by spec.md)*
- [ ] T048a Before tagging, document the current 3-month support question baseline (count from issue tracker / team Slack / email over the prior 3 months) in `docs/ops/support-baseline.md` — provides the reference measurement for SC-008’s 30% reduction target — `docs/ops/support-baseline.md`
- [ ] T048 Push `v1.0.0` tag — confirm `1.0` appears in version selector; `latest` points to `1.0`; smoke test exits 0; site accessible behind Entra ID sign-in in a private browser window

**Checkpoint**: All 19 AC items signed off; smoke test exits 0; `v1.0.0` live on Azure SWA.

---

## Task Summary

| Phase | Stories | Tasks | Parallel opportunities |
|-------|---------|-------|----------------------|
| Phase 1: Setup | — | T001–T002 | T002 |
| Phase 2: Foundational | — | T003–T007d | T004, T005, T006 |
| Phase 3: US1 (P1) | Read Versioned Docs | T008–T016 | T009, T010, T011, T012, T013 |
| Phase 4: US2 (P2) | Browse API Reference | T017–T025 | T020, T024 |
| Phase 5: US3 (P2) | Local Developer Preview | T026–T029 | — |
| Phase 6: US4 (P3) | CI/CD Publish | T030–T043 | T030, T031, T032, T033 |
| Phase 7: Polish | — | T044–T048a, T048 | T044, T045 |
| **Total** | | **53 tasks** | **12 parallel opportunities** |

---

## Dependencies

```
Phase 1 (Setup)
  └── Phase 2 (Foundational) — toolchain working, mkdocs build passes
        └── Phase 3 (US1 — P1) ← MVP MILESTONE
              └── Phase 4 (US2 — P2) — Elements needs site structure + mkdocs.yml from US1
                    └── Phase 5 (US3 — P2) — CDN verification needs vendored assets from US2
                          └── Phase 6 (US4 — P3) — CI/CD needs stable content + config from US1–US3
                                └── Phase 7 (Polish) — release needs passing CI/CD pipeline
```

Story independence notes:
- **US1** is the strict prerequisite for everything (creates site scaffold, `mkdocs.yml`, mike config).
- **US2** can be started independently of US3 (parallel content/assets vs. developer guide work), but US3 verification step T029 needs the vendored assets from US2 to confirm the offline CDN check.
- **US4** CI gate files T031 and T032 can be authored in parallel with US3 content tasks (T026–T027) — they are different files. T033 edits the same workflow file as T032 and must follow it.
- **Azure infra tasks** (T034–T036) can be done any time after T030 is ready; they are cloud-side steps with no local file dependencies.

---

## Parallel Execution Examples

### Phase 3 (US1) — parallel content sprint

```text
T009  docs/index.md
T010  docs/getting-started/index.md     ← all 5 can be written simultaneously
T011  docs/concepts/index.md
T012  docs/how-to/index.md
T013  docs/release-notes/index.md
```

### Phase 6 (US4) — parallel CI/config file authoring

```text
T030  staticwebapp.config.json
T031  .github/workflows/docs-ci.yml     ← T030, T031, T032 can be written simultaneously
T032  .github/workflows/docs-deploy.yml (skeleton; excludes smoke-test step)

T033  .github/workflows/docs-deploy.yml (add smoke-test step) ← follows T032
```

---

## Implementation Strategy

**MVP Scope** (suggested stopping point after Phase 3):
Ship US1 only — a working local site with versioned content and correct nav. Validates toolchain and content workflow before committing to Elements integration or CI/CD.

**Increment 2** — add Phase 4 (US2): unblocks API reference consumers; requires only vendoring work and a valid `openapi.yaml`.

**Increment 3** — add Phase 5 (US3): documentation quality; unlikely to surface issues if Phase 1–4 were done carefully, but formalises the authoring guide for future contributors.

**Full delivery** — Phase 6 (US4) + Phase 7: automates publishing and prepares the `v1.0.0` release.
