# Release Notes

## v1.0

**Released**: 2026-02-18
**Git tag**: v1.0.0

## NEW

- Initial internal documentation site powered by MkDocs Material.
- Versioned publishing via `mike` — version selector in site header.
- API Reference page rendering the committed OpenAPI specification via Stoplight Elements (vendored, no CDN).
- CI quality gates: markdownlint, strict build, internal link check, OpenAPI validation, secret scan.
- Azure Static Web Apps deployment protected by Entra ID at the platform layer.
- Post-deploy smoke test verifying page and asset availability on every publish.
