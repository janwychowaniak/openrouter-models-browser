#!/usr/bin/env python3
"""OpenRouter Models Browser - CLI tool for browsing and comparing AI models."""

import argparse
import json
import sys
from datetime import datetime

import requests
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


def format_price_cents(price_str):
    """Convert per-token price string to cents per 1M tokens.

    API gives per-token price in dollars (e.g., "0.0000003").
    Convert to cents per 1M tokens: float(price) * 100_000_000
    """
    if not price_str:
        return "N/A"
    try:
        price = float(price_str)
        cents_per_million = price * 100_000_000
        return f"${cents_per_million:.2f}"
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
        model.get("context_length", "N/A"),
        architecture.get("modality", "N/A"),
        architecture.get("tokenizer", "N/A"),
        format_price_cents(pricing.get("prompt")),
        format_price_cents(pricing.get("completion")),
        top_provider.get("max_completion_tokens", "N/A"),
    ]


def print_full_model(model):
    """Print full model entry as formatted JSON."""
    print(json.dumps(model, indent=2))


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
  %(prog)s -f claude           Search for models matching "claude"
  %(prog)s -f openai/gpt-4     Exact ID match shows full JSON
  %(prog)s -f "text->text"     Search by modality

Pricing is shown in cents per 1M tokens.
        """,
    )
    parser.add_argument(
        "-f",
        "--find",
        metavar="QUERY",
        help="Search for models by ID, name, or modality. Exact ID match shows full JSON.",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if not args.find:
        parse_args()  # This will trigger help display
        print("Error: No search query provided. Use -f/--find to search.", file=sys.stderr)
        sys.exit(1)

    models = fetch_models()

    # Check for exact ID match first
    exact_match = None
    for model in models:
        if model.get("id") == args.find:
            exact_match = model
            break

    if exact_match:
        print_full_model(exact_match)
        return

    # Otherwise, perform search
    matches = search_models(models, args.find)

    if not matches:
        print(f"No models found matching '{args.find}'", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(matches)} model(s) matching '{args.find}':\n")
    print_comparison_table(matches)


if __name__ == "__main__":
    main()
