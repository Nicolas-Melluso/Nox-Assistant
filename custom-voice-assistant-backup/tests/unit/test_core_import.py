def test_core_import():
    # Ensure repo root is on sys.path when tests are run from different CWDs
    import sys
    import os

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Verify that CoreEngine is re-exported from src.core
    from src.core import CoreEngine

    assert callable(CoreEngine)
