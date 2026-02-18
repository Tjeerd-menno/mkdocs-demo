# Contract: .github/workflows/docs-ci.yml

**File**: `.github/workflows/docs-ci.yml`
**Purpose**: Pull-request quality gate. Runs all blocking checks. Never deploys. All jobs must pass before merging to `main`.

---

```yaml
name: Docs CI

on:
  pull_request:
    branches: [main]

concurrency:
  group: docs-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  gate:
    name: Quality Gates
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0      # mike needs full history; also needed for gitleaks

      # ── Secret scanning ──────────────────────────────────────────────────
      - name: Secret scan (gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # ── Node toolchain ───────────────────────────────────────────────────
      - name: Set up Node 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm

      - name: Install Node deps
        run: npm ci

      # ── Markdown lint ────────────────────────────────────────────────────
      - name: Markdown lint
        run: npx markdownlint-cli2 "docs/**/*.md"

      # ── OpenAPI validation ───────────────────────────────────────────────
      - name: Validate OpenAPI spec(s)
        run: npx vacuum lint docs/reference/openapi/*.yaml

      # ── Python toolchain ─────────────────────────────────────────────────
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install Python deps
        run: pip install -r requirements.txt

      # ── Docs build (strict) ──────────────────────────────────────────────
      - name: Build docs (strict)
        run: mkdocs build --strict

      # ── Internal link check ──────────────────────────────────────────────
      - name: Internal link check
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --offline
            --include-fragments
            --no-progress
            'site/**/*.html'
          fail: true

      # ── External link check (warning only) ───────────────────────────────
      - name: External link check (warning)
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --no-progress
            --exclude-path site/assets
            'site/**/*.html'
          fail: false          # warning only; does not block merge
```

---

## Gate definitions

| Gate | Tool | Failure action |
|------|------|----------------|
| Secret scan | `gitleaks-action@v2` | Block merge |
| Markdown lint | `markdownlint-cli2` | Block merge |
| OpenAPI validation | `vacuum` | Block merge |
| Docs build | `mkdocs build --strict` | Block merge |
| Internal link check | `lychee --offline` | Block merge |
| External link check | `lychee` | Warning only; triage within 1 sprint |

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| `fetch-depth: 0` | `gitleaks` scans full history; `mike` needs history for `versions.json` |
| `concurrency: cancel-in-progress` | Avoids stacking gate runs on rapid pushes to the same PR branch |
| `lychee --offline` for internal check | Checks HTML output only against local file system; fast and deterministic |
| External check non-blocking | External URLs can break transiently; blocking on transient external failures slows developer workflow inappropriately |
| Two separate lychee steps | Keeps failure signals clear: internal link failures are the author's responsibility; external are tracked separately |
