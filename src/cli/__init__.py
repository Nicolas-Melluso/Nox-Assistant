"""CLI entrypoint for NOX.

This module re-exports the `run_console` entrypoint from the
`.console` module so callers can import it as:

	from src.cli import run_console

It also allows running the console directly with ``python -m src.cli``
when the package is on `PYTHONPATH`.
"""
import sys
import os
# Añadir src al sys.path si no está
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
	sys.path.insert(0, src_path)
from .runner import run_console
from .console import main

__all__ = ["run_console", "main"]

if __name__ == "__main__":
    main()
