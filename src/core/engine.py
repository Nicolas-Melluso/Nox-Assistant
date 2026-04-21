"""Minimal core engine scaffold (Fase 0).
Implements a placeholder `CoreEngine` with simple interface used by CLI and tests.
"""
"""
CoreEngine: motor principal del asistente de voz.

- Predice intenciones a partir de texto.
- Extrae entidades (personas, lugares, fechas, horas) usando spaCy y dateparser.
- Ejecuta acciones (placeholder).

Ejemplo de uso:

    from src.core.engine import CoreEngine
    engine = CoreEngine()
    result = engine.predict_intent("Recordame el 10 de diciembre a las 18:00 con Juan Pérez en Madrid.")
    print(result)
    # {'intent': 'unknown', 'confidence': 0.0, 'input_text': ..., 'entities': [...]} 
"""

from typing import Dict, Any
from .entity_extraction import extract_entities

class CoreEngine:
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    def predict_intent(self, text: str) -> Dict[str, Any]:
        """Predice la intención y extrae entidades del texto."""
        # Lógica simple basada en palabras clave
        # Ordenar por prioridad: verbos más específicos primero
        intent_keywords = [
            ("responde", "answer"),
            ("escribe", "write"),
            ("lee", "read"),
            ("elimina", "delete"),
            ("borra", "delete"),
            ("actualiza", "update"),
            ("sincroniza", "sync"),
            ("descarga", "download"),
            ("envía", "send"),
            ("manda", "send"),
            ("crea", "create"),
            ("genera", "generate"),
            ("muestra", "show"),
            ("oculta", "hide"),
            ("reproduce", "play"),
            ("pausa", "pause"),
            ("detén", "stop"),
            ("pará", "stop"),
            ("pon", "set"),
            ("poné", "set"),
            ("configura", "configure"),
            ("llama", "call"),
            ("busca", "search"),
            ("abre", "open"),
            ("abrí", "open"),
            ("cierra", "close"),
            ("cerrá", "close"),
            ("enciende", "turn_on"),
            ("encender", "turn_on"),
            ("prender", "turn_on"),
            ("apaga", "turn_off"),
            ("apagar", "turn_off"),
            ("sube", "increase"),
            ("baja", "decrease"),
        ]
        intent = "unknown"
        confidence = 0.0
        text_lower = text.lower()
        for keyword, mapped_intent in intent_keywords:
            if keyword in text_lower:
                intent = mapped_intent
                confidence = 0.8
                break
        entities = extract_entities(text)
        return {
            "intent": intent,
            "confidence": confidence,
            "input_text": text,
            "entities": entities
        }

    def execute_skill(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder skill execution."""
        return {"skill": "noop", "success": True, "result": None}
