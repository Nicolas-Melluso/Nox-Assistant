"""
Script de evaluación de métricas F1, precisión y recall para intents y entidades.
- Lee un dataset CSV (texto, intent, entidades)
- Usa el pipeline actual para predecir intent y entidades
- Calcula métricas por clase y globales
- Exporta resultados en CSV y Markdown
- Puede usarse standalone o desde pytest
"""
import csv
import os
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
from sklearn.metrics import classification_report, precision_recall_fscore_support

# Ajusta estos paths según tu estructura
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "datasets", "processed", "intents_p99_balanced.csv"))
CSV_REPORT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "csv", "metrics_intents.csv"))
MD_REPORT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "csv", "metrics_intents.md"))

# --- Pipeline de predicción (placeholder, reemplazar por el real) ---
def predict_intent(text: str) -> str:
    # TODO: Importar y usar el pipeline real
    # Ejemplo: from src.core.engine import predict_intent
    return "abrir_app"  # Dummy

def predict_entities(text: str) -> List[str]:
    # TODO: Implementar extracción real de entidades
    return []

# --- Evaluación de intents ---
def load_intent_dataset(path: str) -> Tuple[List[str], List[str]]:
    y_true, texts = [], []
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            y_true.append(row[0])
            texts.append(row[1])
    return y_true, texts

def evaluate_intents(y_true: List[str], texts: List[str]) -> Dict:
    y_pred = [predict_intent(t) for t in texts]
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return report

def save_csv_report(report: Dict, path: str):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Intent", "Precision", "Recall", "F1", "Soporte"])
        for label, metrics in report.items():
            if label in ("accuracy", "macro avg", "weighted avg"):
                continue
            writer.writerow([
                label,
                f"{metrics['precision']:.3f}",
                f"{metrics['recall']:.3f}",
                f"{metrics['f1-score']:.3f}",
                int(metrics['support'])
            ])
        # Totales
        writer.writerow(["macro avg", report["macro avg"]['precision'], report["macro avg"]['recall'], report["macro avg"]['f1-score'], "-"])
        writer.writerow(["weighted avg", report["weighted avg"]['precision'], report["weighted avg"]['recall'], report["weighted avg"]['f1-score'], "-"])
        writer.writerow(["accuracy", "-", "-", report["accuracy"], "-"])

def save_md_report(report: Dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("| Intent | Precision | Recall | F1 | Soporte |\n")
        f.write("|--------|-----------|--------|----|---------|\n")
        for label, metrics in report.items():
            if label in ("accuracy", "macro avg", "weighted avg"):
                continue
            f.write(f"| {label} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | {metrics['f1-score']:.3f} | {int(metrics['support'])} |\n")
        f.write(f"| macro avg | {report['macro avg']['precision']:.3f} | {report['macro avg']['recall']:.3f} | {report['macro avg']['f1-score']:.3f} | - |\n")
        f.write(f"| weighted avg | {report['weighted avg']['precision']:.3f} | {report['weighted avg']['recall']:.3f} | {report['weighted avg']['f1-score']:.3f} | - |\n")
        f.write(f"| accuracy | - | - | {report['accuracy']:.3f} | - |\n")

if __name__ == "__main__":
    y_true, texts = load_intent_dataset(DATASET_PATH)
    report = evaluate_intents(y_true, texts)
    save_csv_report(report, CSV_REPORT_PATH)
    save_md_report(report, MD_REPORT_PATH)
    print(f"Reportes generados en {CSV_REPORT_PATH} y {MD_REPORT_PATH}")
