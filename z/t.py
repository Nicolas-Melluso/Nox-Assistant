"""
Script despachador para ejecutar scripts de training/runs/scripts usando un alias simple.
Uso: python t.py --NOMBRE_SCRIPT.py
Ejemplo: python t.py --run_intent_dataset_initial.py
"""
import sys
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path("training/runs/scripts")

def main():
    args = sys.argv[1:]
    if len(args) != 1 or not args[0].startswith("--"):
        print("Uso: python t.py --NOMBRE_SCRIPT.py")
        sys.exit(1)
    script_name = args[0][2:]
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"No se encontró el script: {script_path}")
        sys.exit(1)
    print(f"Ejecutando: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
