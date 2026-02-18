# Feature Specification: MkDocs Internal Product Documentation Site

**Feature Branch**: `001-mkdocs-docs-site`
**Created**: 2026-02-18
**Status**: Ready for Implementation
**Input**: Internal documentation site using MkDocs Material with Stoplight Elements for OpenAPI reference, versioned by Git tags and deployed to Azure Static Web Apps protected by Entra ID.

## Overview

Build an internal documentation site that serves as the single destination for internal engineers, QA teams, service engineers, and product owners to read versioned product documentation and modern API reference pages. The site is Markdown-first, versioned per product release tag, and self-contained — no runtime dependencies on public CDNs.

## Clarifications

### Session 2026-02-18

- Q: Should `latest` alias point to the most recent stable tag or to `main` HEAD? → A: Option A — `latest` = most recently published stable tag; `main` publishes as `dev` alias.
- Q: What is the hosting target? → A: Azure Static Web Apps with Entra ID protection (replaces GitHub Pages assumption).
- Q: What is the expected concurrent user load? → A: At most 5 concurrent users — this is a small internal engineering audience; no horizontal scaling, SLA, or formal availability target required.
- Q: What observability is required? → A: GitHub Actions CI logs only; no dedicated monitoring, alerting, or distributed tracing required.
- Q: What is the cross-version search scope? → A: Single-version scope (MkDocs built-in default); no cross-version search required.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Read Versioned Product Docs (Priority: P1)

An internal engineer navigating to the docs site selects a specific released version (e.g., `1.2`) from the version selector and reads product documentation — concepts, how-to guides, getting started material — for that version. They can navigate the full site hierarchy, use site search, and follow cross-references within the same version.

**Why this priority**: This is the foundational value proposition of the site. Without reliable, versioned, navigable documentation the site has no purpose. All other stories build on this working baseline.

**Independent Test**: A deployed site with content under `docs/` and at least one published version can be fully tested by browsing the site, using the version selector, and searching. Delivers usable documentation independently of the API reference story.

**Acceptance Scenarios**:

1. **Given** the site has been deployed with version `1.2` via a `v1.2.0` tag, **When** a user opens the version selector, **Then** `1.2` and `latest` (pointing to `1.2`) are listed; `dev` also appears if a `main` push has occurred.
2. **Given** the user selected version `1.2`, **When** they navigate the left sidebar and click any page, **Then** they remain within the `1.2` version and the URL includes the version prefix.
3. **Given** a user types a search query, **When** the query matches content in the current version, **Then** matching results appear immediately in the search panel without a full page reload.
4. **Given** a page contains a cross-reference link, **When** the user clicks it, **Then** the destination page loads within the same version (no version hop, no 404).
5. **Given** an older published version (e.g., `1.1`) exists, **When** the user switches to it, **Then** all pages reflect the content that was current at that release — not content from a later version.

---

### User Story 2 — Browse API Reference (Priority: P2)

An internal engineer opens the API Reference page for the currently selected product version and reads endpoint documentation rendered from the OpenAPI YAML committed at that version. They can browse operations in the sidebar, read request/response schemas, and view examples — without needing to open any external tool.

**Why this priority**: API reference is the highest-value reference content for engineering and QA consumers. Without embedded OpenAPI rendering, they must read raw YAML or use a separate external tool, increasing friction. Depends on US1 (site infrastructure) being in place.

**Independent Test**: Can be tested by deploying a site with a valid `openapi.yaml` file and verifying the Elements component renders the spec on the API reference page. Can be tested on `latest` only before versioning is in place.

**Acceptance Scenarios**:

1. **Given** the user navigates to the Reference → API Reference page, **When** the page loads, **Then** the Stoplight Elements sidebar renders all operations from the committed `openapi.yaml` within 8 seconds on a corporate network.
2. **Given** the page has loaded, **When** the user clicks an operation in the Elements sidebar, **Then** the operation detail panel (path, parameters, request body, response schemas, examples) is displayed.
3. **Given** the current version is `1.2`, **When** the user views the API Reference page, **Then** the Elements component references the OpenAPI spec committed at the `1.2` snapshot — not the spec from another version.
4. **Given** the site has no internet access from the browser (simulate with DevTools offline for external domains), **When** the user loads the API Reference page, **Then** the Elements component still renders fully (all JS, CSS, and fonts served from the site itself).
5. **Given** an OpenAPI operation is marked `x-internal: true`, **When** the page renders, **Then** that operation does not appear in the Elements sidebar.

