"""
Test de integración: evalúa métricas de intents usando el script de métricas.
Se puede ejecutar con pytest y valida que la accuracy global supere un umbral mínimo.
"""
import subprocess
import os
import csv
import pytest

# Construir rutas relativas a la raíz del proyecto (custom-voice-assistant)
CURRENT = os.path.abspath(__file__)
while not os.path.exists(os.path.join(CURRENT, "README.md")) and os.path.dirname(CURRENT) != CURRENT:
    CURRENT = os.path.dirname(CURRENT)
PROJECT_ROOT = CURRENT
SCRIPT_PATH = os.path.join(
    PROJECT_ROOT, "training", "runs", "scripts", "eval_metrics.py"
)
CSV_REPORT_PATH = os.path.join(
    PROJECT_ROOT, "training", "runs", "csv", "metrics_intents.csv"
)
DATASET_PATH = os.path.join(
    PROJECT_ROOT, "training", "datasets", "processed", "intents_p99_balanced.csv"
)

@pytest.mark.metrics
@pytest.mark.skipif(
    not os.path.exists(DATASET_PATH),
    reason="Dataset de intents no encontrado: se omite el test de métricas."
)
def test_intent_metrics():
    # Ejecutar el script de métricas
    result = subprocess.run([
        "python", SCRIPT_PATH
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"El script falló: {result.stderr}"
    # Leer el CSV generado
    with open(CSV_REPORT_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Buscar accuracy global
    accuracy_row = next((r for r in rows if r["Intent"] == "accuracy"), None)
    assert accuracy_row is not None, (
        "No se encontró la fila de accuracy en el reporte.")
    accuracy = float(accuracy_row["F1"])
    # Umbral mínimo de ejemplo (ajustar según necesidad)
    assert accuracy >= 0.10, (
        f"Accuracy global demasiado baja: {accuracy}")
