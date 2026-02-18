# Engineering Specification: MkDocs Internal Product Documentation Site

**Status**: Draft  
**Based on**: `ai-docs/initial-spec.md`  
**Date**: 2026-02-18  
**Scope**: MkDocs Material + Stoplight Elements + versioned publishing via `mike` on GitHub Enterprise Cloud

---

## 1. Requirements

### 1.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Authors write documentation in Markdown files under `docs/`. |
| FR-02 | The site renders using MkDocs with the Material for MkDocs theme. |
| FR-03 | An API reference page renders OpenAPI 3.x YAML using Stoplight Elements web component. |
| FR-04 | The version selector shows all published versions and `latest`; switching versions reloads docs for the selected version. |
| FR-05 | `mike` manages versioned deployments; every published version is immutable after publishing. |
| FR-06 | A developer can serve the full site locally (docs + API reference) with a single command. |
| FR-07 | CI publishes `latest` on every merge to `main`. |
| FR-08 | CI publishes a numbered version on every Git tag matching `v*.*.*`. |
| FR-09 | All builds are reproducible: same source + tag → identical output. |
| FR-10 | Release notes pages exist per product version and categorise changes as BREAKING / NEW / FIXED. |

### 1.2 Constraints

| ID | Constraint |
|----|-----------|
| C-01 | Site is internal only; authentication/authorisation is enforced at the hosting layer (GitHub Enterprise Cloud or internal reverse proxy). No auth code in the docs site itself. |
| C-02 | No runtime dependency on public CDNs. All JS, CSS, and font assets required for Stoplight Elements are vendored inside the repository. |
| C-03 | No secrets, credentials, internal hostnames, or tokens in any committed file or published artifact. |
| C-04 | `mkdocs build --strict` MUST succeed with zero warnings or errors. |
| C-05 | `markdownlint` MUST report zero errors against the project `.markdownlint.json` ruleset. |
| C-06 | Every OpenAPI YAML committed to the repo MUST pass OpenAPI 3.x schema validation. |
| C-07 | Published versioned snapshots are immutable. Bug-fixes to old docs require a new patch-version publication, not retroactive edits. |
| C-08 | The Stoplight Elements interactive "Try It" console is disabled or suppressed; this is a read-only internal reference site. |

---

## 2. Information Architecture

### 2.1 Repository Folder Structure

```text
/                          ← repository root
├── docs/                  ← all authored Markdown content
│   ├── index.md           ← Home / Overview page
│   ├── getting-started/
│   │   ├── index.md
│   │   ├── installation.md
│   │   └── quickstart.md
│   ├── concepts/
│   │   ├── index.md
│   │   └── architecture.md
│   ├── how-to/
│   │   ├── index.md
│   │   └── <task-guides>.md
│   ├── reference/
│   │   ├── api.md         ← Stoplight Elements host page (see §4)
│   │   └── openapi/
│   │       └── openapi.yaml   ← current-branch (main) OpenAPI spec
│   │           [or, for multi-service]
│   │           ├── service-a.yaml
│   │           └── service-b.yaml
│   ├── release-notes/
│   │   ├── index.md       ← version listing / changelog summary
│   │   └── v1.2.md        ← one file per MAJOR.MINOR release
│   └── assets/
│       ├── vendor/
│       │   ├── stoplight-elements.min.js   ← vendored JS (see §4.1)
│       │   └── stoplight-elements.min.css  ← vendored CSS
│       └── stylesheets/
│           └── extra.css  ← theme overrides (minimal)
├── mkdocs.yml             ← single config file (see §3)
├── .markdownlint.json
├── .github/
│   └── workflows/
│       ├── docs-ci.yml    ← PR build + lint + link check + OAS validation
│       └── docs-deploy.yml← publish on main push and v* tag
└── scripts/
    └── post-deploy-smoke.sh  ← post-deploy verification script
```

### 2.2 Navigation Structure

