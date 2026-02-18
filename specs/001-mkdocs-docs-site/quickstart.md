# Developer Quickstart

**Feature**: MkDocs Internal Product Documentation Site
**Audience**: Documentation authors and engineers working on this repo

---

## Prerequisites

| Tool | Required version | Install command |
|------|-----------------|-----------------|
| Python | 3.12 | `pyenv install 3.12` or system package |
| Node.js | 20 LTS | `nvm install 20` or system package |
| pip | ≥ 23 | bundled with Python 3.12 |
| npm | ≥ 10 | bundled with Node 20 |
| git | ≥ 2.39 | system package |

---

## 1. Clone and install dependencies

```bash
git clone <repo-url>
cd mkdocs-demo

# Python toolchain (MkDocs Material + mike)
pip install -r requirements.txt

# Node toolchain (markdownlint-cli2 + vacuum)
npm ci
```

---

## 2. Local preview

```bash
mkdocs serve
```

Open `http://localhost:8000`. Live-reload restarts automatically when any file under `docs/` changes.

The API Reference page at `http://localhost:8000/reference/api/` renders Stoplight Elements from the local vendored JS and the local `docs/reference/openapi/openapi.yaml`.

> **Tip**: If the Elements component renders blank, open DevTools → Console and check for errors. Most commonly: the `openapi.yaml` file is malformed or missing.

---

## 3. Pre-commit checks (run before every commit)

```bash
# Markdown lint
npx markdownlint-cli2 "docs/**/*.md"

# OpenAPI validation
npx vacuum lint docs/reference/openapi/*.yaml

# Full docs build (strict mode)
mkdocs build --strict
```

All three must exit 0 before opening a pull request. CI enforces the same checks and will prevent merge if any fail.

---

## 4. Authoring a new documentation page

1. Create a file in the appropriate section folder (e.g., `docs/how-to/connect-to-service.md`).
2. Add an H1 title as the first line.
3. Add frontmatter if needed (only `title`, `description`, `hide` are permitted):
   ```markdown
   ---
   title: Connect to the Service
   description: Step-by-step guide for connecting an application to the service.
   ---
   # Connect to the Service
   ```
4. Add the page to `mkdocs.yml` under the appropriate `nav` section.
5. Run the pre-commit checks (step 3) before opening a PR.

**Heading rules**:
- One H1 per page (the page title).
- Use H2 for major sections, H3 for subsections. Do not skip levels.

**Content rules**:
- No placeholder text: "TBD", "TODO", "Coming soon" are forbidden in merged content.
- Code samples must be syntactically valid.
- Cross-references must use relative Markdown links (e.g., `../concepts/index.md`), never absolute URLs to internal pages.

---

## 5. Authoring API reference (OpenAPI)

OpenAPI specs MUST be authored in YAML (not JSON). Edit `docs/reference/openapi/openapi.yaml`.

**Per-endpoint checklist** (all required before merge):

- [ ] `summary` or `description` on the operation
- [ ] All path parameters: `name`, `in: path`, `schema.type`, `description`, `example`
- [ ] All query parameters: same fields as path parameters
- [ ] Request body with at least one `example` (if the endpoint accepts a body)
- [ ] All response codes with inline or `$ref` schema
- [ ] At least one error response (4xx or 5xx) with a schema describing the error structure

**Multiline descriptions**: Use YAML block scalar for readability:

```yaml
description: |
  Returns the full profile for the specified user.

  Call this endpoint after authentication to retrieve display name,
  email, and role assignments.
```

**Validate**:

```bash
npx vacuum lint docs/reference/openapi/openapi.yaml
```

---

## 6. Updating vendored Stoplight Elements assets

Vendored assets are intentional snapshots and MUST NOT be updated automatically.

To update:

1. Check the latest version of `@stoplight/elements` on npm.
2. Download the two files:
   ```bash
   curl -o docs/assets/vendor/web-components.min.js \
     https://unpkg.com/@stoplight/elements@<NEW_VERSION>/web-components.min.js
   curl -o docs/assets/vendor/styles.min.css \
     https://unpkg.com/@stoplight/elements@<NEW_VERSION>/styles.min.css
   ```
3. Update `docs/assets/vendor/VENDOR-VERSIONS.md` with the new version, source URL, and date.
4. **Verify no CDN fetches**: Run `mkdocs serve`, open the API Reference page, and check DevTools → Network for any requests to external domains. If found, download those assets too and serve them locally.
5. Open a PR with just this change; include a note confirming the DevTools network verification.

---

## 7. Publishing a new version

Publishing is automated in CI. The workflow is:

| Action | Alias updated | CI trigger |
|--------|--------------|-----------|
| Push to `main` | `dev` | Automatic on every merge to `main` |
| Push `v1.2.0` tag | `1.2` + `latest` | Automatic on tag matching `v*.*.*` |
| Push `v1.2.1` tag | `1.2` (updated in place) + `latest` | Automatic |

**To tag a release manually**:

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

The deploy workflow picks it up automatically.

**Important**: `latest` always points to the most recently published numbered version. It is NOT updated by a push to `main` — only by a `v*.*.*` tag push.

---

## 8. Large OpenAPI spec guidance

If the spec exceeds ~1 MB, Stoplight Elements may render slowly:

- Split by service boundary into separate YAML files (add a new host page per spectrum).
- Remove verbose or redundant `examples` blocks from the spec; keep only 1–2 representative examples per operation.
- Do NOT inline large binary payloads or base64 content in examples.
- Use `$ref` to components to avoid duplicating schema definitions.

There is no automated enforcement of spec size; this is an authoring discipline responsibility.
