import re
import unicodedata
from typing import Dict, Any, Optional

from .contracts import IntentResult


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
    "list_known_targets": ["que podes abrir", "listar apps", "mostrame destinos"],
    "core_status": ["estado", "como estas", "que version sos"],
}


class IntentClassifier:
    """Interfaz base para clasificadores de intención."""

    def predict(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError


def normalize_text(text: str) -> str:
    """Normalize Spanish command text without requiring NLP dependencies."""
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^\w\s.:/-]", " ", ascii_text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", ascii_text).strip()


class RuleBasedIntentClassifier(IntentClassifier):
    """Deterministic MVP classifier used by the orchestrator and CLI.

    It keeps the first useful flows predictable while heavier ML backends stay
    optional behind the same contract.
    """

    def classify(self, text: str) -> IntentResult:
        normalized = normalize_text(text)

        if self._looks_like_list_known_targets(normalized):
            return IntentResult(
                name="list_known_targets",
                confidence=0.95,
                raw_text=text,
                entities={},
            )

        if self._looks_like_core_status(normalized):
            return IntentResult(
                name="core_status",
                confidence=0.95,
                raw_text=text,
                entities={},
            )

        open_target = self._extract_command_target(normalized, self._open_words())
        if open_target:
            entities = {"target": open_target}
            url = self._extract_url(open_target)
            if url:
                entities["url"] = url
            return IntentResult(
                name="open",
                confidence=0.9,
                raw_text=text,
                entities=entities,
            )

        close_target = self._extract_command_target(normalized, self._close_words())
        if close_target:
            return IntentResult(
                name="close",
                confidence=0.9,
                raw_text=text,
                entities={"target": close_target},
            )

        legacy = MockIntentClassifier().predict(text)
        return IntentResult(
            name=legacy["intent"],
            confidence=legacy["confidence"],
            raw_text=text,
            entities={},
        )

    def predict(self, text: str) -> Dict[str, Any]:
        return self.classify(text).to_legacy_dict()

    def _open_words(self) -> tuple[str, ...]:
        return ("abri", "abrir", "abre", "open", "lanza", "lanzar", "inicia", "iniciar", "ir a", "navega")

    def _close_words(self) -> tuple[str, ...]:
        return ("cierra", "cerrar", "cerra", "close")

    def _looks_like_list_known_targets(self, normalized: str) -> bool:
        patterns = (
            "que podes abrir",
            "que puedes abrir",
            "que apps podes abrir",
            "que aplicaciones podes abrir",
            "listar apps",
            "lista apps",
            "listar destinos",
            "mostrame destinos",
            "muestra destinos",
            "destinos disponibles",
            "apps disponibles",
        )
        return any(pattern in normalized for pattern in patterns)

    def _looks_like_core_status(self, normalized: str) -> bool:
        patterns = (
            "estado",
            "status",
            "como estas",
            "que version sos",
            "que version eres",
            "version",
        )
        return any(pattern == normalized or pattern in normalized for pattern in patterns)

    def _extract_command_target(self, normalized: str, command_words: tuple[str, ...]) -> str:
        for command in sorted(command_words, key=len, reverse=True):
            pattern = rf"(?:^|\b){re.escape(command)}\s+(?:la\s+|el\s+|los\s+|las\s+|a\s+|al\s+)?(?P<target>.+)$"
            match = re.search(pattern, normalized)
            if match:
                target = match.group("target").strip()
                return self._normalize_target_alias(target)
        return ""

    def _normalize_target_alias(self, target: str) -> str:
        aliases = {
            "navegador": "browser",
            "chrome": "chrome",
            "firefox": "firefox",
            "codigo": "vscode",
            "visual studio code": "vscode",
            "vs code": "vscode",
            "explorador": "explorer",
            "explorador de archivos": "explorer",
            "calculadora": "calculator",
        }
        return aliases.get(target, target)

    def _extract_url(self, normalized: str) -> str:
        for token in normalized.split():
            if token.startswith(("http://", "https://")):
                return token
            if token.startswith("www."):
                return f"https://{token}"
            if "." in token and "/" not in token:
                return f"https://{token}"
        return ""


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
            ("que podes abrir", "list_known_targets"),
            ("que puedes abrir", "list_known_targets"),
            ("listar apps", "list_known_targets"),
            ("mostrame destinos", "list_known_targets"),
            ("como estas", "core_status"),
            ("que version sos", "core_status"),
            ("estado", "core_status"),
            ("status", "core_status"),
            ("abre", "open"),
            ("cierra", "close"),
            ("cerrar", "close"),
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
            ("steam", "open"),
            ("calculadora", "open"),
        ]

    def predict(self, text: str) -> Dict[str, Any]:
        t = (text or "").lower()
        for k, v in self.rules:
            if k in t:
                return {"intent": v, "confidence": 1.0}
        return {"intent": "unknown", "confidence": 0.0}
