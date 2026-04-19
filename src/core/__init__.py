"""Core motor package for NOX.

This package exposes the core engine API used by other modules.
Keep this module minimal: only package-level documentation and re-exports
so callers can import the engine as `from src.core import CoreEngine`.
"""

from .engine import CoreEngine

__all__ = ["CoreEngine"]
