# Concepts

This section explains the *why* behind the key design decisions for this documentation site.
Understanding these concepts will help you author better documentation and avoid common mistakes.

## Why versioned docs?

Product documentation must match the version a user is running. `mike` publishes immutable snapshots
keyed to `MAJOR.MINOR` release identifiers. Corrections to an existing release require a patch release —
not a retroactive edit.

## Why vendor all assets?

This site has no runtime dependency on public CDNs. All JavaScript and CSS required by the API reference
(Stoplight Elements) are committed under `docs/assets/vendor/`. This ensures the site is fully
accessible on an air-gapped corporate network.

## Why OpenAPI in the repo?

The API specification is hand-authored and committed alongside the code it describes. This makes the spec
a first-class artifact of every release, versioned, reviewable, and rendered in the docs at the same
version tag.

## Why Entra ID at the platform layer?

Authentication is enforced by Azure Static Web Apps before any page is served. The docs site itself
contains zero auth code. This keeps the site simple and removes an entire class of auth-related bugs.
