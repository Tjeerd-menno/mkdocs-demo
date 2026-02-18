# How-To Guides

Task-focused guides for common documentation and engineering workflows.

## Contributing documentation

Before opening a PR with documentation changes, verify your changes locally:

1. Install dependencies as described in [Installation](../getting-started/installation.md).
2. Run `mkdocs serve` and review your changes in a browser at `http://localhost:8000`.
3. Run `mkdocs build --strict` to catch broken links and warnings before pushing.
4. Run `npx markdownlint-cli2 "docs/**/*.md"` to validate the markdown style rules.

Once all checks pass locally, push your branch and open a pull request. CI will run the same
checks automatically before your PR can be merged.

## Publishing a new release

Releases are published automatically when a `v<MAJOR>.<MINOR>.<PATCH>` tag is pushed to the
repository. See the [Quickstart guide](../getting-started/quickstart.md) for the full publish workflow.
