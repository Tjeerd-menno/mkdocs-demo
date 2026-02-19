# Quickstart — Authoring Guide

This guide covers everything you need to know to write and publish documentation on this site.

## Frontmatter rules

Every Markdown file MAY start with a YAML frontmatter block. Only three keys are permitted:

```yaml
---
title: Page Title (optional — overrides nav display name)
description: Brief description for search previews (max 160 chars)
hide:
  - toc        # hides the table of contents
  - navigation # hides the left sidebar
---
```

Any other frontmatter key will cause the build to fail. This is enforced by the
`hooks/validate_frontmatter.py` hook.

## Heading rules

- Every page MUST have exactly one H1 heading.
- Heading levels MUST NOT skip (e.g., H1 → H3 is not permitted).
- Headings at the same section level MUST be unique within each document section
  (siblings, not across the whole document).

## Relative links only

All cross-references between pages MUST use relative Markdown links:

```markdown
✓ [How-To Guides](../how-to/index.md)
✓ [API Reference](../reference/api.md)
✗ [Concepts](/concepts/index.md)           ← absolute paths are forbidden
✗ [Site](https://docs.example.internal/)    ← absolute internal URLs are forbidden
```

## No placeholder text

Published pages MUST NOT contain placeholder text such as `TBD`, `TODO`, or `Coming soon`.
Complete the content before pushing. If content is genuinely incomplete, track it in the issue
tracker and link to the issue instead of writing a placeholder.

## Line length

Markdown prose MUST NOT exceed **120 characters per line**. Code blocks allow up to 200 characters.
Table cells are exempt. Use `\` at the end of a line or break sentences across lines.

## OpenAPI YAML authoring

The API specification lives at `docs/reference/openapi/openapi.yaml`.

### Per-endpoint requirements (from data-model.md)

| Item | Required |
|------|----------|
| `summary` or `description` | Yes |
| All path/query/header parameters with type, description, example | Yes |
| Request body with at least one example | Conditional (if operation accepts a body) |
| All response codes with schemas | Yes (min: one 2xx, one 4xx or 5xx) |
| Error response schema | Yes (at least one error response with a schema) |

### Internal operations

Mark engineer-only operations with `x-internal: true`. The Stoplight Elements component
will hide them from the rendered API reference:

```yaml
  /internal/debug:
    get:
      x-internal: true
      summary: Internal debug endpoint
```

### Validation

Run before pushing:

```bash
pnpm run lint:oas
```

A 100/100 quality score is the target.

## Vendored asset update procedure

To update `@stoplight/elements` to a newer version:

1. Check [npmjs.com/@stoplight/elements](https://www.npmjs.com/package/@stoplight/elements)
   for the latest release.
2. Download the new `web-components.min.js` and `styles.min.css` from unpkg:

   ```bash
   # Replace 9.0.15 with the new version
   curl -o docs/assets/vendor/web-components.min.js \
     https://unpkg.com/@stoplight/elements@9.0.15/web-components.min.js
   curl -o docs/assets/vendor/styles.min.css \
     https://unpkg.com/@stoplight/elements@9.0.15/styles.min.css
   ```

3. Run the CDN URL audit:

   ```bash
   grep -E "(unpkg\.com|cdn\.jsdelivr\.net|fonts\.googleapis\.com)" \
     docs/assets/vendor/styles.min.css
   ```

   This must return **no output**.

4. Update `docs/assets/vendor/VENDOR-VERSIONS.md` with the new version, URL, and date.
5. Run `mkdocs serve` and verify the API Reference page renders correctly.
6. Include the vendored file changes in your PR for reviewer sign-off.

## Publish commands

See [Installation](installation.md) for the full publish command reference.

In brief:

```bash
# Publish main branch as dev (CI runs this automatically on push to main)
mike deploy dev

# Publish a tagged release (CI runs this automatically on a v*.*.* tag push)
mike deploy --update-aliases 1.0 latest
```

## gitleaks pre-commit hook

The `gitleaks` pre-commit hook scans staged files for secrets before every `git commit`.

### When it fires

If gitleaks detects a potential secret, you will see output similar to:

```text
WARN[...] leaks found: 1
    Finding:     api_key = "sk-abc123..."
    Secret:      sk-abc123...
    RuleID:      generic-api-key
    File:        docs/reference/api.md
    Line:        42
```

The commit is blocked until the issue is resolved.

### How to resolve

1. **Remove the secret** from the file. Never commit real credentials to the repository.
2. If the file contained the secret in a code example, replace it with a placeholder:
   `<YOUR_API_KEY>` or `sk-REPLACE_ME`.
3. Retry `git commit`.

### False positives

If gitleaks flags content that is not actually a secret (e.g., an example placeholder that
looks like a key), add a `# gitleaks:allow` comment on the same line:

```yaml
api_key: sk-REPLACE_ME  # gitleaks:allow
```

Document the suppression in your PR description so reviewers can verify it.
