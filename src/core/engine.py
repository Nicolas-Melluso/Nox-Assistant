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
from .external_api import ExternalAPIClient
from sentence_transformers import SentenceTransformer, util
import numpy as np



class CoreEngine:
    def __init__(self, config: Dict[str, Any] | None = None, external_services: Dict[str, Any] | None = None):
        self.config = config or {}
        self.external_api_client = ExternalAPIClient(external_services)
        # Ejemplos mínimos de intenciones (puedes expandir)
        self.intent_examples = {
            "answer": [
                "responde a la pregunta", "dame una respuesta", "responde el mensaje", "contesta el mensaje", "contesta la pregunta", "responde a este correo", "responde a este chat", "contesta este chat"
            ],
            "write": ["escribe un texto", "redacta un mensaje"],
            "read": ["lee el mensaje", "muestra el texto"],
            "delete": ["elimina el archivo", "borra el mensaje", "borra la nota", "elimina el documento"],
            "update": ["actualiza la información", "modifica el dato", "actualiza el sistema", "modifica la configuración"],
            "sync": ["sincroniza los datos", "actualiza la nube", "sincroniza contactos"],
            "download": ["descarga el archivo", "baja el documento", "descarga la imagen", "descarga el informe"],
            "send": [
                "envía el mensaje", "manda el correo", "envía un mensaje", "manda la ubicación", "envía un archivo", "envía la foto", "envía el documento", "envía la ubicación", "envía el contacto", "envía la información"
            ],
            "create": [
                "crea un archivo", "crea una nota", "crea una carpeta", "crea un documento", "crea un reporte", "crea un proyecto", "crea una lista", "crea una presentación"
            ],
            "generate": [
                "genera un reporte", "genera un informe", "genera un documento", "genera una copia", "genera una presentación", "genera una lista", "genera un archivo", "genera una nota"
            ],
            "show": ["muestra la imagen", "enseña el resultado", "muestra el clima", "muestra la barra"],
            "hide": ["oculta la ventana", "esconde el panel", "oculta la barra"],
            "play": ["reproduce la canción", "pon música", "reproduce música"],
            "pause": ["pausa la música", "detén el video", "pausa la canción"],
            "stop": [
                "detén la reproducción", "pará la música", "detén la música", "para la canción", "detén el sonido", "detén el temporizador", "detén el video", "detén la alarma",
                "detén la radio", "detén el audio", "detén el podcast", "detén la grabación", "detén la llamada", "detén el proceso"
            ],
            "set": ["pon la alarma", "configura el temporizador"],
            "configure": ["configura el sistema", "ajusta la configuración", "configura el wifi"],
            "call": ["llama a Juan", "haz una llamada"],
            "search": ["busca en internet", "encuentra información", "busca noticias"],
            "open": ["abre la aplicación", "abrí el programa", "abre la puerta"],
            "close": ["cierra la ventana", "cerrá el archivo", "cierra la puerta"],
            "turn_on": ["enciende la luz", "prende el ventilador"],
            "turn_off": ["apaga la luz", "apagar el televisor", "apaga la tele"],
            "increase": ["sube el volumen", "aumenta la intensidad", "sube la música", "aumenta el brillo", "sube la temperatura"],
            "decrease": [
                "baja el volumen", "disminuye la intensidad", "baja la música", "reduce el volumen", "baja el brillo", "disminuye la música", "baja la temperatura", "reduce la intensidad",
                "disminuye el sonido", "disminuye el audio", "baja el sonido", "baja el audio", "reduce la música", "reduce el brillo", "disminuye el brillo", "disminuye la luz"
            ],
        }
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # Precalcula embeddings de ejemplos
        self.intent_embeddings = {
            intent: self.model.encode(examples, convert_to_tensor=True)
            for intent, examples in self.intent_examples.items()
        }


    def extract_entities(self, text: str):
        """Extrae entidades usando el pipeline modular."""
        return extract_entities(text)

    def call_external_api(self, service: str, endpoint: str, params: Dict[str, Any] = None, method: str = "GET", data: Dict[str, Any] = None):
        """
        Llama a un API externo usando ExternalAPIClient.
        method: "GET" (fetch_data) o "POST"/"PUT"/etc (send_command)
        """
        if method.upper() == "GET":
            return self.external_api_client.fetch_data(service, endpoint, params=params)
        else:
            return self.external_api_client.send_command(service, endpoint, data=data, method=method)
    
        # Ejemplos mínimos de intenciones (puedes expandir)
        self.intent_examples = {
            "answer": [
                "responde a la pregunta", "dame una respuesta", "responde el mensaje", "contesta el mensaje", "contesta la pregunta", "responde a este correo", "responde a este chat", "contesta este chat"
            ],
            "write": ["escribe un texto", "redacta un mensaje"],
            "read": ["lee el mensaje", "muestra el texto"],
            "delete": ["elimina el archivo", "borra el mensaje", "borra la nota", "elimina el documento"],
            "update": ["actualiza la información", "modifica el dato", "actualiza el sistema", "modifica la configuración"],
            "sync": ["sincroniza los datos", "actualiza la nube", "sincroniza contactos"],
            "download": ["descarga el archivo", "baja el documento", "descarga la imagen", "descarga el informe"],
            "send": [
                "envía el mensaje", "manda el correo", "envía un mensaje", "manda la ubicación", "envía un archivo", "envía la foto", "envía el documento", "envía la ubicación", "envía el contacto", "envía la información"
            ],
            "create": [
                "crea un archivo", "crea una nota", "crea una carpeta", "crea un documento", "crea un reporte", "crea un proyecto", "crea una lista", "crea una presentación"
            ],
            "generate": [
                "genera un reporte", "genera un informe", "genera un documento", "genera una copia", "genera una presentación", "genera una lista", "genera un archivo", "genera una nota"
            ],
            "show": ["muestra la imagen", "enseña el resultado", "muestra el clima", "muestra la barra"],
            "hide": ["oculta la ventana", "esconde el panel", "oculta la barra"],
            "play": ["reproduce la canción", "pon música", "reproduce música"],
            "pause": ["pausa la música", "detén el video", "pausa la canción"],
            "stop": [
                "detén la reproducción", "pará la música", "detén la música", "para la canción", "detén el sonido", "detén el temporizador", "detén el video", "detén la alarma",
                "detén la radio", "detén el audio", "detén el podcast", "detén la grabación", "detén la llamada", "detén el proceso"
            ],
            "set": ["pon la alarma", "configura el temporizador"],
            "configure": ["configura el sistema", "ajusta la configuración", "configura el wifi"],
            "call": ["llama a Juan", "haz una llamada"],
            "search": ["busca en internet", "encuentra información", "busca noticias"],
            "open": ["abre la aplicación", "abrí el programa", "abre la puerta"],
            "close": ["cierra la ventana", "cerrá el archivo", "cierra la puerta"],
            "turn_on": ["enciende la luz", "prende el ventilador"],
            "turn_off": ["apaga la luz", "apagar el televisor", "apaga la tele"],
            "increase": ["sube el volumen", "aumenta la intensidad", "sube la música", "aumenta el brillo", "sube la temperatura"],
            "decrease": [
                "baja el volumen", "disminuye la intensidad", "baja la música", "reduce el volumen", "baja el brillo", "disminuye la música", "baja la temperatura", "reduce la intensidad",
                "disminuye el sonido", "disminuye el audio", "baja el sonido", "baja el audio", "reduce la música", "reduce el brillo", "disminuye el brillo", "disminuye la luz"
            ],
        }
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # Precalcula embeddings de ejemplos
        self.intent_embeddings = {
            intent: self.model.encode(examples, convert_to_tensor=True)
            for intent, examples in self.intent_examples.items()
        }

    def predict_intent(self, text: str) -> Dict[str, Any]:
        """Predice la intención usando embeddings y similitud de coseno."""
        text_emb = self.model.encode([text], convert_to_tensor=True)
        best_intent = "unknown"
        best_score = 0.0
        for intent, emb_list in self.intent_embeddings.items():
            # Calcula similitud con todos los ejemplos de la intención
            scores = util.cos_sim(text_emb, emb_list)[0].cpu().numpy()
            score = float(np.max(scores))
            if score > best_score:
                best_score = score
                best_intent = intent
        # Umbral mínimo para considerar una intención válida
        threshold = 0.65
        import os
        if best_score < threshold:
            best_intent = "unknown"
            best_score = 0.0
            # Loguear frases no reconocidas solo si no estamos en modo test
            if os.environ.get("TESTS", "0") != "1":
                try:
                    with open("errores_intencion.log", "a", encoding="utf-8") as f:
                        f.write(text.strip().replace("\n", " ") + "\n")
                except Exception:
                    pass
        entities = extract_entities(text)
        return {
            "intent": best_intent,
            "confidence": round(float(best_score), 3),
            "input_text": text,
            "entities": entities
        }

    def execute_skill(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder skill execution."""
        return {"skill": "noop", "success": True, "result": None}
