"""
feature_flags.py: Lógica para leer y consultar feature flags de NOX.
"""
import os
import yaml

FLAGS_PATH = os.path.join(os.path.dirname(__file__), "feature_flags.yaml")

class FeatureFlags:
    def __init__(self, path: str = FLAGS_PATH):
        with open(path, "r", encoding="utf-8") as f:
            self.flags = yaml.safe_load(f)

    def is_enabled(self, interface: str, category: str, feature: str) -> bool:
        """
        Consulta si una feature está habilitada para una interfaz.
        interface: 'CLI', 'API', 'Desktop'
        category: ej. 'api_externas'
        feature: ej. 'json', 'whatsapp'
        """
        interface = interface.upper()
        return bool(
            self.flags.get(interface, {})
                .get(category, {})
                .get(feature, False)
        )

    def set_flag(self, interface: str, category: str, feature: str, value: bool):
        interface = interface.upper()
        if interface not in self.flags:
            self.flags[interface] = {}
        if category not in self.flags[interface]:
            self.flags[interface][category] = {}
        self.flags[interface][category][feature] = value
        # Guardar cambios
        with open(FLAGS_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.flags, f, allow_unicode=True)

    def list_flags(self):
        return self.flags
