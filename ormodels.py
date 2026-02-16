#!/usr/bin/env python3
"""OpenRouter Models Browser - CLI tool for browsing and comparing AI models."""

import argparse
import json
import re
import sys
from datetime import datetime

import requests
import yaml
from tabulate import tabulate

# Constants
API_URL = "https://openrouter.ai/api/v1/models"
TABLE_HEADERS = [
    "ID",
    "NAME",
    "CREATED",
    "CONTEXT_LENGTH",
    "MODALITY",
    "TOKENIZER",
    "PROMPT",
    "COMPLETION",
    "MAX_COMPL_TOKENS",
]


def fetch_models():
    """Fetch models from OpenRouter API."""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.Timeout:
        print("Error: Request timed out", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch models: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error: Invalid API response: {e}", file=sys.stderr)
        sys.exit(1)


def format_price_dollars(price_str):
    """Convert per-token price string to dollars per 1M tokens.

    API gives per-token price in dollars (e.g., "0.00000025").
    Convert to dollars per 1M tokens: float(price) * 1_000_000
    """
    if not price_str:
        return "N/A"
    try:
        price = float(price_str)
        dollars_per_million = price * 1_000_000
        return f"${dollars_per_million:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def format_timestamp(unix_ts):
    """Convert Unix timestamp to YYYY-MM-DD format."""
    if not unix_ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "N/A"


def format_tokens(count):
    """Format token count as 'NUMBER | NUMBERk' for easy copy and comprehension."""
    if not count:
        return "N/A"
    try:
        count = int(count)
        k_value = count // 1000
        return f"{count} | {k_value}k"
    except (ValueError, TypeError):
        return "N/A"


def search_models(models, query):
    """Case-insensitive search across id, name, and modality fields."""
    query_lower = query.lower()
    matches = []
    for model in models:
        model_id = model.get("id", "").lower()
        name = model.get("name", "").lower()
        modality = model.get("architecture", {}).get("modality", "").lower()

        if query_lower in model_id or query_lower in name or query_lower in modality:
            matches.append(model)
    return matches


def build_table_row(model):
    """Extract 9 columns from model dict for table display."""
    architecture = model.get("architecture", {})
    pricing = model.get("pricing", {})
    top_provider = model.get("top_provider", {})

    return [
        model.get("id", "N/A"),
        model.get("name", "N/A"),
        format_timestamp(model.get("created")),
        format_tokens(model.get("context_length")),
        architecture.get("modality", "N/A"),
        architecture.get("tokenizer", "N/A"),
        format_price_dollars(pricing.get("prompt")),
        format_price_dollars(pricing.get("completion")),
        format_tokens(top_provider.get("max_completion_tokens")),
    ]


def format_description(desc):
    """Format description with sentence-per-line, 2-space indent."""
    if not desc:
        return "  (no description)"
    # Split on sentence boundaries (. followed by space or newline)
    sentences = re.split(r'\.(?:\s+|\n)', desc.strip())
    lines = []
    for s in sentences:
        s = s.strip()
        if s:
            # Add period back if not ending with punctuation
            if not s.endswith(('.', '!', '?')):
                s += '.'
            lines.append(f"  {s}")
    return '\n'.join(lines)


def print_full_model(model):
    """Print full model entry in YAML-ish format with description first."""
    model = model.copy()

    # Extract and format description
    desc = model.pop("description", "")
    print(f"\ndescription:\n{format_description(desc)}\n")

    # Prominent fields with aligned colons
    prominent = ["name", "id", "canonical_slug", "hugging_face_id", "created", "context_length"]
    max_len = max(len(k) for k in prominent)

    for key in prominent:
        value = model.pop(key, None)
        if value == "":
            value = '""'
        elif value is None:
            value = "null"
        print(f"{key}:{' ' * (max_len - len(key))}  {value}")

    print()

    # Rest as YAML
    print(yaml.dump(model, default_flow_style=False, allow_unicode=True, sort_keys=False), end="")

    print()


def print_comparison_table(models):
    """Print models as a formatted comparison table."""
    rows = [build_table_row(model) for model in models]
    print(tabulate(rows, headers=TABLE_HEADERS, tablefmt="simple"))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Browse and compare AI models from OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s claude              Search for models matching "claude"
  %(prog)s openai/gpt-4        Exact ID match shows full YAML
  %(prog)s "text->text"        Search by modality
  %(prog)s claude gemini       Combine multiple searches

Pricing is shown in dollars per 1M tokens.
        """,
    )
    parser.add_argument(
        "query",
        nargs="*",
        metavar="QUERY",
        help="Search for models by ID, name, or modality. Exact ID match (single query) shows full YAML.",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if not args.query:
        print("Error: No search query provided.", file=sys.stderr)
        sys.exit(1)

    models = fetch_models()

    # Single query: check for exact ID match first
    if len(args.query) == 1:
        query = args.query[0]
        for model in models:
            if model.get("id") == query:
                print_full_model(model)
                return

    # Collect matches from all queries (deduplicated by id)
    seen_ids = set()
    all_matches = []
    for query in args.query:
        for match in search_models(models, query):
            model_id = match.get("id")
            if model_id not in seen_ids:
                seen_ids.add(model_id)
                all_matches.append(match)

    if not all_matches:
        queries = ", ".join(f"'{q}'" for q in args.query)
        print(f"No models found matching {queries}", file=sys.stderr)
        sys.exit(1)

    queries = ", ".join(f"'{q}'" for q in args.query)
    print(f"Found {len(all_matches)} model(s) matching {queries}:\n")
    print_comparison_table(all_matches)


if __name__ == "__main__":
    main()
