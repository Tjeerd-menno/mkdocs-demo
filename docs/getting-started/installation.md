# Installation

This guide covers the full developer setup from `git clone` to a running local preview.

## Prerequisites

- **Python 3.12** ([python.org](https://www.python.org/downloads/))
- **Node 20** ([nodejs.org](https://nodejs.org/))
- **pre-commit** (`pip install pre-commit`)

## Setup

```bash
git clone <repository-url>
cd <repository-name>
pip install -r requirements.txt
npm ci
pre-commit install
```

## Local preview

```bash
mkdocs serve
```

The site is accessible at `http://localhost:8000`. Changes to Markdown files trigger a live reload.

## Build (with strict checks)

```bash
mkdocs build --strict
```

Builds to `site/`. With `--strict`, all warnings become errors — fix them before pushing.

## Lint Markdown

```bash
npx markdownlint-cli2 "docs/**/*.md"
```

## Lint OpenAPI spec

```bash
npx vacuum lint docs/reference/openapi/*.yaml
```

## Local versioned preview (mike)

```bash
# Deploy main branch as dev
mike deploy dev

# Deploy a tagged release as a MAJOR.MINOR version and set as latest
mike deploy --update-aliases 1.0 latest

# Serve the versioned site locally
mike serve
```

See `mike --help` for additional options.

## Pre-commit hook (gitleaks)

The `gitleaks` pre-commit hook scans staged files for secrets before each commit.
If it fires, remove or vault the detected secret and retry `git commit`.
For a false positive, add `# gitleaks:allow` as an inline comment on the offending line
and document the suppression in the PR description.
