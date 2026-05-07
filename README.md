# ormodels

[![PyPI version](https://img.shields.io/pypi/v/openrouter-models-browser)](https://pypi.org/project/openrouter-models-browser/)
[![Python versions](https://img.shields.io/pypi/pyversions/openrouter-models-browser)](https://pypi.org/project/openrouter-models-browser/)

A CLI for browsing and comparing AI models from the [OpenRouter](https://openrouter.ai/) API.

## Installation

The command is `ormodels`; the PyPI distribution name is `openrouter-models-browser`.

```sh
# Recommended: isolated tool install
uv tool install openrouter-models-browser
# or
pipx install openrouter-models-browser

# Or as a regular dependency
pip install openrouter-models-browser
```

Requires Python 3.11+.

## Usage

```sh
# Show help
ormodels -h

# Search for models by name, ID, or modality
ormodels claude
ormodels gpt
ormodels "text->text"

# Combine multiple searches (results deduplicated)
ormodels claude gemini

# Get full details for an exact ID match
ormodels anthropic/claude-3.5-sonnet

# Equivalent module form
python -m ormodels claude
```

## Output

### Search results (table)

Comparison table with columns:
`ID`, `NAME`, `CREATED`, `CONTEXT_LENGTH`, `MODALITY`, `TOKENIZER`, `PROMPT`, `COMPLETION`, `MAX_COMPL_TOKENS`.

Pricing is shown in dollars per 1M tokens. Token counts use a dual format (e.g. `256000 | 256k`).

### Exact match (YAML)

When the query exactly matches a model ID, the full model entry is printed in YAML format with the description first, followed by prominent fields, then remaining details.

## Development

```sh
# Set up dev environment
uv sync --all-groups

# Run quality gates
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest

# Run the CLI from source
uv run ormodels claude

# Build distribution artifacts
uv build
```

Publishing is automated via the `Publish` GitHub Actions workflow on a `v*` tag, using PyPI Trusted Publishing (no API token required).

## License

MIT