---

### User Story 3 — Local Developer Preview (Priority: P2)

A documentation author makes changes to Markdown pages or the OpenAPI YAML and previews the result locally with a single command before opening a pull request.

**Why this priority**: Fast, friction-free local feedback is essential for authors to self-review quality. Without local preview, authors rely solely on CI, slowing iteration. For the static site rendering portion, US2 is not a hard dependency — authoring guide content and live reload can be delivered independently. However, the full independent test (confirming the API reference renders completely offline) requires the US2 vendored assets to be in place first.

**Independent Test**: Tested by running the prescribed local command on a fresh checkout and verifying the site and API reference page render correctly in a browser without any network access to external CDNs.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repository and installed the documented dependencies, **When** they run the prescribed local-preview command, **Then** the site is accessible in a browser at `http://localhost:8000` within 30 seconds.
2. **Given** the local site is running, **When** the developer edits a Markdown file and saves it, **Then** the browser reflects the change without requiring a manual restart.
3. **Given** the local site is running, **When** the developer navigates to the API Reference page, **Then** the Stoplight Elements component renders the local `openapi.yaml` — no external network requests occur.
4. **Given** a developer introduces a broken internal link, **When** they run the prescribed build command locally, **Then** the build reports the broken link and exits non-zero.

---

### User Story 4 — CI/CD Publish on Release Tag (Priority: P3)

When a product release tag (`v1.2.0`) is pushed, CI builds the documentation site and publishes an immutable versioned snapshot (`1.2`) to the deployment target. The `latest` alias updates to point to the new version. No manual steps are required.

**Why this priority**: Automated publishing is what turns the docs site from a manual chore into a reliable companion to each product release. Depends on US1 and US3 being stable.

**Independent Test**: Tested by pushing a test tag to a staging branch and verifying the deployment target receives a new version entry in `versions.json` and the snapshot is accessible.

**Acceptance Scenarios**:

1. **Given** no human action beyond pushing a `v1.2.0` tag, **When** CI completes, **Then** the `1.2` version is listed in the deployed site's version selector.
2. **Given** the `v1.2.0` tag has been published, **When** any subsequent `v1.2.x` patch tag is published, **Then** the `1.2` snapshot is updated in place (same version selector entry) without creating a separate patch entry.
3. **Given** a merge to `main` occurs (not a tag), **When** CI completes, **Then** only the `dev` alias updates; `latest` remains pointing to the most recent stable tag; no new numbered version entry is created.
4. **Given** the post-deploy smoke test runs, **When** it detects a required page or asset returns a non-200 status, **Then** the CI job exits non-zero and the team is notified.
5. **Given** a previously published version (e.g., `1.1`) exists, **When** version `1.2` is published, **Then** `1.1` snapshot is unchanged and still accessible.

---

### Edge Cases

- **Empty or missing OpenAPI YAML**: If `docs/reference/openapi/openapi.yaml` is absent at build time, the build MUST fail with a clear error rather than deploying a broken API reference page.
- **Invalid OpenAPI YAML**: If the YAML does not pass schema validation, CI MUST block the merge/publish — the Elements component renders nothing useful for an invalid spec.
- **Very large OpenAPI spec**: A spec exceeding 2 MB causes Elements to slow perceptibly; authors are responsible for keeping specs lean (split by service or prune over-specified examples).
- **Version selector on first deployment**: When only `dev`/`latest` exists and no tagged version has been published, the selector shows a single entry — site must not error; users see the lone entry.
- **Patch release updating immutable snapshot**: The `1.2` alias is updated when `v1.2.1` is published. Users reading `1.2` docs after the patch update see the corrected content. This is by design and is documented in the release notes.
- **User navigates to a non-existent version URL directly**: With the `navigationFallback` set to `rewrite: /index.html` in `staticwebapp.config.json`, Azure Static Web Apps rewrites unknown version paths to the root `index.html`. The root `index.html` generated by `mike` redirects the user to the `latest` alias. The site MUST NOT expose a blank page or framework error; this behaviour is enforced by the committed `staticwebapp.config.json` configuration.

