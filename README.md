# openrouter-models-browser

A CLI tool for browsing and comparing AI models available through the OpenRouter API.

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
# Show help
./ormodels.py -h

# Search for models by name, ID, or modality
./ormodels.py claude
./ormodels.py gpt
./ormodels.py "text->text"

# Combine multiple searches
./ormodels.py claude gemini

# Get full details for exact ID match
./ormodels.py anthropic/claude-3.5-sonnet
```

## Output

### Search Results (Table)

When searching, displays a comparison table with columns:
- ID, NAME, CREATED, CONTEXT_LENGTH, MODALITY, TOKENIZER, PROMPT, COMPLETION, MAX_COMPL_TOKENS

Pricing is shown in dollars per 1M tokens. Token counts show dual format (e.g., `256000 | 256k`).

### Exact Match (YAML)

When an exact model ID is provided, outputs the full model entry in YAML format with description first, followed by prominent fields, then remaining details.

## Dependencies

- `requests` - API calls
- `tabulate` - Table formatting
- `pyyaml` - YAML output
