"""Public entity extraction facade.

The implementation lives in `core.entity_pipeline`. This module keeps the old
imports working while avoiding global spaCy loading at import time.
"""

from typing import Dict, List

from .entity_pipeline.dependencias import extraer_sujeto_verbo_objeto
from .entity_pipeline.ensamblado import ensamblar_output
from .entity_pipeline.limpieza import limpiar_texto
from .entity_pipeline.nlp_singleton import get_spacy_model
from .entity_pipeline.segmentacion import segmentar_frases


NEGACIONES_REGEX = [
    r"\bno\b",
    r"\bnunca\b",
    r"\bjam[aá]s\b",
    r"\bsin\b",
    r"\bning[uú]n\b",
    r"\bninguna\b",
    r"\bninguno\b",
    r"\btampoco\b",
    r"\bni\b",
    r"\bprohibido\b",
    r"\bevita[rd]?\b",
]


def extract_entities(text: str) -> List[Dict]:
    """Extract entities and sentence metadata from Spanish command text."""
    frases = segmentar_frases(text)
    nlp = get_spacy_model()
    return ensamblar_output(frases, NEGACIONES_REGEX, nlp, limpiar_texto)