```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Overview: getting-started/index.md
      - Installation: getting-started/installation.md
      - Quickstart: getting-started/quickstart.md
  - Concepts:
      - Overview: concepts/index.md
      - Architecture: concepts/architecture.md
  - How-To Guides:
      - Overview: how-to/index.md
      # add guide pages here
  - Reference:
      - API Reference: reference/api.md
  - Release Notes:
      - Changelog: release-notes/index.md
      # per-version files discovered automatically or listed explicitly
```

### 2.3 OpenAPI Spec Placement

**Single-service** (default):

```
docs/reference/openapi/openapi.yaml
```

**Multi-service** (when more than one bounded context owns a separate spec):

```
docs/reference/openapi/
├── service-a.yaml
└── service-b.yaml
```

Each versioned snapshot published by `mike` bakes the OpenAPI YAML into the static output. The API reference page path-references the YAML relative to the page root, so each version's snapshot serves its own spec autonomously. See §5 for how this aligns with versioning.

---

## 3. MkDocs Configuration (`mkdocs.yml`)

```yaml
# mkdocs.yml
site_name: "Internal Product Docs"
site_description: "Internal engineering documentation"
site_url: ""          # leave empty; set by CI per environment
docs_dir: docs
site_dir: site

theme:
  name: material
  language: en
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
  features:
    - navigation.tabs          # top-level nav as tabs
    - navigation.sections      # render sub-sections in left sidebar
    - navigation.indexes       # section index pages (index.md per folder)
    - navigation.top           # back-to-top button
    - navigation.footer        # prev/next page links
    - search.highlight
    - search.suggest
    - content.code.copy        # copy button on code blocks
    - content.tabs.link        # linkable content tabs
  custom_dir: docs/overrides   # only if material overrides are needed (omit if empty)

extra:
  version:
    provider: mike
    default: latest

extra_css:
  - assets/stylesheets/extra.css
  - assets/vendor/stoplight-elements.min.css

extra_javascript:
  - assets/vendor/stoplight-elements.min.js

plugins:
  - search
  - mike:
      version_selector: true
      css_dir: assets/stylesheets
      javascript_dir: assets/javascripts

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - toc:
      permalink: true

# nav defined in §2.2
```

**Notes on plugin choices**:

- `mike` is the only versioning plugin used. Do not add `mike` + a second versioning plugin simultaneously.
- `search` is the built-in plugin; no Algolia or external search backend is used (internal site, no public indexing).
- Do not add `social` or `analytics` plugins (no external services).

---

## 4. Stoplight Elements Embedding

### 4.1 Vendored Asset Acquisition

Stoplight Elements ships as a self-contained web-component bundle. Acquire assets from the official npm package (do not link to CDN at runtime):

```bash
# run once, commit the output into the repo
npm pack @stoplight/elements@latest --dry-run   # inspect contents
# or download from the unpkg/npm dist and copy to docs/assets/vendor/
cp node_modules/@stoplight/elements/dist/web-components.min.js \
   docs/assets/vendor/stoplight-elements.min.js
cp node_modules/@stoplight/elements/dist/web-components.min.css \
   docs/assets/vendor/stoplight-elements.min.css
```

Pin the exact version used in a comment at the top of each vendored file and in a `docs/assets/vendor/VENDOR-VERSIONS.md` inventory file. Update vendored assets intentionally (not automatically), treat as a dependency bump, and verify behaviour locally before merging.

### 4.2 The API Reference Host Page (`docs/reference/api.md`)

```markdown
---
title: API Reference
hide:
  - toc          # Elements provides its own sidebar; avoid double navigation
  - navigation   # optional: hide left nav when Elements is full-width
---

# API Reference

<elements-api
  apiDescriptionUrl="./openapi/openapi.yaml"
  router="hash"
  layout="sidebar"
  hideInternal="true"
  tryItCredentialsPolicy="omit"
></elements-api>
```

