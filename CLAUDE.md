# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for browsing and comparing AI models available through the OpenRouter API (`https://openrouter.ai/api/v1/models`).

## Build Commands

```sh
# Install dependencies
pip install -r requirements.txt

# Run the tool
./ormodels.py -f <query>

# Examples
./ormodels.py -h                        # Show help
./ormodels.py -f claude                 # Search for Claude models
./ormodels.py -f anthropic/claude-3.5-sonnet  # Exact ID match (full JSON)
```

## CLI Interface

```sh
./ormodels.py -h          # Print usage
./ormodels.py -f ID       # Print full model entry if exact match found
./ormodels.py -f PHRASE   # Build comparison table for all matches
```

## Table Output Columns

ID, NAME, CREATED (YYYY-MM-DD), CONTEXT_LENGTH, MODALITY, TOKENIZER, PROMPT (cents/1M), COMPLETION (cents/1M), MAX_COMPL_TOKENS

## Search Behavior

Case-insensitive search across model ID, NAME, and MODALITY fields.

## Dependencies

- `requests` - API calls
- `tabulate` - Table formatting

## Code Structure

```
ormodels.py
├── Constants (API_URL, TABLE_HEADERS)
├── fetch_models()           - GET /api/v1/models with error handling
├── format_price_cents()     - Convert per-token price to cents/1M tokens
├── format_timestamp()       - Unix → YYYY-MM-DD
├── search_models()          - Case-insensitive filter on id/name/modality
├── build_table_row()        - Extract 9 columns from model dict
├── print_full_model()       - json.dumps with indent
├── print_comparison_table() - tabulate output
├── parse_args()             - argparse with -f/--find
└── main()                   - Entry point
```

## Development Notes

- Pricing values from API are strings representing cost per token (e.g., "0.0000003")
- Pricing display: `float(price) * 100_000_000` = cents per 1M tokens
