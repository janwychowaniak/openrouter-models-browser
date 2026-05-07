# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for browsing and comparing AI models available through the OpenRouter API (`https://openrouter.ai/api/v1/models`). Distributed on PyPI as `ormodels`.

## Build Commands

```sh
# Set up dev environment
uv sync --all-groups

# Run the CLI from source
uv run ormodels <query>
uv run python -m ormodels <query>

# Examples
uv run ormodels -h                              # Show help
uv run ormodels claude                          # Search for Claude models
uv run ormodels anthropic/claude-3.5-sonnet     # Exact ID match (full YAML)
uv run ormodels claude gemini                   # Combine multiple searches

# Quality gates
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest

# Build artifacts
uv build
```

## CLI Interface

```sh
ormodels -h          # Print usage
ormodels ID          # Print full model entry if exact match found
ormodels PHRASE      # Build comparison table for all matches
ormodels A B         # Combine multiple searches (deduplicated)
```

## Table Output Columns

ID, NAME, CREATED (YYYY-MM-DD), CONTEXT_LENGTH (n | nk), MODALITY, TOKENIZER, PROMPT ($/1M), COMPLETION ($/1M), MAX_COMPL_TOKENS (n | nk)

## Search Behavior

Case-insensitive search across model ID, NAME, and MODALITY fields.

## Dependencies

Runtime:
- `requests` - API calls
- `tabulate` - Table formatting
- `pyyaml` - YAML output for exact matches

Dev (via `[dependency-groups]` in `pyproject.toml`):
- `ruff`, `mypy`, `pytest`, `types-requests`, `types-PyYAML`, `types-tabulate`

## Code Structure

```
src/ormodels/
├── __init__.py              - Exposes __version__ and main
├── __main__.py              - Enables `python -m ormodels`
└── cli.py                   - All CLI logic
    ├── Constants (API_URL, TABLE_HEADERS)
    ├── fetch_models()           - GET /api/v1/models with error handling
    ├── format_price_dollars()   - Convert per-token price to $/1M tokens
    ├── format_timestamp()       - Unix → YYYY-MM-DD
    ├── format_tokens()          - Dual format: "256000 | 256k"
    ├── format_description()     - Sentence-per-line with 2-space indent
    ├── search_models()          - Case-insensitive filter on id/name/modality
    ├── build_table_row()        - Extract 9 columns from model dict
    ├── print_full_model()       - YAML output with description first
    ├── print_comparison_table() - tabulate output
    ├── parse_args()             - argparse with positional QUERY
    └── main()                   - Entry point (registered as `ormodels`)

tests/
└── test_cli.py              - Unit tests for pure formatters + --help smoke test
```

Packaging:
- `pyproject.toml` (hatchling backend, src layout)
- `[project.scripts]` registers `ormodels = "ormodels.cli:main"`
- `.github/workflows/ci.yml` — lint, typecheck, tests on 3.11/3.12/3.13
- `.github/workflows/publish.yml` — PyPI Trusted Publishing on `v*` tags
- `.github/dependabot.yml` — weekly pip + actions security updates

## Development Notes

- Pricing values from API are strings representing cost per token (e.g., "0.00000025")
- Pricing display: `float(price) * 1_000_000` = dollars per 1M tokens
- The OpenRouter response is dynamic JSON, so internal types are `dict[str, Any]` at the boundary; do not over-specify with TypedDicts unless behavior depends on it.
- `mypy --strict` is enforced. Add type ignores narrowly (with reason) rather than loosening config.
