"""
autonomous_nox.py
CLI para AutonomousNox — agente LLM que planifica y ejecuta flujos en el PC.

Uso:
    python scripts/autonomous_nox.py
    python scripts/autonomous_nox.py --dry-run     # muestra pasos sin ejecutar
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Asegurar que src/ este en el path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.autonomous_agent import run_agent
from src.skills.policies import get_policy
from src.skills.voice_offline import speak_text, start_voice_control, stop_voice_control, voice_status

# ── ANSI colors (terminal NOX: negro + rojo + blanco) ─────────────────────────
RED    = "\033[91m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BANNER = f"""{RED}{BOLD}
 ███╗   ██╗ ██████╗ ██╗  ██╗
 ████╗  ██║██╔═══██╗╚██╗██╔╝
 ██╔██╗ ██║██║   ██║ ╚███╔╝ 
 ██║╚██╗██║██║   ██║ ██╔██╗ 
 ██║ ╚████║╚██████╔╝██╔╝ ██╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝
{RESET}{GRAY} Autonomous Agent — Local First{RESET}
"""


def _on_step(tool: str, args: dict, result: dict) -> None:
    status = f"{RED}✗{RESET}" if "error" in result else f"{WHITE}✓{RESET}"
    args_str = ", ".join(f"{k}={v!r}" for k, v in args.items()) if args else ""
    print(f"  {status} {WHITE}{tool}{RESET}({GRAY}{args_str}{RESET})")
    if "error" in result:
        print(f"    {RED}Error: {result['error']}{RESET}")


def _on_confirm(tool: str, args: dict, policy: dict) -> bool:
    risk = str(policy.get("risk", "medium"))
    reason = str(policy.get("reason", "accion sensible"))
    print(f"{RED}[CONFIRM]{RESET} Tool: {tool} | Riesgo: {risk} | Motivo: {reason}")
    print(f"{GRAY}Args: {args}{RESET}")
    ans = input(f"{WHITE}Permitir ejecucion? (s/n): {RESET}").strip().lower()
    return ans in {"s", "si", "y", "yes"}


def _execute_instruction(user_input: str, auto_confirm: bool = False, source: str = "texto") -> str | None:
    if not user_input:
        return None
    print(f"{GRAY}Procesando ({source})...{RESET}")
    try:
        def _auto_confirm_safe(tool: str, args: dict, policy: dict) -> bool:
            # El modo auto-confirm nunca debe ejecutar acciones de riesgo alto/critico.
            pol = policy or get_policy(tool)
            risk = str(pol.get("risk", "medium")).lower()
            return risk not in {"high", "critical"}

        confirm_cb = _auto_confirm_safe if auto_confirm else _on_confirm
        result = run_agent(user_input, on_step=_on_step, on_confirm=confirm_cb)
    except ValueError as e:
        print(f"\n{RED}Error de configuracion:{RESET} {e}")
        print(f"{GRAY}Revisa .env (NOX_PROVIDER_PRIORITY, GITHUB_*, OLLAMA_*).{RESET}\n")
        return None
    except Exception as e:
        print(f"\n{RED}Error:{RESET} {e}\n")
        return None

    print(f"\n{WHITE}{BOLD}NOX:{RESET} {result.message}")
    if result.steps:
        tools = ", ".join(result.tools_used)
        print(f"{GRAY}  Herramientas usadas: {tools}{RESET}")
        print(f"{GRAY}  Providers usados: {', '.join(result.providers_used)}{RESET}")
        print(f"{GRAY}  Run ID: {result.run_id}{RESET}")
    print()
    return result.message


def _is_probable_voice_command(cmd: str) -> bool:
    text = (cmd or "").strip().lower()
    if not text:
        return False
    text = re.sub(r"\s+", " ", text)
    tokens = text.split(" ")
    if len(tokens) < 2:
        return False
    unique = set(tokens)
    if len(unique) == 1:
        return False
    # evita ruido tipo "noc noc noc" o similares
    if len(tokens) >= 3 and max(tokens.count(t) for t in unique) / len(tokens) > 0.7:
        return False
    return True


def _is_pronunciation_probe(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    # Evita spamear: muestra parciales con largo minimo y cambios reales.
    return len(t) >= 3

def main() -> None:
    parser = argparse.ArgumentParser(description="NOX Autonomous Agent")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar plan sin ejecutar")
    parser.add_argument("--auto-confirm", action="store_true", help="Aceptar automaticamente acciones sensibles")
    parser.add_argument("--voice", action="store_true", help="Activar escucha offline por wake word")
    parser.add_argument("--wake-word", default=os.getenv("NOX_WAKE_WORD", "nox"), help="Wake word para activar escucha")
    args = parser.parse_args()

    priority = os.getenv("NOX_PROVIDER_PRIORITY", "github,ollama")
    github_model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    py_ver = sys.version_info

    print(BANNER)
    if py_ver >= (3, 14):
        print(f"{RED}Aviso:{RESET} Python {py_ver.major}.{py_ver.minor} detectado. Se recomienda Python 3.11/3.12 para mayor estabilidad de voz/ML.")
    print(f"{GRAY}Prioridad providers: {priority}{RESET}")
    print(f"{GRAY}Models: github={github_model} | ollama={ollama_model}{RESET}")

    if args.voice:
        _last_partial = {"text": ""}

        def _voice_on_wake(raw_text: str) -> None:
            print(f"{GRAY}[VOICE] Wake word detectada: {raw_text}{RESET}")

        def _voice_on_partial(text: str) -> None:
            if not _is_pronunciation_probe(text):
                return
            if text == _last_partial["text"]:
                return
            _last_partial["text"] = text
            print(f"{GRAY}[VOICE][partial] {text}{RESET}")

        def _voice_on_command(cmd: str) -> None:
            print(f"{GRAY}[VOICE] Comando detectado: {cmd}{RESET}")
            if not _is_probable_voice_command(cmd):
                print(f"{GRAY}[VOICE] Ignorado por baja confianza semantica.{RESET}")
                return
            # Evita bloquear el input principal con confirmaciones de voz y confirma de forma hablada.
            message = _execute_instruction(cmd, auto_confirm=True, source="voz")
            if message:
                speak_text(message)
                speak_text("Listo. Si quieres otro comando, di Nox.")

        info = start_voice_control(
            on_command=_voice_on_command,
            on_wake=_voice_on_wake,
            on_partial=_voice_on_partial,
            wake_word=args.wake_word,
        )
        if info.get("started"):
            st = voice_status()
            print(
                f"{GRAY}Voice ON: di '{info.get('wake_word', args.wake_word)}' y luego tu comando (ventana {info.get('listen_window_sec', 8)}s).{RESET}"
            )
            print(f"{GRAY}Aliases wake: {', '.join(info.get('wake_aliases', []))}{RESET}")
            print(
                f"{GRAY}Voice input: device={st.get('voice_device')} | sample_rate={st.get('voice_sample_rate')}{RESET}"
            )
        else:
            print(f"{RED}Voice no iniciado:{RESET} {info.get('message')}")
            st = voice_status()
            if st.get("last_error"):
                print(f"{RED}Detalle:{RESET} {st['last_error']}")
            print(f"{GRAY}Tip: ejecuta 'python scripts/setup_vosk_es.py' y luego 'python scripts/test_vosk_microphone.py'.{RESET}")

    print(f"{GRAY}Escribe tu instruccion. Ctrl+C o 'exit' para salir.{RESET}\n")

    while True:
        try:
            user_input = input(f"{RED}>{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GRAY}Hasta luego.{RESET}")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "salir", "quit"}:
            if args.voice:
                stop_voice_control()
            print(f"{GRAY}Hasta luego.{RESET}")
            break

        _execute_instruction(user_input, auto_confirm=args.auto_confirm, source="texto")


if __name__ == "__main__":
    main()
