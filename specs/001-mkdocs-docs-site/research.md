# Research: MkDocs Internal Product Documentation Site

**Phase**: 0 — Pre-design research
**Date**: 2026-02-18
**Feeds into**: plan.md, data-model.md, contracts/

---

## R-01: Stoplight Elements Vendoring

**Question**: Which npm package + which dist files should be vendored for the `<elements-api>` web component?

**Decision**: Use `@stoplight/elements@9.0.15`.

**Rationale**: `@stoplight/elements-web-components` is effectively abandoned (v6.4.1, last published ~5 years ago). `@stoplight/elements` is the actively maintained package (43k+ weekly downloads; v9.0.15 published Feb 2026) and ships a self-contained web-components IIFE bundle at the package root.

**Files to vendor**:

| Source file in npm package | Dest in repo | Size |
|---|---|---|
| `web-components.min.js` | `docs/assets/vendor/web-components.min.js` | 2.09 MB |
| `styles.min.css` | `docs/assets/vendor/styles.min.css` | 298 kB |

**One open risk**: The CSS bundle may reference external font or icon URLs (e.g., `fonts.googleapis.com`). This must be verified in M2 by loading the page with DevTools Network open and offline mode applied to external domains. If external fetches are detected, extract and vendor those resources separately.

**Alternatives considered**:
- CDN reference at runtime (`unpkg.com`) — rejected; violates C-02 (no runtime CDN dependency) and the constitution's asset management rule.
- `@stoplight/elements-web-components@6.4.1` — rejected; unmaintained.

---

## R-02: Azure Static Web Apps + Entra ID Authentication

**Question**: How do we protect all routes with Entra ID without adding auth code to the docs site?

**Decision**: Use `staticwebapp.config.json` with the `aad` built-in provider + a **custom Entra ID provider configuration** (app registration required) to restrict access to a specific tenant.

**Key facts**:

| Item | Value |
|---|---|
| Config file | `staticwebapp.config.json` at repo root (copied to `output_location` by SWA) |
| Identity provider key | `aad` |
| Login route | `/.auth/login/aad` |
| Role for any logged-in user | `authenticated` (built-in) |
| Deploy action | `Azure/static-web-apps-deploy@v1` |
| Required secret | `AZURE_STATIC_WEB_APPS_API_TOKEN` (or OIDC token) |

**Minimal config** (all routes protected, unauthenticated → redirect to Entra ID login):

```json
{
  "routes": [
    {
      "route": "/*",
      "allowedRoles": ["authenticated"]
    }
  ],
  "responseOverrides": {
    "401": {
      "statusCode": 302,
      "redirect": "/.auth/login/aad"
    }
  }
}
```

**Tenant restriction**: The built-in `aad` provider accepts **any** Microsoft account (personal or organisational). To restrict to a specific Entra ID tenant, a custom provider with an app registration must be configured. This is non-negotiable for an internal site. The `auth` block in `staticwebapp.config.json` handles this — see the contracts specification.

**Rationale**: Platform-level auth means zero auth code in the docs site, consistent with the spec assumption and constitution security principle.

**Alternatives considered**:
- App-level auth (middleware, reverse proxy) — rejected; adds code complexity; not needed for a static site.
- No auth (rely on network perimeter) — rejected; hosting is on Azure SWA public endpoint; network perimeter not sufficient.

---

## R-03: `mike` + Azure Static Web Apps Compatibility

**Question**: Does `mike` work with Azure SWA (which uses artifact upload rather than git-backed hosting)?

**Decision**: Yes, with a minor workflow adaptation.

**Rationale**: `mike` writes versioned output to a local folder (default: `site/` or a configurable output dir). The Azure SWA deploy action (`azure/static-web-apps-deploy@v1`) then uploads that folder. The two tools are independent — `mike build` produces the static output; `azure/static-web-apps-deploy` publishes it. The key is setting `mike`'s deploy target to write locally (not push to `gh-pages`) and pointing `output_location` in the deploy action at the mike output directory.

**Workflow**:
```bash
# In CI:
git fetch --unshallow        # mike needs full git history for versions.json
mike deploy --no-push --update-aliases "$VERSION" latest
# output is written to <output_location> dir
# then azure/static-web-apps-deploy uploads that dir
```

**Risk**: If `mike` cannot write a complete site tree (all versions) from the local repo state alone, this approach breaks. Mitigation: pre-fetch the existing `versions.json` from the live site before running `mike deploy`, or maintain `versions.json` separately. In practice, `mike` in `--no-push` mode writes a complete versioned tree by reading the existing git history — this works if the checkout has full history (`fetch-depth: 0`).

---

## R-04: OpenAPI Validation Tool — `vacuum` vs `spectral`

**Question**: Which OpenAPI validation tool to use in CI?

**Decision**: `@quobix/vacuum` (npm package; CLI: `vacuum`). Note: the package was originally referenced as `@apideck-oss/vacuum` in early planning — the correct published npm package name is `@quobix/vacuum` (Apideck is a sponsor of the project, not the publisher).

**Rationale**:
- `vacuum` is significantly faster than `spectral` for large specs (Rust internals, millisecond validation times vs seconds for `spectral`).
- Supports OpenAPI 3.x and 3.1 natively.
- No cloud dependency; fully offline.
- npm package: `@apideck-oss/vacuum` — installs as `vacuum` CLI.
- Spectral is also a valid choice and has a richer ruleset ecosystem; prefer it if the team already has a Spectral ruleset.

**Alternatives considered**:
- `@stoplight/spectral-cli` — valid; richer built-in rulesets; slower for large specs; either works.
- `openapi-generator` validate — heavier, Java dependency; rejected.

---

## R-05: `latest` Alias Policy (resolved in spec)

**Decision**: Option A — `latest` = most recently published stable tag. `main` branch publishes as `dev`.

**Rationale**: Internal engineers reading `latest` always see a coherent, released version. Work-in-progress (on `main`) is accessible only under `dev`. This prevents readers from accidentally reading incomplete documentation between releases.

**`mike` commands**:
- On `main` push: `mike deploy --update-aliases dev`
- On `v*.*.*` tag push: `mike deploy --update-aliases $MAJOR_MINOR latest`

---

## R-06: Link Checking Tool

**Question**: Which link checker to use post-build?

**Decision**: `lychee` (via `lycheeverse/lychee-action` in CI) for external links (warning only); `mkdocs-linkcheck` or `htmltest` for internal links (blocking).

**Rationale**: `lychee` handles both internal and external links, is fast, and has a GitHub Action. For internal-only blocking checks, `htmltest` is simpler and faster. Either is acceptable; the key requirement from the constitution is that broken **internal** links block merge. External link failures are warnings only.

**Selected tool**: `lychee` with `--exclude-external` flag for the blocking internal-only check; second run without flag for warning-only external check.
