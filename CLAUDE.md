# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for browsing and comparing AI models available through the OpenRouter API (`https://openrouter.ai/api/v1/models`).

## Build Commands

```sh
# Install dependencies
pip install -r requirements.txt

# Run the tool
./ormodels.py <query>

# Examples
./ormodels.py -h                       # Show help
./ormodels.py claude                   # Search for Claude models
./ormodels.py anthropic/claude-3.5-sonnet  # Exact ID match (full YAML)
./ormodels.py claude gemini            # Combine multiple searches
```

## CLI Interface

```sh
./ormodels.py -h          # Print usage
./ormodels.py ID          # Print full model entry if exact match found
./ormodels.py PHRASE      # Build comparison table for all matches
./ormodels.py A B         # Combine multiple searches (deduplicated)
```

## Table Output Columns

ID, NAME, CREATED (YYYY-MM-DD), CONTEXT_LENGTH (n | nk), MODALITY, TOKENIZER, PROMPT ($/1M), COMPLETION ($/1M), MAX_COMPL_TOKENS (n | nk)

## Search Behavior

Case-insensitive search across model ID, NAME, and MODALITY fields.

## Dependencies

- `requests` - API calls
- `tabulate` - Table formatting
- `pyyaml` - YAML output for exact matches

## Code Structure

```
ormodels.py
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
└── main()                   - Entry point
```

## Development Notes

- Pricing values from API are strings representing cost per token (e.g., "0.00000025")
- Pricing display: `float(price) * 1_000_000` = dollars per 1M tokens
