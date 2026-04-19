import pytest
import sys
import os

# Agregar src/ al sys.path para que los imports funcionen
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.engine import CoreEngine

@pytest.fixture
def engine():
    """Fixture que retorna una instancia de CoreEngine para los tests."""
    return CoreEngine()