---

## Requirements *(mandatory)*

### Functional Requirements

**Content & Authoring**

- **FR-001**: The site MUST be authored exclusively in Markdown files under `docs/`. No templating languages or JSX are used in content files.
- **FR-002**: Every Markdown file MUST pass `markdownlint` with the project ruleset before merging.
- **FR-003**: Frontmatter keys MUST be restricted to the set defined in the authoring guide; undocumented keys MUST be rejected by a lint step.
- **FR-004**: Published pages MUST NOT contain placeholder text ("TBD", "TODO", "Coming soon").
- **FR-005**: Embedded code samples MUST be syntactically valid. They SHOULD be sourced from CI-verified snippets where the sample can be executed in CI without a full product build; otherwise, correctness is verified by the reviewer sign-off process.

**Navigation & Structure**

- **FR-006**: The top-level navigation MUST follow the hierarchy: Home → Getting Started → Concepts → How-To Guides → Reference → Release Notes.
- **FR-007**: Each page MUST have exactly one H1 heading. Heading levels MUST NOT be skipped.
- **FR-008**: Cross-references between pages MUST use relative Markdown links; absolute internal URLs are forbidden.

**API Reference**

- **FR-009**: An API reference page MUST render the committed OpenAPI 3.x YAML using the Stoplight Elements web component.
- **FR-010**: The OpenAPI YAML file MUST reside at `docs/reference/openapi/openapi.yaml` (single service) or `docs/reference/openapi/<service>.yaml` (multi-service).
- **FR-011**: The Elements component MUST be configured in read-only mode: interactive "Try It" credential forwarding MUST be disabled.
- **FR-012**: Operations marked `x-internal: true` in the OpenAPI spec MUST NOT appear in the rendered reference.
- **FR-013**: Every OpenAPI endpoint MUST document: purpose, all parameters (path/query/header) with types and examples, at least one request body example (where applicable), all response codes with schemas, and at least one error response schema.

**Versioning**

- **FR-014**: Docs versions MUST be managed by `mike` and correspond 1:1 to product Git tags (`v<MAJOR>.<MINOR>.<PATCH>`).
- **FR-015**: Published version identifiers in the version selector MUST use `<MAJOR>.<MINOR>` format only.
- **FR-016**: Patch releases (`v1.2.1`, `v1.2.2`, …) MUST update the `1.2` alias in place; they MUST NOT create a separate `1.2.1` selector entry.
- **FR-017**: Once a versioned snapshot is published, its content MUST be immutable; corrections require a new patch release.
- **FR-018**: The `dev` alias MUST be published on every push to `main`. The `latest` alias MUST point to the most recently published stable tagged release (e.g., `1.2`). `latest` MUST NOT be updated by a `main` branch push — only by a `v*.*.*` tag push. Patch tag pushes (`v1.2.1`, `v1.2.2`, …) update the `1.2` snapshot in place and update `latest` only if `1.2` is already the `latest` version (i.e., no newer MAJOR.MINOR has been published). Assumption: patch releases are published only for the most recent stable MAJOR.MINOR; out-of-order patch releases for older versions are not supported and would require a manual `mike` alias correction.

**Assets & Security**

- **FR-019**: All JavaScript and CSS required by Stoplight Elements MUST be vendored under `docs/assets/vendor/`. No runtime CDN fetches are permitted.
- **FR-020**: No secrets, credentials, internal hostnames, or tokens MUST appear in any committed file.
- **FR-021**: Pre-commit hooks MUST enforce secret scanning.

**Build & CI**

- **FR-022**: `mkdocs build --strict` MUST succeed with zero warnings on every merge to `main`.
- **FR-023**: OpenAPI YAML MUST pass schema validation on every pull request.
- **FR-024**: Internal links MUST be checked for integrity on every pull request; broken internal links MUST block merge.
- **FR-025**: A post-deploy smoke test MUST verify version visibility, page availability, and asset accessibility after every deployment.

### Key Entities

