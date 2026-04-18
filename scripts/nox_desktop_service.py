from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent_logging import append_step_log, get_log_path
from src.autonomous_agent import run_agent
from src.skills.voice_offline import speak_text, start_voice_control, stop_voice_control


def _should_skip_tts_line(line: str) -> bool:
    """Identifica líneas técnicas que no deben ser habladas en TTS."""
    low = (line or "").strip().lower()
    if not low:
        return True

    technical_markers = [
        "herramientas usadas",
        "providers usados",
        "run id",
        "tool:",
        "args:",
        "stage:",
        "traceback",
        "open_app(",
        "play_game_smart(",
        "search_youtube(",
        "set_volume(",
        "set_brightness(",
    ]
    return any(m in low for m in technical_markers)


def _message_for_tts(message: str) -> str:
    """Devuelve una respuesta hablable, sin detalles tecnicos que deben quedar en logs."""
    lines = [ln.strip() for ln in (message or "").splitlines()]
    clean_lines = [ln for ln in lines if not _should_skip_tts_line(ln)]

    if not clean_lines:
        return "Listo. Tarea completada."

    spoken = " ".join(clean_lines)
    spoken = re.sub(r"\s+", " ", spoken).strip()

    # Limita verbosidad para TTS y evita lectura larga de resumenes.
    if len(spoken) > 220:
        spoken = spoken[:217].rstrip() + "..."
    return spoken


def _startup_bat_path() -> Path:
    appdata = Path(os.getenv("APPDATA", ""))
    return appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "nox_desktop_service.bat"


def install_startup() -> None:
    bat = _startup_bat_path()
    repo = ROOT
    py = str(Path(sys.executable))
    content = f"""@echo off
cd /d \"{repo}\"
\"{py}\" scripts\\nox_desktop_service.py --run
"""
    bat.write_text(content, encoding="utf-8")
    print(f"Startup instalado: {bat}")


def remove_startup() -> None:
    bat = _startup_bat_path()
    if bat.exists():
        bat.unlink()
        print(f"Startup eliminado: {bat}")
    else:
        print("Startup no estaba instalado.")


def run_service() -> None:
    print("NOX Desktop Service iniciado. Voz activa en background.")

    partial_state = {"last": "", "ts": 0.0}

    def _on_wake(raw: str) -> None:
        print(f"[SERVICE][WAKE] Detectada wake word en: {raw}")
        print("[SERVICE][LISTENING] Escuchando comando...")
        append_step_log({"stage": "service_wake", "text": raw})

    def _on_partial(text: str) -> None:
        now = time.time()
        if text == partial_state["last"] and (now - partial_state["ts"]) < 1.0:
            return
        partial_state["last"] = text
        partial_state["ts"] = now
        print(f"[SERVICE][PARTIAL] {text}")

    def _on_command(cmd: str) -> None:
        print(f"[SERVICE][VOICE] {cmd}")
        append_step_log({"stage": "service_voice_command", "command": cmd})

        result = run_agent(cmd, on_confirm=lambda t, a, p: str(p.get("risk", "low")).lower() == "low")

        # Log completo visible para auditar todo lo que produjo la IA (incluye estilo/persona).
        print(f"[SERVICE][IA_FULL] {result.message}")
        append_step_log(
            {
                "stage": "service_ia_full",
                "message": result.message,
                "tools_used": result.tools_used,
                "providers_used": result.providers_used,
                "run_id": result.run_id,
            }
        )

        # Filtrar antes de hablar: remover líneas técnicas, solo guardar en logs
        tts_message = _message_for_tts(result.message)
        append_step_log({"stage": "service_tts", "message": tts_message})
        print("[SERVICE][LISTENING] Esperando wake word...")

    info = start_voice_control(on_command=_on_command, on_wake=_on_wake, on_partial=_on_partial)
    if not info.get("started"):
        print(f"No se pudo iniciar voz: {info.get('message')}")
        append_step_log({"stage": "service_start_error", "error": info.get("message")})
        return

    print("Modo servicio activo. Ctrl+C para detener.")
    print(f"[SERVICE][LISTENING] Esperando wake word '{info.get('wake_word', 'nox')}'...")
    print(f"[SERVICE][LOG] Archivo: {get_log_path()}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo servicio...")
    finally:
        append_step_log({"stage": "service_stop"})
        stop_voice_control()


def main() -> None:
    parser = argparse.ArgumentParser(description="NOX desktop service")
    parser.add_argument("--run", action="store_true", help="Run service loop")
    parser.add_argument("--install-startup", action="store_true", help="Install startup bat")
    parser.add_argument("--remove-startup", action="store_true", help="Remove startup bat")
    args = parser.parse_args()

    if args.install_startup:
        install_startup()
        return
    if args.remove_startup:
        remove_startup()
        return
    run_service()


if __name__ == "__main__":
    main()
