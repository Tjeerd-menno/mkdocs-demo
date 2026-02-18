"""
MkDocs hook: validate_openapi.py
Raises SystemExit if docs/reference/openapi/openapi.yaml is absent at build time.
Satisfies edge case: missing OpenAPI YAML must fail the build with a clear error.
"""
import os
from mkdocs.config.defaults import MkDocsConfig


def on_startup(command: str, dirty: bool) -> None:
    """Called once when mkdocs starts (build, serve, gh-deploy)."""
    _check_openapi()


def on_config(config: MkDocsConfig) -> MkDocsConfig:
    """Fallback check if on_startup is not triggered in older mkdocs versions."""
    _check_openapi()
    return config


def _check_openapi() -> None:
    oas_path = os.path.join("docs", "reference", "openapi", "openapi.yaml")
    if not os.path.isfile(oas_path):
        raise SystemExit(
            f"\n[validate_openapi] ERROR: Required OpenAPI spec not found at '{oas_path}'.\n"
            "Create docs/reference/openapi/openapi.yaml before building the site.\n"
            "See docs/getting-started/quickstart.md for authoring guidance."
        )
