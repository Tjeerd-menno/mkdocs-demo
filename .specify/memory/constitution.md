<!--
SYNC IMPACT REPORT
==================
Version change:    0.0.0 (unfilled template) -> 1.0.0 -> 1.0.1 -> 1.0.2
Modified principles:
  1.0.0 — N/A: initial ratification (all principles are new)
  1.0.1 — Principle V: removed TODO(VERSIONING_ALIAS_POLICY), replaced with resolved policy text
  1.0.2 — Principle II body + CI/CD table: standardised on `lychee` (was `mkdocs-linkcheck or equivalent`)

Added sections:
  - Core Principles (5 principles: I–V)
  - Authoring & Tooling Standards
  - CI/CD Quality Gates
  - Governance

Removed sections: N/A

Templates reviewed:
  ✅ .specify/templates/plan-template.md  — Constitution Check gate aligns with all 5 principles
  ✅ .specify/templates/spec-template.md  — FR / Success Criteria structure consistent with Principles II and IV
  ✅ .specify/templates/tasks-template.md — Phase structure consistent with Principles II (test tasks) and V (versioning tasks)

Follow-up TODOs:
  ✅ RESOLVED(HOSTING_TARGET): Azure Static Web Apps with Entra ID protection (custom aad provider,
     tenant-restricted app registration). Governance section phrasing remains valid.
  ✅ RESOLVED(OPENAPI_SOURCE): OpenAPI spec is committed as a YAML artifact in the same PR as the
     code change (not CI-generated). Principle IV gate confirmed correct.
  ✅ RESOLVED(VERSIONING_ALIAS_POLICY): `latest` alias = most recently published stable tag (Option A).
     `main` push updates only the `dev` alias. Principle V updated accordingly.

Version 1.0.1 (2026-02-18): Closed deferred TODOs from initial ratification. No principle wording changed.
-->

# MkDocs Internal Product Docs Constitution

## Core Principles

### I. Markdown & Content Quality

Every piece of published content MUST meet a defined quality bar before it reaches the deployed site.

- All Markdown files MUST pass `markdownlint` with zero errors; no rule suppressions without explicit,
  documented justification committed alongside the suppression.
- Published pages MUST NOT contain stub text, "TBD", "TODO", "Coming soon", or placeholder headings.
  Work-in-progress content MUST remain on a feature branch until complete.
- Embedded code samples MUST be syntactically valid and, where feasible, extracted from tested source
  files or CI-verified snippets. Copy-pasted, untested code samples are forbidden.
- Each page MUST have a single, clear purpose. Omnibus "miscellaneous" pages are forbidden; reorganize
  content into appropriate sections before merging.
- Frontmatter MUST use only the fields defined in the project authoring guide. Undocumented or
  "creative" frontmatter keys MUST NOT be introduced without a constitution amendment or authoring-guide update.

**Rationale**: Documentation is a product surface. Low-quality content erodes trust, increases support
burden, and makes AI-agent-assisted authoring unreliable. A consistent, lint-enforced baseline keeps
the corpus machine-readable and human-trustworthy.

### II. Test Before Publish (NON-NEGOTIABLE)

No documentation change reaches the deployment target without passing automated quality gates in CI.

- The CI pipeline MUST run the following checks on every pull request targeting `main`:
  1. `markdownlint` — zero warnings, zero errors.
  2. `mkdocs build --strict` — build MUST succeed with no warnings.
  3. Link checking (`lychee`) — zero broken internal links; external link
     failures are warnings, not blocking, but MUST be triaged within one sprint.
  4. OpenAPI schema validation (`vacuum` or `spectral`) — every OpenAPI YAML committed to the repo
     MUST conform to OpenAPI 3.x and pass the configured ruleset.
- Tests for new content categories (e.g., a new top-level nav section) MUST be written as link-map
  assertions or smoke-test scripts before the content is authored, following a docs-TDD approach.
- Versioned snapshots published via `mike` MUST be verified by a post-deploy smoke test confirming:
  - The version appears in the version selector.
  - The OpenAPI reference page loads and references the correct spec version.

**Rationale**: "It looks fine locally" is not a quality gate. Automated enforcement prevents regressions,
broken links, and malformed specs from reaching internal users who depend on this site for their work.

### III. User Experience Consistency

All pages across all versions MUST provide a coherent, predictable reading experience.

- Navigation MUST follow the approved Information Architecture hierarchy:
  Home → Getting Started → Concepts → How-to Guides → Reference → Release Notes.
  Deviations require a documented IA amendment, not ad-hoc restructuring.
- Heading hierarchy MUST be respected on every page: H1 (page title, one per page) → H2 (major
  sections) → H3 (subsections) → H4 (rarely; only for deep reference material). Skipping levels
  is forbidden.
- Admonitions, callouts, tabs, and code blocks MUST use Material for MkDocs built-in components.
  Custom HTML widgets are forbidden unless standard components provably cannot satisfy the need,
  and then only after review and documentation in the authoring guide.
- Cross-references between pages MUST use relative Markdown links (e.g., `../section/page.md`).
  Absolute URLs pointing to internal pages are forbidden — they break versioning and local dev.
- The Stoplight Elements API reference page MUST be visually integrated using the site colour tokens
  where Elements supports customization. CSS overrides beyond the approved theming shim require review.

**Rationale**: Consistency reduces cognitive load. Internal engineers switching between doc versions
or doc sections MUST not have to re-learn navigation or scanning patterns. The cost of inconsistency
compounds across every reader session.

### IV. Technical Documentation Completeness

