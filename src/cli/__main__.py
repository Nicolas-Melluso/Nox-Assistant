# Permite ejecutar: python -m src.cli

import os
import sys
# Setear PYTHONPATH automáticamente si no está
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root + os.pathsep + os.environ.get('PYTHONPATH', '')
from .console import main

if __name__ == "__main__":
    main()
