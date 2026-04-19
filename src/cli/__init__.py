"""CLI entrypoint for NOX.

This module re-exports the `run_console` entrypoint from the
`.console` module so callers can import it as:

	from src.cli import run_console

It also allows running the console directly with ``python -m src.cli``
when the package is on `PYTHONPATH`.
"""
from .console import run_console

__all__ = ["run_console"]


if __name__ == "__main__":
	run_console()