- **Documentation Page**: A Markdown file under `docs/` representing a single topic. Belongs to exactly one nav section. Has a single H1 title.
- **OpenAPI Specification**: A YAML file at the prescribed path representing the API contract for one service at a given version. Validated in CI. Rendered by Stoplight Elements.
- **Site Version**: A named, immutable snapshot of all docs and the OpenAPI spec, identified by `<MAJOR>.<MINOR>`. Published by `mike` to the deployment target.
- **Version Alias**: A mutable pointer (`latest`, `dev`) managed by `mike` that redirects users to a specific version snapshot.
- **Vendored Asset**: A JavaScript or CSS file copied from a fixed npm package release into `docs/assets/vendor/` and committed. Updated intentionally, not automatically.

---

## Non-Functional Requirements

### Availability & Reliability
- The site serves at most 5 concurrent internal users; no formal uptime SLA or availability target is required.
- Best-effort availability: if the Azure Static Web Apps deployment is unavailable, the impact is low. No automated failover is required.
- Builds MUST be reproducible: the same source commit MUST always produce identical output.

### Performance
- Page load targets apply on a corporate wired network with ≤5 concurrent users (no CDN acceleration needed).
- Individual Markdown pages MUST load in under 3 seconds (relaxed from a public-site target given the small audience and internal network).
- The API Reference page (Stoplight Elements) MUST fully render within 8 seconds (Elements has a heavier initial paint; acceptable for an internal read-only reference).

### Observability
- GitHub Actions CI logs are the sole observability mechanism required. No application-level logging, metrics dashboards, or alerting pipelines are needed.
- Post-deploy smoke test failures surface via GitHub Actions job failure notifications (standard GitHub notification channel).

### Security
- Authentication and authorisation are fully handled by **Azure Static Web Apps with Entra ID** (Microsoft Entra ID route-level protection). The docs site itself contains no auth code, login pages, or tokens.
- All traffic to the site MUST be gated by Entra ID sign-in; unauthenticated requests MUST be redirected to the Entra ID login page by the Azure Static Web Apps platform, not by the docs site.
- No secrets, credentials, internal hostnames, or tokens MUST appear in any committed file or published artifact.

## Assumptions

- Authentication and authorisation are fully handled at the Azure Static Web Apps platform layer via Entra ID. The docs site itself has no auth code.
- The OpenAPI YAML is hand-authored and committed in the same PR as the API code change. CI-generated specs are a future option.
- A single OpenAPI spec (`openapi.yaml`) covers the first release; multi-service expansion is a future concern.
- Hosting target is **Azure Static Web Apps** (primary). GitHub Pages and internal static hosts are not used.
- The CI deploy step uses the Azure Static Web Apps GitHub Actions workflow (`azure/static-web-apps-deploy`) to publish the built `site/` directory.
- "Try It" interactive console suppression is sufficient via `tryItCredentialsPolicy="omit"` and `hideInternal="true"` on the Elements component; no server-side proxy blocking is required.
- Site search is scoped to the currently selected version only (MkDocs built-in behaviour with `mike`). Cross-version search is not required.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can go from `git clone` to a running local preview in under 5 minutes following the documented setup steps.
- **SC-002**: Every Markdown content page loads in under 3 seconds on a corporate wired network (measured from navigation start to the browser `load` event using Chrome DevTools → Network tab → `load` timing row), with ≤5 concurrent users.
- **SC-003**: The API Reference page (Stoplight Elements) fully renders all operations from the OpenAPI spec within 8 seconds of the browser `load` event on a corporate network (measured using Chrome DevTools → Performance tab → record a page load and locate the `load` event marker).
- **SC-004**: CI publishes a new versioned snapshot within 10 minutes of a release tag being pushed (from tag push to version visible in `versions.json`).
- **SC-005**: Zero broken internal links in any published version, verified by automated link checking on every merge.
- **SC-006**: 100% of pull requests are gated by markdownlint, strict-build, link-check, and OpenAPI validation before merge — no manual exceptions without a logged justification. Verified by auditing the GitHub repository's **branch protection rules** (Settings → Branches → `main`) and confirming `docs-ci` is listed as a required status check.
- **SC-007**: No public CDN URLs appear in any deployed site artifact. Verified by running: `grep -r -E "(unpkg\.com|cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|stackpath\.bootstrapcdn\.com)" site/` — command must return no output.
- **SC-008**: After 3 months of operation, documentation-related support questions (engineers asking where to find info that is already documented) decrease by at least 30% compared to the pre-site baseline.