**Attribute explanations**:

| Attribute | Value | Reason |
|-----------|-------|--------|
| `apiDescriptionUrl` | `./openapi/openapi.yaml` | Relative path; works in all versions since each mike snapshot includes its own copy of the spec. |
| `router` | `hash` | Hash routing avoids conflicts with MkDocs static routing and works without a server-side router. |
| `layout` | `sidebar` | Sidebar layout is readable-first (vs `stacked`). |
| `hideInternal` | `true` | Suppresses endpoints/operations marked `x-internal: true` in the OpenAPI spec. |
| `tryItCredentialsPolicy` | `omit` | Disables credential forwarding; "Try It" is effectively read-only per constraint C-08. |

> **Disabling "Try It" entirely**: Elements does not have a single `disableTryIt` boolean in all versions. Setting `tryItCredentialsPolicy="omit"` and (`hideServer` if supported) reduces the interactive surface. If a release of Elements adds a `hideTryIt` attribute, prefer that.

### 4.3 Multi-Service Variant

If multiple OpenAPI specs exist, create one host page per service:

```
docs/reference/
├── service-a-api.md     ← apiDescriptionUrl="./openapi/service-a.yaml"
├── service-b-api.md     ← apiDescriptionUrl="./openapi/service-b.yaml"
└── openapi/
    ├── service-a.yaml
    └── service-b.yaml
```

Add each to the `Reference` nav section in `mkdocs.yml`.

### 4.4 Local Developer Experience

With the vendored assets in place and `mkdocs.yml` referencing them, a developer can run:

```bash
mkdocs serve
```

Then open `http://localhost:8000/reference/api/` to see the Elements component rendering from the local `openapi.yaml`. No network access is required.

---

## 5. Versioning Strategy

### 5.1 Git Tag Convention

```
v<MAJOR>.<MINOR>.<PATCH>

Examples:
  v1.0.0   → first release
  v1.2.0   → new features in the 1.x line
  v1.2.1   → patch/bug-fix in the 1.2 line
  v2.0.0   → breaking change
```

Lightweight tags are acceptable but annotated tags are preferred (they carry a message describing the release).

### 5.2 Published Version Identifiers

`mike` publishes versions using the `<MAJOR>.<MINOR>` identifier (drop the patch segment):

```
mike deploy --update-aliases 1.2 latest   # for v1.2.0 and later 1.2.x patches
```

Patch releases overwrite the existing `1.2` alias; they do not create a separate `1.2.1` entry in the version selector. This keeps the selector readable.

### 5.3 The `latest` Alias

**Policy** (TBD; choose one before first deployment — see TODO in constitution):

- **Option A** *(recommended)*: `latest` = the most recently published stable tag. `main` branch docs are published under a `dev` alias, not `latest`. Users reading `latest` always see a coherent released version.
- **Option B**: `latest` = `main` branch HEAD. Choose this only if the team wants readers to see unreleased changes by default.

Update `mkdocs.yml` `extra.version.default` accordingly (`latest` in Option A, `dev` in Option B if main is `dev`).

### 5.4 Version Selector Appearance

With `mike` and Material's version plugin configured (`extra.version.provider: mike`), the selector appears in the top navigation bar automatically. The JSON at `<site-root>/versions.json` (maintained by `mike`) drives the selector.

### 5.5 OpenAPI Spec Alignment with Versions

The OpenAPI YAML committed on the branch being published IS the spec for that version. There is no separate spec extraction step — the YAML under `docs/reference/openapi/` is authored in the same repo, committed alongside code changes, and snapshotted as part of the `mike deploy` output.

**Discipline required**: When a code change alters API behaviour, the OpenAPI YAML MUST be updated in the same pull request. A linting step (`spectral`/`vacuum`) in CI enforces structural validity; prose-vs-spec divergence is caught by documentation review in the PR.

---

## 6. CI/CD

