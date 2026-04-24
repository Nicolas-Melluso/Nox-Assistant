from typing import Dict, Any, Optional


DEFAULT_INTENT_EXAMPLES: Dict[str, list] = {
    "answer": [
        "responde a la pregunta", "dame una respuesta", "responde el mensaje", "contesta el mensaje",
    ],
    "write": ["escribe un texto", "redacta un mensaje"],
    "read": ["lee el mensaje", "muestra el texto"],
    "delete": ["elimina el archivo", "borra el mensaje"],
    "open": ["abre la aplicación", "abrir youtube", "abrir spotify", "abre spotify"],
    "close": ["cierra la ventana", "cerrar spotify"],
    "play": ["reproduce la canción", "pon música", "reproduce música"],
    "pause": ["pausa la música", "pausa"],
    "stop": ["detén la música", "detener"],
    "set": ["pon la alarma", "configura el temporizador"],
    "configure": ["configura el wifi", "ajusta la configuración"],
    "call": ["llama a"],
    "search": ["busca", "buscar"],
}


class IntentClassifier:
    """Interfaz base para clasificadores de intención."""

    def predict(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError


class LazySentenceTransformerIntentClassifier(IntentClassifier):
    """Clasificador basado en sentence-transformers cargado de forma perezosa.

    Evita importar/descargar modelos hasta que `predict()` sea llamado.
    """

    def __init__(self, intent_examples: Optional[Dict[str, list]] = None, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.65):
        self.intent_examples = intent_examples or DEFAULT_INTENT_EXAMPLES
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._util = None
        self._np = None
        self._embeddings = None

    def _ensure_model(self):
        if self._model is None:
            # Import localmente para evitar coste en import time
            from sentence_transformers import SentenceTransformer, util
            import numpy as np

            self._model = SentenceTransformer(self.model_name)
            self._util = util
            self._np = np
            # Precompute embeddings for examples
            self._embeddings = {
                intent: self._model.encode(examples, convert_to_tensor=True)
                for intent, examples in self.intent_examples.items()
            }

    def predict(self, text: str) -> Dict[str, Any]:
        self._ensure_model()
        if not text:
            return {"intent": "unknown", "confidence": 0.0}
        text_emb = self._model.encode([text], convert_to_tensor=True)
        best_intent = "unknown"
        best_score = 0.0
        for intent, emb in self._embeddings.items():
            scores = self._util.cos_sim(text_emb, emb)[0]
            try:
                score = float(self._np.max(scores.cpu().numpy()))
            except Exception:
                score = float(self._np.max(scores.numpy()))
            if score > best_score:
                best_score = score
                best_intent = intent
        if best_score < self.threshold:
            return {"intent": "unknown", "confidence": 0.0}
        return {"intent": best_intent, "confidence": round(float(best_score), 3)}


class MockIntentClassifier(IntentClassifier):
    """Clasificador simple para tests y CI que usa reglas por substring."""

    def __init__(self):
        self.rules = [
            ("pon la alarma", "set"),
            ("enciende", "turn_on"),
            ("apaga", "turn_off"),
            ("sube", "increase"),
            ("baja", "decrease"),
            ("configura", "configure"),
            ("llama", "call"),
            ("busca", "search"),
            ("abre", "open"),
            ("cierra", "close"),
            ("crea", "create"),
            ("genera", "generate"),
            ("muestra", "show"),
            ("oculta", "hide"),
            ("reproduce", "play"),
            ("pausa", "pause"),
            ("detén", "stop"),
            ("deten", "stop"),
            ("detener", "stop"),
            ("responde", "answer"),
            ("escribe", "write"),
            ("lee", "read"),
            ("elimina", "delete"),
            ("borra", "delete"),
            ("actualiza", "update"),
            ("sincroniza", "sync"),
            ("descarga", "download"),
            ("envía", "send"),
            ("envia", "send"),
            ("manda", "send"),
            ("spotify", "open"),
            ("youtube", "open"),
        ]

    def predict(self, text: str) -> Dict[str, Any]:
        t = (text or "").lower()
        for k, v in self.rules:
            if k in t:
                return {"intent": v, "confidence": 1.0}
        return {"intent": "unknown", "confidence": 0.0}
