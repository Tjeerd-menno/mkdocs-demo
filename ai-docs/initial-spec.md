# Spec: Internal Product Docs with MkDocs + Stoplight Elements (OpenAPI)

## 1. Summary
Create an internal documentation site using **MkDocs Material** for versioned product docs and **Stoplight Elements** for modern, good-looking OpenAPI reference documentation embedded inside the site. The docs site is **not public** and will be hosted inside our enterprise environment (GitHub Enterprise Cloud deployment target).

This spec covers:
- Site structure and authoring conventions (Markdown-first)
- Embedding Stoplight Elements for OpenAPI reference pages
- Versioning strategy aligned with product releases
- CI build + deployment approach

---

## 2. Goals
- Provide a **Markdown-first** internal documentation site.
- Provide **high-quality API reference** using **Stoplight Elements** rendered from OpenAPI.
- Support **versioned documentation** aligned with product releases (tags).
- Ensure the workflow works well with **AI agents** (predictable structure, minimal magic).
- Use a simple, maintainable CI pipeline on GitHub.

---

## 3. Non-Goals
- Public documentation hosting or SEO optimization.
- Complex multi-tenant docs portals for external customers.
- Fully interactive API “try it out” with live credentials (may be added later if needed).
- Replacing code-level API docs generation tooling (we will consume OpenAPI output).

---

## 4. Audience & Use Cases
### Primary users
- Internal engineers, QA, service engineers, product owners.

### Primary use cases
- Read product docs for a specific released version (e.g., v2.3).
- Read API reference in a modern UI (Stoplight Elements) for that same version.
- Keep “latest” docs for ongoing development (main branch).
- Allow PR-based review for docs changes.

---

## 5. High-Level Approach
### Documentation engine
- **MkDocs** with **Material for MkDocs** theme
- Site content in `docs/` (Markdown files)

### API reference
- Use **Stoplight Elements** (web components) embedded in an MkDocs page.
- OpenAPI specs stored under version control inside the docs tree:
  - `docs/openapi/openapi.yaml` (for current branch)
  - or `docs/openapi/<service>/<version>/openapi.yaml` if multiple specs exist

### Versioning
- Version docs based on **Git tags** (e.g., `v1.8.0`) and publish immutable versions.
- Use `mike` to publish versions:
  - `latest` points to main (or most recent release tag—choose one and be consistent)
  - version list includes `1.8`, `1.7`, etc. (exact format to be decided in plan)

### Build & deploy
- Use **GitHub Actions**:
  - On push to `main`: build + deploy `latest`
  - On tag `v*`: build + deploy that version
- Host as a static site:
  - GitHub Pages (private/internal) **or** internal static hosting target (depending on enterprise constraints)

---

## 6. Information Architecture (Proposed)
### Top-level nav
- Home / Overview
- Getting Started
- Concepts
- How-to Guides
- Reference
  - API Reference (Stoplight Elements)
  - Events / AsyncAPI (future, optional)
- Release Notes (by version)

### Content conventions (AI-agent friendly)
- Prefer `.md` over `.mdx` (avoid React/JSX in docs).
- Use consistent frontmatter (only fields we define; no “creative” frontmatter).
- Keep navigation primarily filesystem-driven or a simple `mkdocs.yml` nav structure.

---

## 7. Technical Choices (Initial)
- MkDocs + Material theme
- Stoplight Elements embedded via local JS assets where feasible (avoid external CDN dependencies for internal reliability)
- OpenAPI spec format: OpenAPI 3.x in YAML
- CI: GitHub Actions
- Version deployment: `mike`

Notes:
- Stoplight Elements should be used in “docs-like” mode (readability-first).
- If we later need “Try it out”, we can evaluate CORS, auth, and whether to add Swagger UI as a secondary page.

---

## 8. Non-Functional Requirements (Internal Site; pragmatic)
### Security
- Site must be accessible only to authenticated internal users (enterprise controls).
- No secrets embedded in the site repo or published artifacts.
- Avoid pulling runtime assets from public CDNs (prefer vendored/local assets).

### Reliability & Maintainability
- Reproducible builds from CI.
- Clear folder conventions so changes are easy to review in PRs.
- Minimal custom code in the docs site.

### Performance
- Pages should load quickly on corporate networks.
- API reference pages should be usable without long blocking loads (avoid huge bundles; keep spec sizes reasonable).

### Usability
- Search enabled.
- Version selector clearly visible (Material + mike integration).
- API reference page visually consistent with site theme (as much as Stoplight Elements allows).

---

## 9. Acceptance Criteria
- A developer can run docs locally with one command and see:
  - MkDocs site
  - Embedded Stoplight API reference rendering the local OpenAPI YAML
- CI builds on GitHub Actions succeed and publish:
  - `latest` for main
  - a versioned snapshot for a tag (e.g., `v1.0.0`)
- Users can switch between versions and see the matching OpenAPI reference for that version.
- No runtime dependency on public CDNs for core rendering (docs and API reference assets are available locally).
- Navigation structure is clear and consistent across versions.

---

## 10. Risks & Mitigations
- **Large OpenAPI specs** causing slow render:
  - Mitigate by splitting specs, reducing examples, or using multiple service specs.
- **Theme consistency limitations** with Stoplight Elements:
  - Accept partial mismatch; keep page layout consistent; minimize custom styling.
- **Enterprise hosting constraints** for GitHub Pages:
  - Provide alternative deploy option (internal static hosting) in the plan.

---

## 11. Open Questions (to resolve in plan)
- Hosting target: GitHub Pages (Enterprise) vs internal static host.
- Version naming policy: full semver (`1.2.3`) vs minor (`1.2`) vs both.
- Single OpenAPI spec vs multiple specs (per service / bounded context).
- Source of OpenAPI:
  - generated during CI (Swashbuckle/NSwag) vs committed artifact
- Whether to include a secondary interactive console (Swagger UI) later.

---