### 6.1 Workflow Split

Two separate GitHub Actions workflow files:

| File | Trigger | Purpose |
|------|---------|---------|
| `.github/workflows/docs-ci.yml` | `pull_request` to `main` | Quality gates — never deploys |
| `.github/workflows/docs-deploy.yml` | `push` to `main`; `push` of `v*.*.*` tag | Build + deploy only after gates pass |

### 6.2 CI Workflow (`docs-ci.yml`)

```yaml
name: Docs CI

on:
  pull_request:
    branches: [main]

jobs:
  lint-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # needed for mike version history

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python deps
        run: pip install mkdocs-material mike mkdocs-linkcheck

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Node deps
        run: npm ci                # package-lock.json pins markdownlint-cli2, vacuum/spectral

      - name: Markdown lint
        run: npx markdownlint-cli2 "docs/**/*.md"

      - name: OpenAPI validation
        run: npx vacuum lint docs/reference/openapi/*.yaml
        # or: npx @stoplight/spectral-cli lint docs/reference/openapi/*.yaml

      - name: Docs build (strict)
        run: mkdocs build --strict

      - name: Internal link check
        run: python -m mkdocs_linkcheck site/
        # or whichever link-check integration is chosen

      - name: Secret scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 6.3 Deploy Workflow (`docs-deploy.yml`)

```yaml
name: Docs Deploy

on:
  push:
    branches: [main]
    tags:
      - "v*.*.*"

permissions:
  contents: write     # mike writes to gh-pages branch

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure git
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install deps
        run: pip install mkdocs-material mike

      - name: Deploy latest (main push)
        if: github.ref == 'refs/heads/main'
        run: mike deploy --push --update-aliases dev latest
        # Change 'dev' to 'latest' if using Option B versioning policy

      - name: Deploy versioned snapshot (tag push)
        if: startsWith(github.ref, 'refs/tags/v')
        run: |
          VERSION=$(echo "${{ github.ref_name }}" | sed 's/^v//' | cut -d. -f1,2)
          mike deploy --push --update-aliases "$VERSION" latest

      - name: Post-deploy smoke test
        run: bash scripts/post-deploy-smoke.sh "$VERSION_OR_DEV"
        # See §6.4
```

> **Hosting target note**: The workflow above assumes GitHub Pages as the deployment target (mike pushes to `gh-pages` branch). For an internal static host, replace the `mike deploy --push` step with a step that copies `site/` to the internal host via `rsync`, SCP, or blob storage upload. The build steps remain identical.

### 6.4 Post-Deploy Smoke Test (`scripts/post-deploy-smoke.sh`)

The script performs HTTP GET requests against the freshly deployed URL and asserts:

1. The version appears in `<base-url>/versions.json`.
2. HTTP 200 for `<base-url>/<version>/index.html`.
3. HTTP 200 for `<base-url>/<version>/reference/api/index.html`.
4. The OpenAPI YAML is accessible at `<base-url>/<version>/reference/openapi/openapi.yaml`.
5. The vendored JS asset returns HTTP 200 (confirming it was included in the deploy).

If any check fails, the script exits non-zero and the workflow step fails, triggering an alert. The deployment is already live at that point (mike pushed), so human rollback is needed; consider automating rollback by re-publishing the previous version with `mike deploy`.

### 6.5 Python & Node Dependency Pinning

```
requirements.txt (Python):
  mkdocs-material==9.x.x
  mike==2.x.x
  mkdocs-linkcheck==x.x.x

package.json (Node):
  {
    "devDependencies": {
      "markdownlint-cli2": "^0.x.x",
      "@stoplight/spectral-cli": "^6.x.x"  ← or @apideck-oss/vacuum
    }
  }
