from __future__ import annotations

SKILL_POLICIES: dict[str, dict] = {
    "take_photos": {"risk": "medium", "confirm": True, "reason": "Accede a la camara"},
    "show_photo_picker": {"risk": "low", "confirm": False, "reason": "UI local de seleccion"},
    "take_screenshot": {"risk": "medium", "confirm": True, "reason": "Captura contenido de pantalla"},
    "set_volume": {"risk": "low", "confirm": False, "reason": "Ajuste multimedia"},
    "set_brightness": {"risk": "low", "confirm": False, "reason": "Ajuste de pantalla"},
    "open_app": {"risk": "medium", "confirm": True, "reason": "Abre apps o URLs"},
    "open_folder": {"risk": "low", "confirm": False, "reason": "Abre explorador"},
    "shutdown": {"risk": "critical", "confirm": True, "reason": "Apaga el sistema"},
    "restart": {"risk": "critical", "confirm": True, "reason": "Reinicia el sistema"},
    "hibernate": {"risk": "high", "confirm": True, "reason": "Suspende la sesion actual"},
    "sleep_pc": {"risk": "high", "confirm": True, "reason": "Suspende temporalmente el equipo"},
    "lock_pc": {"risk": "medium", "confirm": True, "reason": "Bloquea la pantalla"},
    "search_youtube": {"risk": "low", "confirm": False, "reason": "Busqueda web"},
    "start_timer": {"risk": "low", "confirm": False, "reason": "Timer local"},
    "get_system_info": {"risk": "low", "confirm": False, "reason": "Lectura de estado"},
    "notify": {"risk": "low", "confirm": False, "reason": "Notificacion local"},
    "activate_focus_mode": {"risk": "medium", "confirm": True, "reason": "Cambia estado del sistema"},
    "activate_gaming_mode": {"risk": "medium", "confirm": True, "reason": "Cambia estado del sistema y abre apps"},
    "photo_pro_flow": {"risk": "medium", "confirm": True, "reason": "Camara + selector + apertura carpeta"},
    "gaming_setup_flow": {"risk": "medium", "confirm": True, "reason": "Ajustes + apps + posible web"},
    "focus_pomodoro_flow": {"risk": "medium", "confirm": True, "reason": "Ajustes + timer + apps"},
    "voice_control_start": {"risk": "high", "confirm": True, "reason": "Activa escucha continua"},
    "voice_control_stop": {"risk": "high", "confirm": True, "reason": "Control de modo escucha"},
    "speak_text": {"risk": "low", "confirm": False, "reason": "Salida de voz local"},
}


def get_policy(tool: str) -> dict:
    return SKILL_POLICIES.get(tool, {"risk": "medium", "confirm": True, "reason": "Skill no clasificada"})


def requires_confirmation(tool: str) -> bool:
    pol = get_policy(tool)
    return bool(pol.get("confirm", False)) or str(pol.get("risk", "low")) in {"medium", "high", "critical"}
