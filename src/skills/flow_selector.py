from __future__ import annotations


def suggest_flow(user_input: str, context: dict) -> str | None:
    text = (user_input or "").lower()
    hour = int(context.get("hour") or 12)
    cpu = float(context.get("cpu_percent") or 0)

    if any(k in text for k in ["foto", "camara", "selfie"]):
        return "photo_pro_flow"

    if any(k in text for k in ["gaming", "jugar", "steam", "discord", "setup gamer"]):
        return "gaming_setup_flow"

    if any(k in text for k in ["foco", "pomodoro", "concentr", "estudiar", "trabajar"]):
        return "focus_pomodoro_flow"

    # Nudge inteligente por contexto
    if hour >= 23 or hour <= 6:
        return "focus_pomodoro_flow" if cpu > 80 else None

    return None
