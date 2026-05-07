"""OpenRouter Models Browser package."""

from importlib.metadata import PackageNotFoundError, version

from ormodels.cli import main

try:
    __version__ = version("ormodels")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__", "main"]
