# Data Model: MkDocs Internal Product Documentation Site

**Phase**: 1 — Design
**Date**: 2026-02-18

This document defines the content model, frontmatter schema, navigation structure, and validation rules for the documentation site. It replaces the traditional "data model" for a docs-only project.

---

## Entities

### 1. Documentation Page

A single Markdown file under `docs/`. The fundamental unit of authoring.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `title` | frontmatter string | No (falls back to H1) | Max 80 chars; use H1 as single source of truth; frontmatter title overrides nav display only |
| `description` | frontmatter string | No | Max 160 chars; used for site search result preview only |
| `hide` | frontmatter list | No | Allowed values: `toc`, `navigation`. Only permitted on API reference page. |
| H1 heading | Markdown body | Yes | Exactly one per page; matches or closely resembles the title |
| Body content | Markdown | Yes | Must not contain placeholder text; must follow heading hierarchy |

**Allowed frontmatter keys**: `title`, `description`, `hide`. All other keys are forbidden without an authoring-guide amendment.

**Nav section membership**: Each page belongs to exactly one top-level nav section (see Navigation Model below). Pages MUST NOT be symlinked or referenced from multiple nav entries.

---

### 2. OpenAPI Specification

The YAML file representing the API contract for one service at a given version snapshot.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `openapi` | string | Yes | Must be `3.0.x` or `3.1.x` |
| `info.title` | string | Yes | Product name; matches site name |
| `info.version` | string | Yes | Must match `MAJOR.MINOR.PATCH` of the product release |
| `info.description` | string | Yes | Brief purpose statement (1–3 sentences) |
| `paths` | object | Yes | At least one path; all paths must satisfy completeness rules below |
| `components.schemas` | object | Conditional | Required if any `$ref` is used in paths |

**Per-endpoint completeness rules** (from FR-013):

| Item | Required | Notes |
|------|----------|-------|
| `summary` or `description` | Yes | At least one; `description` preferred for detail |
| All path parameters documented | Yes | `name`, `in`, `schema.type`, `description`, at least one `example` |
| All query parameters documented | Yes | Same as path parameters |
| All header parameters documented | Yes | Same; omit standard headers like `Authorization` if auth is platform-managed |
| Request body with at least one example | Conditional | Required if the operation accepts a body |
| All declared response codes with `$ref` or inline schema | Yes | Min: one 2xx, one 4xx or 5xx |
| Error response schema | Yes | At least one error response with a schema object documenting the error structure |

**Validation**: `vacuum lint docs/reference/openapi/*.yaml` must exit 0 in CI using the `@apideck-oss/vacuum` default ruleset, which enforces structural OpenAPI 3.x correctness (valid schema refs, response object presence, operation ID uniqueness, etc.). The per-endpoint completeness rules in the table above (parameter examples, error schemas, request body examples) are **authoring requirements** verified by the PR reviewer sign-off process (T047), not by automated vacuum rules. Authors MUST consult the table above before opening a PR.

**State transitions / lifecycle**:
```
[authored on feature branch]
  → [PR opened: vacuum validates]
  → [merged to main: committed as current spec]
  → [v* tag: baked into versioned snapshot]
  → [immutable in snapshot: never edited retroactively]
```

---

### 3. Site Version

A named, immutable snapshot of all documentation pages and the OpenAPI spec, managed by `mike`.

| Field | Type | Constraints |
|-------|------|-------------|
| `version_id` | string | Format: `MAJOR.MINOR` (e.g., `1.2`). Never includes patch segment in selector. |
| `aliases` | list of strings | Subset of `latest`, `dev`. `latest` only updated on `v*.*.*` tag publish. |
| `title` | string | Optional; used by mike for display. Set to `MAJOR.MINOR` by default. |
| `created_from` | git tag | `v<MAJOR>.<MINOR>.<PATCH>`; recorded in release notes. |
| `is_mutable` | bool | Always `false` for a numbered version after publish. `dev`/`latest` aliases are mutable pointers. |

**`versions.json` structure** (written by `mike`, consumed by Material version selector):
```json
[
  { "version": "1.2", "title": "1.2", "aliases": ["latest"] },
  { "version": "1.1", "title": "1.1", "aliases": [] },
  { "version": "dev",  "title": "dev",  "aliases": [] }
]
```

---

### 4. Version Alias

A mutable pointer managed by `mike`. Redirects readers to a specific versioned snapshot.

| Alias | Points to | Updated by |
|-------|-----------|-----------|
| `latest` | Most recently published `MAJOR.MINOR` snapshot | `v*.*.*` tag push in CI |
| `dev` | `main` branch HEAD snapshot | Every push to `main` in CI |

Aliases are NOT separate published versions; they are entries in `versions.json` with `"aliases"` containing the pointer name.

---

### 5. Vendored Asset

A file copied from a fixed npm package version into `docs/assets/vendor/`.

| Field | Constraints |
|-------|-------------|
| Source package | Pinned: `@stoplight/elements@9.0.15` |
| Source file | `web-components.min.js`, `styles.min.css` |
| Dest path | `docs/assets/vendor/<exact-source-filename>` |
| Update policy | Intentional only; requires: (a) local verification, (b) `VENDOR-VERSIONS.md` update, (c) PR review |

**`VENDOR-VERSIONS.md` schema** (free-form Markdown table, required fields):

| Column | Example |
|--------|---------|
| Package | `@stoplight/elements` |
| Version | `9.0.15` |
| Files vendored | `web-components.min.js`, `styles.min.css` |
| Source URL | `https://unpkg.com/@stoplight/elements@9.0.15/<file>` |
| Vendored date | `2026-02-18` |
| Vendor'd by | GitHub username |

---

## Navigation Model

Fixed hierarchy (deviations require a constitution amendment):

```
Home (docs/index.md)
Getting Started
  ├── Overview (docs/getting-started/index.md)
  ├── Installation (docs/getting-started/installation.md)
  └── Quickstart (docs/getting-started/quickstart.md)
Concepts
  └── Overview (docs/concepts/index.md)
  └── [additional concept pages]
How-To Guides
  └── Overview (docs/how-to/index.md)
  └── [task-focused guide pages]
Reference
  └── API Reference (docs/reference/api.md)        ← Elements host page
Release Notes
  └── Changelog (docs/release-notes/index.md)
  └── [per-MAJOR.MINOR release note pages]
```

**Nav section rules**:
- Each section folder MUST have a `index.md` (used as the section landing page via `navigation.indexes` Material feature).
- New top-level sections require an amendment to `mkdocs.yml` nav AND a link-map test before content is added.

---

## Release Notes Schema

Each release notes page (e.g., `docs/release-notes/v1.2.md`) MUST follow this structure:

```markdown
# Release Notes — 1.2

**Released**: YYYY-MM-DD
**Git tag**: v1.2.0

## BREAKING Changes
- [List; empty section = omit the heading]

## NEW
- [List]

## FIXED
- [List]
```

**Categorisation rules** (aligned with constitution Principle IV):
- `BREAKING` → corresponds to MAJOR semver increment; consumers must take action.
- `NEW` → corresponds to MINOR semver increment; additive changes.
- `FIXED` → corresponds to PATCH semver increment; bug fixes, corrections.

Empty categories MUST be omitted (do not include a heading with "None").
