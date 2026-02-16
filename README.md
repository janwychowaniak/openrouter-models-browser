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
./ormodels.py -f claude
./ormodels.py -f gpt
./ormodels.py -f "text->text"

# Combine multiple searches
./ormodels.py -f claude -f gemini

# Get full JSON for exact ID match
./ormodels.py -f anthropic/claude-3.5-sonnet
```

## Output

### Search Results (Table)

When searching, displays a comparison table with columns:
- ID, NAME, CREATED, CONTEXT_LENGTH, MODALITY, TOKENIZER, PROMPT, COMPLETION, MAX_COMPL_TOKENS

Pricing is shown in dollars per 1M tokens.

### Exact Match (JSON)

When an exact model ID is provided, outputs the full model entry as formatted JSON.

## Dependencies

- `requests` - API calls
- `tabulate` - Table formatting
