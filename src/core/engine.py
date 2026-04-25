"""Refactored CoreEngine delegando intent classification y skills.
"""

from typing import Dict, Any, Optional, Callable
import os

from .external_api import ExternalAPIClient
from .os_control import OSController, SubprocessOSController
from .intent_classifier import LazySentenceTransformerIntentClassifier, MockIntentClassifier, RuleBasedIntentClassifier
from .orchestrator import NoxOrchestrator, default_registry
from .security import FileAuditSink


class CoreEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None, external_services: Optional[Dict[str, Any]] = None, os_controller: Optional[OSController] = None, classifier: Optional[Any] = None, entity_extractor: Optional[Callable[[str], list]] = None):
        self.config = config or {}
        self.external_api_client = ExternalAPIClient(external_services)
        if os_controller is not None:
            self.os_controller = os_controller
        else:
            dry = os.environ.get("MOCK_ENGINE", "0") == "1"
            self.os_controller = SubprocessOSController(dry_run=dry)

        if classifier is not None:
            self.intent_classifier = classifier
        else:
            if os.environ.get("MOCK_ENGINE", "0") == "1":
                self.intent_classifier = MockIntentClassifier()
            elif self.config.get("classifier_backend") == "sentence_transformer":
                self.intent_classifier = LazySentenceTransformerIntentClassifier()
            else:
                self.intent_classifier = RuleBasedIntentClassifier()

        self.skill_registry = default_registry(os_controller=self.os_controller)
        audit_sink = None
        if self.config.get("audit_enabled", True):
            audit_path = self.config.get("audit_path", "logs/audit.jsonl")
            audit_sink = FileAuditSink(audit_path)
        self.orchestrator = NoxOrchestrator(
            classifier=self.intent_classifier,
            registry=self.skill_registry,
            os_controller=self.os_controller,
            audit_sink=audit_sink,
        )
        # Inyectable: extractor de entidades (útil para tests para evitar cargar spaCy)
        self.entity_extractor = entity_extractor

    def extract_entities(self, text: str):
        # Importar y ejecutar el pipeline de extracción de entidades de forma perezosa
        if self.entity_extractor is not None:
            try:
                return self.entity_extractor(text)
            except Exception:
                return []
        try:
            from .entity_extraction import extract_entities as _extract
        except Exception:
            # Si falla la importación (p. ej. spaCy no instalado en CI), devolver lista vacía
            return []
        return _extract(text)

    def call_external_api(self, service: str, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", data: Optional[Dict[str, Any]] = None):
        if method.upper() == "GET":
            return self.external_api_client.fetch_data(service, endpoint, params=params)
        return self.external_api_client.send_command(service, endpoint, data=data, method=method)

    def predict_intent(self, text: str) -> Dict[str, Any]:
        result = self.intent_classifier.predict(text)
        result["input_text"] = text
        result["entities"] = self.extract_entities(text)
        return result

    def execute_skill(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        intent = (intent_result.get("intent") or "").lower()
        if intent == "noop":
            return {"skill": "noop", "success": True}
        try:
            if hasattr(self, "skill_registry") and self.skill_registry:
                skill_result = self.skill_registry.dispatch(intent_result)
                skill = self.skill_registry.find_for_intent(intent)
                skill_name = skill.name if skill else (skill_result.data or {}).get("skill", "noop")
                return skill_result.to_legacy_dict(skill_name)
        except Exception as e:
            return {"skill": "error", "success": False, "error": str(e)}
        return {"skill": "noop", "success": False}

    def handle(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compatibility wrapper around the new orchestrator entrypoint."""
        result = self.orchestrator.handle(text, context=context)
        legacy = result.to_legacy_dict()
        legacy["entities"] = self.extract_entities(text)
        return legacy