```

Pin to exact versions; bump intentionally and test locally before merging.

---

## 7. Acceptance Criteria / Definition of Done

A reviewer signs off when ALL of the following are verified:

### Local Development (AC-1–AC-4)

- [ ] **AC-1**: `mkdocs serve` starts without errors and the site opens at `http://localhost:8000`.
- [ ] **AC-2**: Navigating to `/reference/api/` renders the Stoplight Elements component displaying the local `openapi.yaml` without any external network requests (verify via browser DevTools → Network → filter by domain ≠ localhost).
- [ ] **AC-3**: No console errors related to missing assets or CORS failures when running locally.
- [ ] **AC-4**: `mkdocs build --strict` exits 0 with no warnings.

### Content & Lint (AC-5–AC-7)

- [ ] **AC-5**: `npx markdownlint-cli2 "docs/**/*.md"` exits 0 with no errors.
- [ ] **AC-6**: OpenAPI YAML validation (`vacuum lint` or `spectral lint`) exits 0.
- [ ] **AC-7**: Internal link check finds zero broken links (`site/` after build).

### Versioning (AC-8–AC-11)

- [ ] **AC-8**: After pushing a `v1.0.0` tag, CI publishes a `1.0` entry in the deployed site's version selector.
- [ ] **AC-9**: After merging to `main`, CI publishes/updates the `dev` (or `latest`) alias.
- [ ] **AC-10**: `<base-url>/versions.json` lists all expected versions after both test deployments.
- [ ] **AC-11**: Selecting version `1.0` in the version selector loads that version's docs (including its own copy of `openapi.yaml`) without referencing content from another version.

### API Reference (AC-12–AC-14)

- [ ] **AC-12**: Every operation in `openapi.yaml` appears in the Stoplight Elements sidebar on the API reference page.
- [ ] **AC-13**: No public CDN URLs appear in the built output (`grep -r "unpkg.com\|cdn.jsdelivr.net\|cdnjs.cloudflare.com" site/` must return empty).
- [ ] **AC-14**: The "Try It" interactive console is suppressed or non-functional (no live requests leave the browser from the API reference page when clicking any "try it" feature).

### Security & Secrets (AC-15–AC-16)

- [ ] **AC-15**: `gitleaks detect` on the repository (including history) returns no findings.
- [ ] **AC-16**: No internal hostnames, IP ranges, bearer tokens, or passwords appear in any file under `docs/`, `site/`, or `mkdocs.yml`.

### CI/CD (AC-17–AC-19)

- [ ] **AC-17**: A pull request that introduces a broken Markdown link causes CI to fail (demonstrates link-check gate is enforced).
- [ ] **AC-18**: A pull request that introduces an invalid OpenAPI YAML causes CI to fail (demonstrates OAS validation gate is enforced).
- [ ] **AC-19**: Post-deploy smoke test script returns exit code 0 after a successful deployment and non-zero when a checklist item fails (verify by intentionally breaking a page, deploying, and observing smoke-test failure).

---

## 8. Open Decisions (must be resolved before first production deployment)

| # | Decision | Options | Impact |
|---|----------|---------|--------|
| D-01 | Hosting target | GitHub Pages (enterprise private repo) vs internal static host | Affects deploy step in `docs-deploy.yml` and base URL configuration |
| D-02 | `latest` alias policy | Option A: most recent tag / Option B: `main` HEAD | Affects `mike deploy` command arguments and `extra.version.default` in `mkdocs.yml` |
| D-03 | OpenAPI source of truth | Committed YAML reviewed in PR vs generated by CI from application code | Affects whether `docs/reference/openapi/` holds a hand-authored or auto-generated file; determines if a sync step is needed in CI |
| D-04 | Single vs multi-service OpenAPI | One `openapi.yaml` vs one per bounded context | Affects nav structure, Elements page count, and validation step |
| D-05 | Interactive "Try It" suppression approach | `tryItCredentialsPolicy="omit"` only vs full disable (flag or proxy-block) | Minor UX difference; confirm with security team |

---

*End of engineering specification.*
