# Pre-PR Author Self-Review Checklist: MkDocs Internal Product Documentation Site

**Purpose**: "Unit tests" for requirement quality — validate that every requirement in this feature is complete, clear, consistent, and ready to implement before opening a pull request. Each item tests the *specification*, not the implementation.
**Created**: 2026-02-18
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md) | [tasks.md](../tasks.md)
**Audience**: Author, before opening a PR against `001-mkdocs-docs-site`

---

## Requirement Completeness

- [x] CHK001 Are all 25 functional requirements (FR-001–FR-025) traceable to at least one task in tasks.md? [Completeness, Spec §FR-001–FR-025]
- [x] CHK002 Are all 4 NFR sections (Availability, Performance, Observability, Security) present in spec.md with at least one specific, measurable value each? [Completeness, Spec §NFR]
- [x] CHK003 Are all 6 edge cases documented in spec.md (missing YAML, invalid YAML, large spec, first-deploy selector, patch immutability, non-existent URL)? [Completeness, Spec §Edge Cases]
- [x] CHK004 Are the 5 key entities in spec.md (Documentation Page, OpenAPI Specification, Site Version, Version Alias, Vendored Asset) each defined with their invariants and relationships? [Completeness, Spec §Key Entities]
- [x] CHK005 Is the permitted frontmatter keyset explicitly enumerated (`title`, `description`, `hide`) in an authoritative artifact that the `validate_frontmatter.py` hook can reference? [Completeness, Spec §FR-003, Gap]
- [x] CHK006 Is there a documented mechanism for collecting the SC-008 support-question baseline *before* go-live, not just as a post-launch retrospective? [Completeness, Spec §SC-008, tasks.md T048a]

---

## Requirement Clarity

- [x] CHK007 Are all performance targets quantified with specific numbers — pages < 3 s (SC-002), Elements < 8 s (SC-003), CI publish < 10 min (SC-004) — with the measurement method stated? [Clarity, Spec §SC-002–SC-004]
- [x] CHK008 Is "read-only mode" for the Elements component (FR-011) defined by specific attribute values (`tryItCredentialsPolicy="omit"`, `hideInternal="true"`) rather than a vague description? [Clarity, Spec §FR-011]
- [x] CHK009 Is the `x-internal: true` filter (FR-012) defined as the exact OpenAPI extension key an author must use — not just described in prose? [Clarity, Spec §FR-012]
- [x] CHK010 Is "immutable snapshot" (FR-017) explicitly defined: a published version is correctable only via a new patch release, never by retroactive edit? [Clarity, Spec §FR-017]
- [x] CHK011 Is the `latest` alias update rule (FR-018) unambiguous for all three trigger scenarios: main push (→ only `dev`), tag push (→ `MAJOR.MINOR` + `latest`), patch tag push (→ `MAJOR.MINOR` only)? [Clarity, Spec §FR-018]
- [x] CHK012 Is "zero broken internal links" (SC-005) scoped to what lychee checks — built `site/` relative links — rather than leaving the boundary implicit? [Clarity, Spec §SC-005, Ambiguity]
- [x] CHK013 Is SC-007 ("no CDN URLs in site/") defined with a concrete verification method (e.g., a specific `grep` pattern or list of known CDN hostnames to check)? [Clarity, Spec §SC-007, Ambiguity]
- [x] CHK014 Is the "non-existent version URL" edge case resolved beyond "404 or redirects to `latest` depending on hosting config"? Does `staticwebapp.config.json` define the exact behaviour? [Clarity, Spec §Edge Cases, Gap]

---

## Requirement Consistency

- [x] CHK015 Does the Stoplight Elements render time target match across all documents — US2-AS1, SC-003, plan.md NFR, and copilot-instructions.md — all stating **8 seconds**? [Consistency, Spec §US2-AS1 + §SC-003]
- [x] CHK016 Are the tool names consistent across spec.md, plan.md, tasks.md, constitution, and contracts — `lychee` for link checking, `vacuum` for OpenAPI, `gitleaks` for secrets — with no stale references to `mkdocs-linkcheck` or `spectral` as primary tools? [Consistency]
- [x] CHK017 Does the `mike deploy dev` command (without `--update-aliases latest`) in tasks.md T015 and plan.md M3 both correctly omit the `latest` alias, consistent with FR-018? [Consistency, Spec §FR-018, tasks.md T015]
- [x] CHK018 Is the nav hierarchy in FR-006 (Home → Getting Started → Concepts → How-to Guides → Reference → Release Notes) identical to the nav defined in contracts/mkdocs.yml.md? [Consistency, Spec §FR-006]
- [x] CHK019 Is the canonical OpenAPI YAML path (`docs/reference/openapi/openapi.yaml`) consistent across FR-010, tasks.md T020, contracts/ci-gate.yml.md, and scripts/smoke-test.sh? [Consistency, Spec §FR-010]
- [x] CHK020 Are the 5 MkDocs custom hooks (`validate_openapi.py`, `validate_frontmatter.py`) referenced both in tasks.md (T007c, T007d) and in the plan.md Repository Root project structure? [Consistency, plan.md §Project Structure]

