# Contract: .markdownlint.json

**File**: `/.markdownlint.json`
**Purpose**: Authoritative markdownlint ruleset. All rules are applied on `docs/**/*.md` in CI and on save in VS Code. No rule may be suppressed without a documented justification committed alongside the suppression.

---

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "heading_line_length": 120,
    "code_block_line_length": 200,
    "tables": false
  },
  "MD024": {
    "siblings_only": true
  },
  "MD033": {
    "allowed_elements": ["elements-api"]
  },
  "MD041": true,
  "MD007": {
    "indent": 2
  }
}
```

---

## Rule decisions

| Rule | Setting | Rationale |
|------|---------|-----------|
| `default: true` | All rules on | Start strict; suppress only with justification |
| `MD013` line length | 120 chars | Generous enough for code references; avoids mid-sentence wrapping in Markdown prose |
| `MD013.tables: false` | Off for tables | Table cells cannot be wrapped; disabling for tables is idiomatic |
| `MD024 siblings_only` | True | Allows repeated headings in different sections (e.g., "Overview" in multiple how-to pages) |
| `MD033 allowed_elements` | `["elements-api"]` | Allows the Stoplight Elements `<elements-api>` custom element tag on `reference/api.md`; all other HTML is forbidden |
| `MD041` | True | Every file must begin with a top-level heading |
| `MD007` indent | 2 | Standard unordered list indent |
