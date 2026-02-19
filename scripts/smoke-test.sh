#!/usr/bin/env bash
# smoke-test.sh — post-deploy health checks
# Usage: DOCS_BASE_URL=https://your-swa.azurestaticapps.net bash scripts/smoke-test.sh
# TARGET_VERSION env var is set by the deploy workflow (e.g. "1.0" or "dev")
set -euo pipefail

BASE_URL="${DOCS_BASE_URL:?DOCS_BASE_URL must be set}"
VERSION="${TARGET_VERSION:-dev}"

check() {
  local url="$1"
  local code
  code=$(curl --silent --output /dev/null --write-out "%{http_code}" --max-time 10 "$url")
  if [[ "$code" -ge 400 ]] || [[ "$code" == "000" ]]; then
    echo "FAIL [$code]: $url" >&2
    return 1
  fi
  echo "OK   [$code]: $url"
}

FAILED=0

check "${BASE_URL}/versions.json"                                          || FAILED=1
check "${BASE_URL}/${VERSION}/index.html"                                  || FAILED=1
check "${BASE_URL}/${VERSION}/reference/api/index.html"                   || FAILED=1
check "${BASE_URL}/${VERSION}/reference/openapi/openapi.yaml"             || FAILED=1
check "${BASE_URL}/${VERSION}/assets/vendor/web-components.min.js"        || FAILED=1

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "Smoke test FAILED — one or more checks returned non-200." >&2
  exit 1
fi

echo ""
echo "All smoke test checks passed."