Technical content MUST be accurate, complete, and traceable to authoritative sources.

- Every HTTP API endpoint documented via Stoplight Elements MUST have, at minimum:
  - A description of purpose.
  - All path, query, and header parameters documented with types, constraints, and examples.
  - At least one request body example (where applicable).
  - All documented response codes with schema references and human-readable descriptions.
  - At least one error response (4xx or 5xx) with error schema documented.
- Conceptual pages MUST follow the "Why before How" structure: rationale and context MUST precede
  procedural steps. Pages that are purely procedural without conceptual framing MUST be filed as
  How-to Guides, not Concepts.
- Release notes MUST categorize changes using BREAKING/NEW/FIXED labels, aligned with the product
  semver policy (MAJOR → BREAKING, MINOR → NEW, PATCH → FIXED).
- The OpenAPI YAML committed to the docs repo is the single source of truth for API reference. Prose
  descriptions of API behaviour that contradict the OpenAPI spec MUST be treated as bugs and resolved
  within one sprint of discovery.

**Rationale**: Incomplete or inaccurate technical docs are worse than no docs — they create false
confidence and debugging overhead. The OpenAPI spec as source of truth ensures docs and API stay
synchronized across releases.

### V. Versioning Discipline

Documentation versioning MUST be tight, predictable, and aligned with product releases.

- Docs versions MUST be published using `mike` and MUST correspond 1:1 to product Git tags
  (`v<MAJOR>.<MINOR>.<PATCH>`). Docs MUST NOT be published for commits without a corresponding
  product tag, except for the `dev` alias which tracks `main`.
- The `latest` alias MUST point to the most recently published stable tag. Publishing a new stable
  tag MUST update `latest`; pushing to `main` MUST NOT update `latest` (only `dev`).
- Version identifiers in the published site MUST use the format `<MAJOR>.<MINOR>` (e.g., `1.2`).
  Patch-only releases MUST update docs under the existing `<MAJOR>.<MINOR>` alias.
- Once a versioned snapshot is published, its content is immutable. Corrections to old version docs
  require a new patch release — retroactive edits to a deployed snapshot are forbidden.
- Breaking changes to the Information Architecture or top-level navigation MUST be treated as a docs
  major version event and communicated in the release notes.

**Rationale**: Version discipline ensures engineers reading docs for `v1.2` see exactly what was
current at that release. Mutable history creates confusion in incident investigations and audits.

## Authoring & Tooling Standards

- **Editor tooling**: Authors MUST configure their editor to run `markdownlint` on save. The project
  `.markdownlint.json` is the authoritative ruleset.
- **Local preview**: Authors MUST verify changes locally with `mkdocs serve` before opening a PR.
  "It built in CI" is not a substitute for human visual review on the Material theme.
- **OpenAPI authoring**: OpenAPI specs MUST be authored in YAML (not JSON). Inline descriptions
  MUST use `|` block scalar for multiline content to remain diff-friendly.
- **Asset management**: JavaScript and CSS assets for Stoplight Elements MUST be vendored into the
  repository under `docs/assets/vendor/`. Runtime fetches from public CDNs are forbidden for core
  rendering assets (security and reliability requirement).
- **No secrets**: No API keys, tokens, internal hostnames, or credentials MUST appear in any committed
  file. Pre-commit hooks MUST enforce secret scanning (`gitleaks` or equivalent).
- **Minimal custom code**: Custom MkDocs hooks and overrides MUST be kept minimal and documented.
  Each hook MUST have a comment explaining why a standard plugin was insufficient.

## CI/CD Quality Gates

The following gates MUST be enforced and are blocking for all merges to `main`:

| Gate | Tool | Failure Action |
|------|------|----------------|
| Markdown linting | `markdownlint-cli2` | Block merge |
| Docs build | `mkdocs build --strict` | Block merge |
| Internal link check | `lychee` (`mkdocs-linkcheck` equivalent) | Block merge |
| OpenAPI validation | `vacuum` / `spectral` | Block merge |
| Secret scanning | `gitleaks` | Block merge |
| External link check | `lychee` or equivalent | Warning; triage within 1 sprint |
| Post-deploy smoke test | Custom script | Rollback trigger if failed |

Bypassing gates via admin merge MUST be logged, linked to an incident or emergency rationale, and
followed up with a remediation PR within two business days.

## Governance

- This constitution supersedes all other authoring preferences, style guides, or undocumented
  conventions. When conflict arises, the constitution wins.
- **Amendment procedure**: Any principle change requires a pull request that:
  1. Updates this constitution with a new version per the semantic versioning policy below.
  2. Updates the Sync Impact Report comment at the top of this file.
  3. Is reviewed and approved by the Tech Docs Lead and at least one senior engineer.
  4. Includes a migration plan if existing published content violates the new principle.
- **Versioning policy**:
  - MAJOR bump: Removal or incompatible redefinition of an existing principle.
  - MINOR bump: New principle or section added; materially expanded guidance.
  - PATCH bump: Clarification, wording improvement, or typo fix.
- **Compliance review**: On the first working day of each month, the Tech Docs Lead reviews all merged
  PRs from the prior month against the active principles and logs any violations in the project issue
  tracker with a `docs-constitution-gap` label.
- **Runtime guidance**: For day-to-day authoring decisions not covered by the principles above, refer
  to the project authoring guide (to be maintained alongside this constitution in `.specify/memory/`).

**Version**: 1.0.2 | **Ratified**: 2026-02-18 | **Last Amended**: 2026-02-18
