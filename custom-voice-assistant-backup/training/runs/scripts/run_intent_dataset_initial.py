"""
Script de control para auditar el dataset de intenciones (p99).
No ejecutar sin revisión. Genera un archivo de control con la fecha y detalles del dataset.
"""
import csv
from datetime import datetime
from pathlib import Path

RAW_DATASET = Path("training/datasets/raw/intents_p99_template.csv")
CONTROL_DIR = Path("training/runs/csv")

print("Corriendo control de dataset de intenciones (p99). Fecha:", datetime.now().isoformat())

def main():
    run_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    control_file = CONTROL_DIR / f"control_intents_dataset_{run_date}.log"
    with RAW_DATASET.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    with control_file.open("w", encoding="utf-8") as log:
        log.write(f"Fecha de control: {run_date}\n")
        log.write(f"Cantidad de ejemplos: {len(rows)}\n")
        log.write(f"Intenciones únicas: {set(r['intent'] for r in rows)}\n")
        log.write("Primeros 5 ejemplos:\n")
        for r in rows[:5]:
            log.write(str(r) + "\n")

if __name__ == "__main__":
    main()

print(f"Archivo de control guardado en: {CONTROL_DIR.resolve()}")
