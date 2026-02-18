# Vendored Assets

<!-- markdownlint-disable MD013 -->

| Package | Version | Files vendored | Source URL | Vendored date | Vendor'd by |
|---------|---------|---------------|------------|---------------|-------------|
| `@stoplight/elements` | `9.0.15` | `web-components.min.js` | `https://unpkg.com/@stoplight/elements@9.0.15/web-components.min.js` | 2026-02-18 | tdouma |
| `@stoplight/elements` | `9.0.15` | `styles.min.css` | `https://unpkg.com/@stoplight/elements@9.0.15/styles.min.css` | 2026-02-18 | tdouma |

<!-- markdownlint-enable MD013 -->

## CDN URL audit result

Checked 2026-02-18: `styles.min.css` contains **no external CDN references**
(no `fonts.googleapis.com`, `fonts.gstatic.com`, `unpkg.com`, `cdn.jsdelivr.net`, or similar).
The API Reference page renders fully offline.

## Update procedure

1. Check for a new release of `@stoplight/elements` at <https://www.npmjs.com/package/@stoplight/elements>.
2. Download the new `web-components.min.js` and `styles.min.css` from unpkg (replace `9.0.15` with the new version).
3. Re-run the CDN URL audit on the new `styles.min.css`.
4. Update the version, source URL, and date in this table.
5. Verify the API Reference page renders correctly locally before opening a PR.
6. Require reviewer sign-off on the vendored file changes.
