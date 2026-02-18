# Contract: mkdocs.yml

**File**: `/mkdocs.yml`
**Purpose**: Single MkDocs configuration. All settings are mandatory unless marked optional.

---

```yaml
# mkdocs.yml
site_name: "Internal Product Docs"
site_description: "Internal engineering documentation — not for public distribution"
# site_url: set in CI deploy step via --config-file override or environment variable; leave empty here
docs_dir: docs
site_dir: site

theme:
  name: material
  language: en
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs          # top-level sections as header tabs
    - navigation.sections      # expand subsections in left sidebar
    - navigation.indexes       # folder index.md pages
    - navigation.top           # back-to-top button
    - navigation.footer        # prev / next links
    - search.highlight
    - search.suggest
    - content.code.copy
    - content.tabs.link

extra:
  version:
    provider: mike
    default: latest            # version selector default alias

extra_css:
  - assets/stylesheets/extra.css
  - assets/vendor/styles.min.css

extra_javascript:
  - assets/vendor/web-components.min.js

plugins:
  - search
  - mike:
      alias_type: symlink
      redirect_template: null
      deploy_prefix: ""
      canonical_version: null
      version_selector: true

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
      title: On this page

nav:
  - Home: index.md
  - Getting Started:
      - getting-started/index.md
      - Installation: getting-started/installation.md
      - Quickstart: getting-started/quickstart.md
  - Concepts:
      - concepts/index.md
  - How-To Guides:
      - how-to/index.md
  - Reference:
      - API Reference: reference/api.md
  - Release Notes:
      - release-notes/index.md
```

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| No `social`, `analytics`, `git-revision-date` plugins | No external service dependencies; internal site |
| No `custom_dir` for theme overrides | Minimise custom code per constitution; add only if strictly required |
| `extra.version.default: latest` | Version selector defaults to the most recently published stable tag |
| `site_url` left empty | Set by CI to the Azure SWA hostname at deploy time; avoids hardcoding |
| Dark/light toggle | Low-effort UX improvement; built into Material; no custom code |
