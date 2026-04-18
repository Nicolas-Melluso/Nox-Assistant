import re
import unicodedata


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


CORE_INTENTS = {
    "pc_shutdown",
    "pc_restart",
    "pc_sleep",
    "pc_hibernate",
    "pc_lock",
    "set_volume",
    "volume_up",
    "volume_down",
    "volume_mute",
    "volume_unmute",
    "set_brightness",
    "brightness_up",
    "brightness_down",
    "wifi_on",
    "wifi_off",
    "bluetooth_on",
    "bluetooth_off",
    "open_spotify",
    "close_spotify",
    "open_discord",
    "close_discord",
    "open_steam",
    "close_steam",
    "open_chrome",
    "close_chrome",
    "open_edge",
    "close_edge",
    "open_youtube",
    "close_youtube",
    "browser_search_web",
    "browser_open_history",
    "media_play",
    "media_pause",
    "media_next_track",
    "media_prev_track",
    "media_stop",
    "start_timer",
    "stop_timer",
    "set_alarm",
    "cancel_alarm",
    "take_screenshot",
    "get_time",
    "get_date",
    "get_cpu_usage",
    "get_ram_usage",
    "get_battery_status",
    "get_network_status",
    "open_task_manager",
    "mode_focus_on",
    "mode_gaming_on",
}


def _normalize_predicted_intent(predicted_intent: str) -> tuple[str, str | None]:
    # Soporta intents alias con formato "target__style" del set NOX250.
    if "__" in predicted_intent:
        base = predicted_intent.split("__", 1)[0]
        if base in CORE_INTENTS:
            return base, f"Alias NOX250: {predicted_intent} -> {base}"
    return predicted_intent, None


def route_intent(text: str, predicted_intent: str) -> tuple[str, str | None]:
    """
    Corrige intents en casos de lenguaje natural donde el clasificador puede fallar.
    Retorna (intent_final, razon_o_none).
    """
    normalized_intent, alias_reason = _normalize_predicted_intent(predicted_intent)
    t = _normalize(text)
    reason_prefix = f"{alias_reason}; " if alias_reason else ""

    # Volumen y brillo con valor explicito deben ser set exacto, no up/down ambiguo.
    if re.search(r"\bvolumen\b", t):
        if re.search(r"\b(\d{1,3}%?|maximo|maxima|max|minimo|minima|min|al\s+\d+)\b", t):
            if normalized_intent != "set_volume":
                return "set_volume", reason_prefix + "Regla: volumen con valor -> set_volume"

    if re.search(r"\bbrillo\b", t):
        if re.search(r"\b(\d{1,3}%?|maximo|maxima|max|minimo|minima|min|al\s+\d+)\b", t):
            if normalized_intent != "set_brightness":
                return "set_brightness", reason_prefix + "Regla: brillo con valor -> set_brightness"

    open_verbs = ("abre", "abri", "abrime", "abrir", "pon", "poneme", "reproduce")
    close_verbs = ("cierra", "cerra", "cerrame", "cerrar")

    if "youtube" in t:
        if any(v in t for v in close_verbs):
            if normalized_intent != "close_youtube":
                return "close_youtube", reason_prefix + "Regla: youtube + verbo de cierre"
            return normalized_intent, alias_reason
        if any(v in t for v in open_verbs):
            if normalized_intent != "open_youtube":
                return "open_youtube", reason_prefix + "Regla: youtube + verbo de apertura/reproduccion"
            return normalized_intent, alias_reason

    if re.search(r"\b(video|videos)\b", t):
        if re.search(r"\b(graba|grabar|grabacion|recording|pantalla)\b", t):
            pass
        elif any(v in t for v in open_verbs):
            if normalized_intent != "open_youtube":
                return "open_youtube", reason_prefix + "Regla: pedido de video -> YouTube por defecto"
            return normalized_intent, alias_reason

    if re.search(r"\b(sacame una foto|saca una foto|foto|captura de pantalla|pantallazo|screenshot)\b", t):
        if normalized_intent != "take_screenshot":
            return "take_screenshot", reason_prefix + "Regla: sinonimos de captura/foto"

    if re.search(r"\b(mail|correo|gmail|email)\b", t):
        if normalized_intent != "send_email" and "whatsapp" not in t:
            return "send_email", reason_prefix + "Regla: lenguaje de correo"

    return normalized_intent, alias_reason
