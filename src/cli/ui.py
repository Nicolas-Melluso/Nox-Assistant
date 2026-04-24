from typing import Any, Optional, Sequence, Tuple, List
import os
import sys

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    Fore = None
    Style = None

try:
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import HSplit
    from prompt_toolkit.widgets import RadioList
    from prompt_toolkit.shortcuts import choice as pt_choice
except Exception:
    Application = None
    pt_choice = None

def print_banner() -> None:
    # Modo no interactivo (piped / redirected)
    if not sys.stdout.isatty():
        print("NOX CLI v0.4.0 (modo no interactivo)")
        return

    # Si colorama está disponible, usar colores; si no, caer en plano
    use_color = bool(Fore and Style)

    if use_color:
        try:
            print(f"{Fore.RED}{Style.BRIGHT}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT}║   NOX CLI v0.4.0                                   ║{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print()
            print(f"{Fore.RED}{Style.BRIGHT} ███╗   ██╗ ██████╗ ██╗  ██╗{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT} ████╗  ██║██╔═══██╗╚██╗██╔╝{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT} ██╔██╗ ██║██║   ██║ ╚███╔╝ {Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT} ██║╚██╗██║██║   ██║ ██╔██╗ {Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT} ██║ ╚████║╚██████╔╝██╔╝ ██╗{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT} ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝{Style.RESET_ALL}")
        except Exception:
            use_color = False

    if not use_color:
        # Fallback plain text banner
        print("╔════════════════════════════════════════════════════╗")
        print("║   NOX CLI v0.4.0                                   ║")
        print("╚════════════════════════════════════════════════════╝")
        print()
        print(" ███╗   ██╗ ██████╗ ██╗  ██╗")
        print(" ████╗  ██║██╔═══██╗╚██╗██╔╝")
        print(" ██╔██╗ ██║██║   ██║ ╚███╔╝ ")
        print(" ██║╚██╗██║██║   ██║ ██╔██╗ ")
        print(" ██║ ╚████║╚██████╔╝██╔╝ ██╗")
        print(" ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝")

    cwd = os.getcwd()
    if not (cwd.endswith("custom-voice-assistant") or cwd.endswith("custom-voice-assistant/")):
        if use_color:
            print(f"{Fore.WHITE}Usa: cd custom-voice-assistant && python -m src.cli{Style.RESET_ALL}\n")
        else:
            print("Usa: cd custom-voice-assistant && python -m src.cli\n")

def show_menu(options: Optional[Sequence[Tuple[Any, str]]] = None, title: str = "Selecciona opción") -> Optional[Any]:
    if options is None:
        options = [
            ("cmd", "CMD"),
            ("powershell", "PowerShell"),
            ("bash", "Bash"),
            ("actual", "Terminal actual"),
            ("salir", "Salir"),
        ]
    # Prefer prompt_toolkit.shortcuts.choice when available: provides
    # framed UI, proper Enter handling and Escape/C-c interrupt.
    if pt_choice is not None:
        try:
            return pt_choice(
                message="Selecciona una opción:",
                options=list(options),
                bottom_toolbar="Usa ↑/↓ para moverte, Enter para elegir, Esc/Ctrl-C para salir.",
                show_frame=True,
                enable_interrupt=True,
            )
        except Exception:
            pass

    if Application is not None:
        try:
            radio = RadioList(values=list(options))
            kb = KeyBindings()

            @kb.add("enter")
            def _enter(event):
                event.app.exit(result=radio.current_value)

            @kb.add("escape")
            @kb.add("c-c")
            def _abort(event):
                event.app.exit(result=None)

            layout = Layout(HSplit([radio]), focused_element=radio)
            app = Application(layout=layout, key_bindings=kb, full_screen=False)
            return app.run()
        except Exception:
            pass
    print("Opciones:")
    for val, label in options:
        print(f"  {val}: {label}")
    try:
        return input("Opción > ").strip()
    except EOFError:
        return None

def format_entities(entities: Any) -> str:
    if not entities:
        return "  (ninguna)"
    lines: List[str] = []

    # Caso especial: salida del pipeline 'ensamblar_output' -> lista de frases con 'frase' y 'entidades'
    if isinstance(entities, (list, tuple)) and entities and isinstance(entities[0], dict) and (
        'frase' in entities[0] or 'entidades' in entities[0] or 'entities' in entities[0]
    ):
        for item in entities:
            frase = item.get('frase') or item.get('sentence') or None
            ents = item.get('entidades') or item.get('entities') or []
            if frase:
                lines.append(f"Frase: {frase}")
            if not ents:
                lines.append("  (ninguna)")
            else:
                for e in ents:
                    if isinstance(e, dict):
                        label = e.get('label') or e.get('entity') or e.get('type') or 'entity'
                        text_val = e.get('text') or e.get('value') or ''
                        extras: List[str] = []
                        start = e.get('start', None)
                        end = e.get('end', None)
                        if start is not None or end is not None:
                            extras.append(f"pos={start}:{end}")
                        conf = e.get('confidence') or e.get('score')
                        if conf is not None:
                            try:
                                extras.append(f"conf={float(conf):.2f}")
                            except Exception:
                                extras.append(f"conf={conf}")
                        role = e.get('role') or e.get('role_label')
                        if role:
                            extras.append(f"role={role}")
                        extras_text = f" ({', '.join(extras)})" if extras else ""
                        lines.append(f" - {label}: {text_val}{extras_text}")
                    else:
                        lines.append(f" - {e}")
            lines.append("")
        return "\n".join(lines).rstrip()

    def _format_item(item: Any) -> List[str]:
        out: List[str] = []
        if isinstance(item, (str, int, float)):
            out.append(f" - {item}")
            return out
        if isinstance(item, dict):
            name = item.get("entity") or item.get("type") or item.get("name") or "entity"
            value = item.get("value") or item.get("text") or ""
            start = item.get("start", item.get("start_pos", None))
            end = item.get("end", item.get("end_pos", None))
            conf = item.get("confidence", item.get("score", None))
            extras: List[str] = []
            if start is not None or end is not None:
                extras.append(f"pos={start}:{end}")
            if conf is not None:
                try:
                    extras.append(f"conf={float(conf):.2f}")
                except Exception:
                    extras.append(f"conf={conf}")
            role = item.get("role") or item.get("role_label")
            if role:
                extras.append(f"role={role}")
            extras_text = f" ({', '.join(extras)})" if extras else ""
            out.append(f" - {name}: {value}{extras_text}")
            return out
        if isinstance(item, (list, tuple, set)):
            for sub in item:
                out.extend(_format_item(sub))
            return out
        try:
            name = getattr(item, "entity", None) or getattr(item, "type", None) or getattr(item, "name", None) or item.__class__.__name__
            value = getattr(item, "value", None) or getattr(item, "text", None) or str(item)
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            conf = getattr(item, "confidence", None) or getattr(item, "score", None)
            extras: List[str] = []
            if start is not None or end is not None:
                extras.append(f"pos={start}:{end}")
            if conf is not None:
                try:
                    extras.append(f"conf={float(conf):.2f}")
                except Exception:
                    extras.append(f"conf={conf}")
            extras_text = f" ({', '.join(extras)})" if extras else ""
            out.append(f" - {name}: {value}{extras_text}")
            return out
        except Exception:
            out.append(f" - {repr(item)}")
            return out

    if isinstance(entities, dict):
        for k, v in entities.items():
            if isinstance(v, (list, tuple, set)):
                lines.append(f" - {k}:")
                for sub in v:
                    for l in _format_item(sub):
                        lines.append("    " + l.lstrip(" -"))
            else:
                for l in _format_item(v):
                    lines.append(f" - {k}: {l.lstrip(' -')}")
        return "\n".join(lines)

    if isinstance(entities, (list, tuple, set)):
        for e in entities:
            for l in _format_item(e):
                lines.append(l)
        return "\n".join(lines)

    for l in _format_item(entities):
        lines.append(l)
    return "\n".join(lines)
