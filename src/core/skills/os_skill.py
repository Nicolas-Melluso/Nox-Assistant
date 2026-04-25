from pathlib import Path
from typing import Any, Dict, Optional

from ..contracts import IntentResult, SkillResult
from ..os_control import OSController
from . import Skill


def load_apps_config(apps_config_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
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


class OSSkill(Skill):
    name = "os.open_known_target"
    description = "Open configured apps or URLs through the operating system."
    permissions = ("os.open_path", "os.start_app")
    supported_intents = ("open", "launch", "start", "play")

    def __init__(self, os_controller: OSController, apps_config_path: Optional[str] = None):
        self.os_controller = os_controller
        self.apps = load_apps_config(apps_config_path)

    def _load_apps(self, apps_config_path: Optional[str]):
        return load_apps_config(apps_config_path)

    def _match_app(self, text: str) -> Optional[str]:
        t = (text or "").lower()
        for app, data in self.apps.items():
            for kw in data.get("keywords", []):
                if kw.lower() in t:
                    return app
        return None

    def handles(self, intent_result: Dict[str, Any]) -> bool:
        intent = (intent_result.get("intent") or "").lower()
        text = (intent_result.get("input_text") or "").lower()
        return intent in self.supported_intents or self._match_app(text) is not None

    def run(
        self,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        if isinstance(intent_result, IntentResult):
            intent = intent_result.name.lower()
            text = intent_result.raw_text or ""
            entities = intent_result.entities if isinstance(intent_result.entities, dict) else {}
        else:
            intent = (intent_result.get("intent") or "").lower()
            text = (intent_result.get("input_text") or "") or ""
            entities = intent_result.get("entities") if isinstance(intent_result.get("entities"), dict) else {}

        app = self._match_app(text)
        if not app and isinstance(entities, dict):
            target = str(entities.get("target") or "").lower()
            if target in self.apps:
                app = target

        try:
            if intent in ("open", "launch", "start", "play"):
                candidate = text.strip()
                if candidate.startswith(("http", "www")):
                    res = self.os_controller.open_path(candidate)
                    return SkillResult(
                        success=bool(res.get("ok", False)),
                        message=f"Abri {candidate}.",
                        data={"result": res, "target": candidate},
                    )

                if app:
                    app_info = self.apps.get(app, {}) or {}
                    url = app_info.get("url")
                    if url:
                        res = self.os_controller.open_path(url)
                        return SkillResult(
                            success=bool(res.get("ok", False)),
                            message=f"Abri {app}.",
                            data={"result": res, "target": app, "url": url},
                        )

                    target = app_info.get("path") or app
                    res = self.os_controller.start_app(target)
                    if res.get("ok"):
                        return SkillResult(
                            success=True,
                            message=f"Inicie {target}.",
                            data={"result": res, "target": target},
                        )

                    fallback_urls = {
                        "youtube": "https://www.youtube.com",
                        "spotify": "https://open.spotify.com",
                    }
                    fb = fallback_urls.get(app)
                    if fb:
                        res2 = self.os_controller.open_path(fb)
                        return SkillResult(
                            success=bool(res2.get("ok", False)),
                            message=f"Abri {app}.",
                            data={"result": res2, "target": app, "url": fb},
                        )

                return SkillResult(
                    success=False,
                    message=f"No tengo un destino seguro configurado para '{candidate}'.",
                    data={"target": candidate},
                )

        except Exception as exc:
            return SkillResult(success=False, message="Error ejecutando control del sistema.", error=str(exc))

        return SkillResult(success=False, message="No se ejecuto ninguna accion segura.")


class BlockedProcessControlSkill(Skill):
    name = "os.process_control.blocked"
    description = "Reject process control actions until explicit permissions and auditing are complete."
    permissions = ("os.process_control.request",)
    supported_intents = ("close", "stop")

    def run(
        self,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        if isinstance(intent_result, IntentResult):
            text = intent_result.raw_text or ""
            entities = intent_result.entities if isinstance(intent_result.entities, dict) else {}
        else:
            text = (intent_result.get("input_text") or "") or ""
            entities = intent_result.get("entities") if isinstance(intent_result.get("entities"), dict) else {}

        target = str(entities.get("target") or text.strip())
        return SkillResult(
            success=False,
            message="Cerrar procesos esta bloqueado en el MVP hasta tener permisos explicitos.",
            data={"target": target, "blocked": True, "reason": "process_control_blocked"},
        )


class ListKnownTargetsSkill(Skill):
    name = "os.list_known_targets"
    description = "List configured safe app and URL targets."
    permissions = ("os.list_known_targets",)
    supported_intents = ("list_known_targets",)

    def __init__(self, apps_config_path: Optional[str] = None):
        self.apps = load_apps_config(apps_config_path)

    def run(
        self,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        targets = []
        for name, data in sorted(self.apps.items()):
            kind = "url" if data.get("url") else "app"
            target = data.get("url") or data.get("path") or name
            targets.append(
                {
                    "name": name,
                    "kind": kind,
                    "target": target,
                    "keywords": list(data.get("keywords", [])),
                }
            )

        names = ", ".join(item["name"] for item in targets)
        message = f"Puedo abrir: {names}." if names else "No hay destinos configurados."
        return SkillResult(
            success=True,
            message=message,
            data={"targets": targets, "count": len(targets)},
        )
