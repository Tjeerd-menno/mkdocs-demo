"""
MkDocs hook: validate_frontmatter.py
Validates that every Markdown page uses only permitted frontmatter keys.
Permitted keys: title, description, hide  (per data-model.md and FR-003)
Unknown keys cause the build to fail with a descriptive error.
"""
import re
from typing import Optional
import yaml
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

PERMITTED_KEYS = {"title", "description", "hide"}
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def on_page_read_source(page: Page, config: MkDocsConfig) -> Optional[str]:
    """Called each time MkDocs reads a page's source Markdown."""
    # page.file.abs_src_path may be None for virtual pages
    src_path = getattr(page.file, "abs_src_path", None) or page.file.src_path
    try:
        with open(src_path, encoding="utf-8") as fh:
            source = fh.read()
    except (OSError, TypeError):
        return None  # let MkDocs handle the error itself

    match = _FRONTMATTER_RE.match(source)
    if not match:
        return None  # no frontmatter — nothing to validate

    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise SystemExit(
            f"\n[validate_frontmatter] ERROR: YAML parse error in frontmatter of '{src_path}':\n{exc}"
        ) from exc

    unknown = set(data.keys()) - PERMITTED_KEYS
    if unknown:
        raise SystemExit(
            f"\n[validate_frontmatter] ERROR: Unknown frontmatter key(s) in '{src_path}': "
            f"{sorted(unknown)}\n"
            f"Permitted keys are: {sorted(PERMITTED_KEYS)}\n"
            "See docs/getting-started/quickstart.md to add a new key via an authoring-guide amendment."
        )
    return None  # return None to let MkDocs load the file normally
