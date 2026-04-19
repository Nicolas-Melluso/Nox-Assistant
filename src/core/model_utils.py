"""
Funciones utilitarias para manejo de modelos y vectorizadores.
"""
import joblib
from pathlib import Path

def save_model(model, path):
    """Guarda un modelo sklearn/joblib en la ruta dada."""
    joblib.dump(model, path)

def load_model(path):
    """Carga un modelo sklearn/joblib desde la ruta dada."""
    return joblib.load(path)

def save_vectorizer(vectorizer, path):
    """Guarda un vectorizador sklearn/joblib en la ruta dada."""
    joblib.dump(vectorizer, path)

def load_vectorizer(path):
    """Carga un vectorizador sklearn/joblib desde la ruta dada."""
    return joblib.load(path)
