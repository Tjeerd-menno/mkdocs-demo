# Contract: .github/workflows/docs-deploy.yml

**File**: `.github/workflows/docs-deploy.yml`
**Purpose**: Automated deployment. Publishes `dev` alias on every push to `main`; publishes `MAJOR.MINOR` version + `latest` alias on every `v*.*.*` tag push. Never runs on pull requests.

---

```yaml
name: Docs Deploy

on:
  push:
    branches: [main]
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"

permissions:
  contents: write      # mike writes to git history / local dir
  id-token: write      # OIDC if using federated identity instead of API token

concurrency:
  group: docs-deploy
  cancel-in-progress: false   # never cancel a deploy mid-flight

jobs:
  deploy:
    name: Build & Deploy
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure git identity
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      # ── Python toolchain ─────────────────────────────────────────────────
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install Python deps
        run: pip install -r requirements.txt

      # ── Resolve version identifier ────────────────────────────────────────
      - name: Resolve version
        id: version
        run: |
          if [[ "${{ github.ref }}" == refs/tags/* ]]; then
            TAG="${{ github.ref_name }}"               # e.g. v1.2.3
            VER="${TAG#v}"                              # strip leading v → 1.2.3
            ALIAS="${VER%.*}"                           # strip patch → 1.2
            echo "alias=${ALIAS}"   >> "$GITHUB_OUTPUT"
            echo "update_latest=true"  >> "$GITHUB_OUTPUT"
          else
            echo "alias=dev"        >> "$GITHUB_OUTPUT"
            echo "update_latest=false" >> "$GITHUB_OUTPUT"
          fi

      # ── Build versioned snapshot with mike ────────────────────────────────
      - name: Deploy (tag → MAJOR.MINOR + latest)
        if: steps.version.outputs.update_latest == 'true'
        run: |
          mike deploy \
            --no-redirect \
            --update-aliases \
            "${{ steps.version.outputs.alias }}" latest

      - name: Deploy (main → dev)
        if: steps.version.outputs.update_latest == 'false'
        run: |
          mike deploy \
            --no-redirect \
            --update-aliases \
            dev

      # ── Deploy to Azure Static Web Apps ───────────────────────────────────
      - name: Deploy to Azure SWA
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: upload
          app_location: "/"
          output_location: "site"
          skip_app_build: true    # mike already built; don't let SWA rebuild

      # ── Post-deploy smoke test ────────────────────────────────────────────
      - name: Smoke test
        env:
          TARGET_VERSION: ${{ steps.version.outputs.alias }}
          BASE_URL: ${{ vars.DOCS_BASE_URL }}   # set as repo variable (not secret)
        run: bash scripts/smoke-test.sh

```

---

## smoke-test.sh contract

**File**: `scripts/smoke-test.sh`
**Inputs** (env): `BASE_URL`, `TARGET_VERSION`
**Exit code**: 0 = all checks pass; 1 = any check fails

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL%/}"
VER="${TARGET_VERSION}"

check() {
  local url="$1"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$url")
  if [[ "$code" != "200" ]]; then
    echo "FAIL [$code]: $url" >&2
    return 1
  fi
  echo "OK   [$code]: $url"
}

echo "=== Smoke test: $BASE (version: $VER) ==="

check "${BASE}/versions.json"
check "${BASE}/${VER}/index.html"
check "${BASE}/${VER}/reference/api/index.html"
check "${BASE}/${VER}/reference/openapi/openapi.yaml"
check "${BASE}/${VER}/assets/vendor/web-components.min.js"

# Confirm version appears in versions.json
if ! curl -s "${BASE}/versions.json" | grep -q "\"${VER}\""; then
  echo "FAIL: version '${VER}' not found in versions.json" >&2
  exit 1
fi

echo "=== All smoke tests passed ==="
```

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| `fetch-depth: 0` | `mike` reads the existing git history to construct the full `versions.json` |
| `concurrency: cancel-in-progress: false` | A deploy must never be interrupted mid-flight; next deploy queues behind it |
| `skip_app_build: true` on SWA deploy | `mike` has already produced the complete `site/` output; SWA must not re-run a build step that would overwrite it |
| `DOCS_BASE_URL` as repo variable (not secret) | The site URL is not sensitive; using a variable (not a secret) makes it visible in workflow logs |
| Tag format `v[0-9]+.[0-9]+.[0-9]+` | Explicit regex prevents accidental triggers on pre-release tags (`v1.0.0-rc1`) |
| `--no-redirect` on `mike deploy` | Prevents mike from writing a redirect from the root to the default version (Azure SWA handles root redirect via `navigationFallback`) |