---

## Acceptance Criteria Quality

- [x] CHK021 Does each of the 4 user stories (US1–US4) have at least one Given/When/Then scenario covering a **failure or exception path** (not only the happy path)? [Acceptance Criteria, Spec §User Scenarios]
- [x] CHK022 Is SC-001 (< 5 min setup) verifiable from the documented steps alone — could a reviewer time it end-to-end from `git clone` using only `docs/getting-started/installation.md`? [Acceptance Criteria, Spec §SC-001]
- [x] CHK023 Are SC-002 and SC-003 (page load and render time) measurable with a specific browser tool or method stated, rather than left to informal estimation? [Measurability, Spec §SC-002–SC-003]
- [x] CHK024 Is SC-006 ("100% of PRs gated") verifiable via a GitHub branch protection audit, not just an assertion? Is the verification method stated? [Measurability, Spec §SC-006]

---

## Scenario Coverage

- [x] CHK025 Is the "version selector on first deployment" edge case (only `dev`/`latest`, no numbered version yet) covered in `staticwebapp.config.json` — confirming the site renders without error on a lone selector entry? [Coverage, Spec §Edge Cases]
- [x] CHK026 Are all 5 OpenAPI endpoint completeness requirements from FR-013 (purpose, parameters, request body, response codes, error schema) traceable to the `vacuum` ruleset in contracts? [Coverage, Spec §FR-013]
- [x] CHK027 Is the "patch tag updates alias in place" scenario (FR-016, e.g., `v1.2.1` → updates `1.2`) covered by a dedicated end-to-end verification task (tasks.md T043)? [Coverage, Spec §FR-016]
- [x] CHK028 Is there a requirement or task covering what an author *sees* (and what they must do) when the gitleaks pre-commit hook fires locally — i.e., is the failure UX and remediation path documented? [Coverage, Gap]
- [x] CHK029 Is the MD033 `allowed_elements: ["elements-api"]` rule sufficient to prevent all other custom HTML in Markdown, or are there HTML elements permissible in other contexts that are not accounted for? [Coverage, Spec §FR-001, contracts/markdownlint.json.md]

---

## Non-Functional Requirements

- [x] CHK030 Is the "≤5 concurrent users, no SLA" constraint stated clearly enough to prevent an implementer from adding a CDN, load balancer, or auto-scaling configuration? [Clarity, Spec §NFR Availability]
- [x] CHK031 Is the "GitHub Actions CI logs only" observability scope stated explicitly enough to prevent implementers from adding Application Insights, Datadog, or other monitoring tools? [Clarity, Spec §NFR Observability]
- [x] CHK032 Is the Entra ID tenant restriction (custom app registration, not the default `aad` built-in provider) specified as a hard requirement, not an optional recommendation? [Clarity, Spec §NFR Security, contracts/staticwebapp.config.json.md]

---

## Dependencies & Assumptions

- [x] CHK033 Is the `azure/static-web-apps-deploy` action pinned to `@v1` (not `@latest`) in contracts/ci-deploy.yml.md to prevent unintentional upgrades? [Dependency, contracts/ci-deploy.yml.md]
- [x] CHK034 Is the `@stoplight/elements@9.0.15` version pinned and the source URL fixed in both VENDOR-VERSIONS.md and research.md R-01, so a future vendoring update has a clear procedure to follow? [Dependency, Spec §FR-019]
- [x] CHK035 Is the assumption that the OpenAPI spec is hand-authored (not CI-generated) documented explicitly in spec.md Assumptions, so future contributors do not introduce a code-generation step without an amendment? [Assumption, Spec §Assumptions]
- [x] CHK036 Are both the GitHub Actions secret (`AZURE_STATIC_WEB_APPS_API_TOKEN`) and the repository variable (`DOCS_BASE_URL`) named in an authoritative artifact (contracts or tasks), so an implementer knows exactly what to create in GitHub? [Dependency, tasks.md T036]

---

## Summary

| Category | Items | Estimated review time |
|----------|-------|-----------------------|
| Requirement Completeness | CHK001–CHK006 | ~3 min |
| Requirement Clarity | CHK007–CHK014 | ~4 min |
| Requirement Consistency | CHK015–CHK020 | ~3 min |
| Acceptance Criteria Quality | CHK021–CHK024 | ~2 min |
| Scenario Coverage | CHK025–CHK029 | ~3 min |
| Non-Functional Requirements | CHK030–CHK032 | ~2 min |
| Dependencies & Assumptions | CHK033–CHK036 | ~2 min |
| **Total** | **36 items** | **~19 min** |

> Mark each item `[x]` when satisfied. Add inline notes for any item that reveals a gap — open a tracked issue or update the relevant spec artifact before merging.
