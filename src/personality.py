from __future__ import annotations

import hashlib
import os

_PERSONA_MODE = os.getenv("NOX_PERSONA_MODE", "jarvis_sarcastic").strip().lower()
_ENABLE_JOKES = os.getenv("NOX_ENABLE_JOKES", "true").strip().lower() in {"1", "true", "yes", "si", "on"}

_JARVIS_SARCASTIC_QUIPS = [
    "Mision cumplida. Increiblemente, sin incendiar el sistema.",
    "Listo. Lo hice rapido para que no te diera tiempo a procrastinar.",
    "Hecho. Otro dia salvado por tu asistente favorito.",
    "Terminado. Prometo no cobrar horas extra por genialidad.",
]


def get_persona_prompt_block() -> str:
    if _PERSONA_MODE == "jarvis_sarcastic":
        return (
            "Tono: elegante, directo y ligeramente sarcastico (sin faltar el respeto). "
            "Prioriza respuestas cortas, accionables y con confianza. "
            "Si hay error, ofrece solucion concreta en 1-2 pasos."
        )
    return "Tono: profesional, claro y conciso."


def maybe_add_persona_quip(summary: str) -> str:
    text = (summary or "").strip()
    if not text or not _ENABLE_JOKES or _PERSONA_MODE != "jarvis_sarcastic":
        return text

    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(_JARVIS_SARCASTIC_QUIPS)
    quip = _JARVIS_SARCASTIC_QUIPS[idx]
    return f"{text}\n{quip}"
