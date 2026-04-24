from typing import Dict, Any, Optional
from pathlib import Path
import os

from ..os_control import OSController
from . import Skill


class OSSkill(Skill):
    def __init__(self, os_controller: OSController, apps_config_path: Optional[str] = None):
        self.os_controller = os_controller
        self.apps = self._load_apps(apps_config_path)

    def _load_apps(self, apps_config_path: Optional[str]):
        # Intentar cargar YAML si está disponible, si no, fallback a parser mínimo
        path = Path(apps_config_path) if apps_config_path else Path(__file__).resolve().parents[2] / "config" / "apps.yaml"
        apps: Dict[str, Dict[str, Any]] = {}
        if not path.exists():
            return apps
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
                if isinstance(raw, dict):
                    return raw
        except Exception:
            # Fallback a parser simple en caso de no disponer de PyYAML
            with open(path, "r", encoding="utf-8") as f:
                current = None
                for raw in f:
                    line = raw.rstrip("\n")
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    if s.endswith(":") and not s.startswith("-"):
                        current = s[:-1].strip()
                        apps[current] = {"keywords": []}
                    elif s.startswith("- "):
                        if current is None:
                            continue
                        item = s[2:].strip().strip('"').strip("'")
                        apps[current].setdefault("keywords", []).append(item)
        return apps

    def _match_app(self, text: str) -> Optional[str]:
        t = text.lower()
        for app, data in self.apps.items():
            for kw in data.get("keywords", []):
                if kw.lower() in t:
                    return app
        return None

    def handles(self, intent_result: Dict[str, Any]) -> bool:
        intent = (intent_result.get("intent") or "").lower()
        text = (intent_result.get("input_text") or "").lower()
        if intent in ("open", "launch", "start", "play", "close", "stop"):
            return True
        if self._match_app(text):
            return True
        return False

    def run(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        intent = (intent_result.get("intent") or "").lower()
        text = (intent_result.get("input_text") or "") or ""
        app = self._match_app(text)
        try:
            if intent in ("open", "launch", "start", "play"):
                candidate = text.strip()
                if candidate.startswith("http") or candidate.startswith("www"):
                    res = self.os_controller.open_path(candidate)
                    return {"skill": "open_path", "success": bool(res.get("ok", False)), "result": res}
                if app:
                    app_info = self.apps.get(app, {}) or {}
                    # Si la configuración del app contiene una URL, abrirla en el navegador
                    url = app_info.get("url")
                    if url:
                        res = self.os_controller.open_path(url)
                        return {"skill": "open_url", "success": bool(res.get("ok", False)), "result": res, "target": app, "url": url}
                    # Intentar iniciar la app por nombre/path; si falla, fallback a abrir una URL conocida
                    target = app_info.get("path") or app
                    res = self.os_controller.start_app(target)
                    if res.get("ok"):
                        return {"skill": "start_app", "success": True, "result": res, "target": target}
                    # Fallbacks para servicios web conocidos
                    fallback_urls = {
                        "youtube": "https://www.youtube.com",
                        "spotify": "https://open.spotify.com",
                        "browser": None,
                    }
                    fb = fallback_urls.get(app)
                    if fb:
                        res2 = self.os_controller.open_path(fb)
                        return {"skill": "open_url", "success": bool(res2.get("ok", False)), "result": res2, "target": app, "url": fb}
                    # Último recurso: intentar abrir el texto como path/URL
                    res3 = self.os_controller.open_path(candidate)
                    return {"skill": "open_path", "success": bool(res3.get("ok", False)), "result": res3, "target": candidate}

            if intent in ("close", "stop"):
                if app:
                    if os.name == "nt":
                        cmd = f'taskkill /IM {app}.exe /F'
                    else:
                        cmd = f'pkill {app}'
                    res = self.os_controller.run_command(cmd, shell=True)
                    return {"skill": "kill_app", "success": bool(res.get("ok", False)), "result": res}
                return {"skill": "noop", "success": False}
        except Exception as e:
            return {"skill": "error", "success": False, "error": str(e)}
        return {"skill": "noop", "success": False}
