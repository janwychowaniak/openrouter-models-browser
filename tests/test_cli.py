"""Tests for ormodels CLI."""

from __future__ import annotations

import subprocess
import sys

from ormodels.cli import (
    build_table_row,
    format_description,
    format_price_dollars,
    format_timestamp,
    format_tokens,
    search_models,
)


def test_format_tokens_dual_format() -> None:
    assert format_tokens(256000) == "256000 | 256k"
    assert format_tokens("128000") == "128000 | 128k"
    assert format_tokens(0) == "N/A"
    assert format_tokens(None) == "N/A"
    assert format_tokens("not-a-number") == "N/A"


def test_format_price_dollars_handles_missing() -> None:
    assert format_price_dollars("0.00000025") == "$0.25"
    assert format_price_dollars("0.000003") == "$3.00"
    assert format_price_dollars(None) == "N/A"
    assert format_price_dollars("") == "N/A"
    assert format_price_dollars("garbage") == "N/A"


def test_format_timestamp_invalid() -> None:
    assert format_timestamp(0) == "N/A"
    assert format_timestamp(None) == "N/A"
    # 2024-01-01 00:00:00 UTC = 1704067200; result is timezone-dependent
    # so just check the shape rather than exact value
    result = format_timestamp(1704067200)
    assert len(result) == 10 and result[4] == "-" and result[7] == "-"


def test_format_description_empty() -> None:
    assert format_description("") == "  (no description)"
    assert format_description(None) == "  (no description)"


def test_format_description_splits_sentences() -> None:
    desc = "First sentence. Second sentence. Third one"
    out = format_description(desc)
    assert out == "  First sentence.\n  Second sentence.\n  Third one."


def test_search_models_case_insensitive() -> None:
    models = [
        {"id": "anthropic/claude-3", "name": "Claude 3", "architecture": {"modality": "text"}},
        {"id": "openai/gpt-4", "name": "GPT-4", "architecture": {"modality": "text"}},
        {"id": "google/gemini", "name": "Gemini", "architecture": {"modality": "image->text"}},
    ]
    assert len(search_models(models, "CLAUDE")) == 1
    assert len(search_models(models, "gpt")) == 1
    assert len(search_models(models, "image")) == 1
    assert len(search_models(models, "nope")) == 0


def test_build_table_row_handles_missing_fields() -> None:
    model = {"id": "x/y", "name": "Y"}
    row = build_table_row(model)
    assert len(row) == 9
    assert row[0] == "x/y"
    assert row[1] == "Y"
    assert all(cell == "N/A" for cell in row[2:])


def test_help_runs() -> None:
    """Smoke test: `python -m ormodels --help` exits 0."""
    result = subprocess.run(
        [sys.executable, "-m", "ormodels", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "Browse and compare AI models" in result.stdout
