from __future__ import annotations
def show_menu():
    """Muestra el menú y retorna la opción elegida."""
    import platform
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import HSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.styles import Style
    system = platform.system()
    if system == "Windows":
        opciones = [
            ("powershell", "PowerShell (nueva ventana)"),
            ("cmd", "CMD (nueva ventana)"),
            ("actual", "Terminal actual (no abrir nueva ventana)"),
            ("salir", "Salir")
        ]
    else:
        opciones = [
            ("bash", "Bash/Terminal (nueva ventana)"),
            ("actual", "Terminal actual (no abrir nueva ventana)"),
            ("salir", "Salir")
        ]
    menu_items = opciones
    selected = [0]
    result = {'value': None}
    def get_menu_text():
        lines = []
        for idx, (value, label) in enumerate(menu_items):
            if idx == selected[0]:
                lines.append(('class:selected', f'> {label} <\n'))
            else:
                lines.append(('', f'  {label}\n'))
        return lines
    kb = KeyBindings()
    @kb.add('up')
    def _(event):
        if selected[0] > 0:
            selected[0] -= 1
        event.app.invalidate()
    @kb.add('down')
    def _(event):
        if selected[0] < len(menu_items) - 1:
            selected[0] += 1
        event.app.invalidate()
    @kb.add('enter')
    def _(event):
        result['value'] = menu_items[selected[0]][0]
        event.app.exit()
    @kb.add('escape')
    def _(event):
        result['value'] = None
        event.app.exit()
    style = Style.from_dict({'selected': 'reverse bold fg:#ff0000'})
    body = HSplit([
        Window(height=1, char=' '),
        Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
        Window(height=1, char=' '),
        Window(FormattedTextControl('Usa flechas y Enter para seleccionar (Esc para cancelar):'), height=1)
    ])
    app = Application(
        layout=Layout(body),
        key_bindings=kb,
        style=style,
        full_screen=False,
    )
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo por Ctrl+C o Ctrl+D...")
        sys.exit(0)
    return result['value']
"""Simple console CLI to exercise CoreEngine for Fase 0"""
from typing import Any
import sys
import os
import platform
import subprocess

import argparse
import os
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style as PTStyle

import sys
import os
# Añadir src al sys.path si no está
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from src.core.engine import CoreEngine
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
except ImportError:
    class Dummy:
        RESET = RESET_ALL = BRIGHT = DIM = NORMAL = ''
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ''
    Fore = Style = Dummy()

def format_entities(entities):
    if not entities:
        return f"{Fore.WHITE}Ninguna{Style.RESET_ALL}"
    lines = []
    for ent in entities:
        label = ent.get('label', 'ENT')
        text = ent.get('text', str(ent))
        extra = ''
        # Mostrar cantidad y unidad si existen
        if 'cantidad' in ent:
            extra += f" | cantidad: {ent['cantidad']}"
        if 'unidad' in ent:
            extra += f" | unidad: {ent['unidad']}"
        lines.append(f"- {Fore.GREEN}{label}{Style.RESET_ALL}: {Fore.CYAN}{text}{Style.RESET_ALL}{extra}")
    return '\n'.join(lines)

def print_banner():
    import sys
    if not sys.stdout.isatty():
        print("NOX CLI v0.4.0 (modo no interactivo)")
        return
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
    cwd = os.getcwd()
    if not (cwd.endswith("custom-voice-assistant") or cwd.endswith("custom-voice-assistant/")):
        print(f"{Fore.WHITE}Usa: cd custom-voice-assistant && python -m src.cli{Style.RESET_ALL}\n")




def run_console(once=False):
    print_banner()
    engine = CoreEngine()
    is_tty = sys.stdout.isatty()
    line = "─" * 52 if is_tty else "-" * 52
    if once:
        try:
            if sys.stdin.isatty():
                text = input().strip()
            else:
                text = sys.stdin.readline().strip()
        except EOFError:
            print(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            return
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            sys.exit(0)
        if not text:
            return
        result = engine.predict_intent(text)
        intent = result.get('intent', 'unknown')
        conf = result.get('confidence', 0.0)
        entities = result.get('entities', [])
        color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)
        print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Intención:{Style.RESET_ALL} {color}{intent}{Style.RESET_ALL}   {Fore.CYAN}Confianza:{Style.RESET_ALL} {color}{conf:.2f}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Entidades:{Style.RESET_ALL}\n{format_entities(entities)}")
        print(f"{Fore.WHITE}{line}{Style.RESET_ALL}\n")
        return
    while True:
        try:
            text = input(f"{Fore.BLUE}{Style.BRIGHT}🗣️  Frase > {Style.RESET_ALL}").strip()
        except EOFError:
            print(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            sys.exit(0)
        if not text:
            continue
        if text.lower() in ("exit", "quit", "salir"):
            print(f"{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        result = engine.predict_intent(text)
        intent = result.get('intent', 'unknown')
        conf = result.get('confidence', 0.0)
        entities = result.get('entities', [])
        color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)
        print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Intención:{Style.RESET_ALL} {color}{intent}{Style.RESET_ALL}   {Fore.CYAN}Confianza:{Style.RESET_ALL} {color}{conf:.2f}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Entidades:{Style.RESET_ALL}\n{format_entities(entities)}")
        print(f"{Fore.WHITE}{line}{Style.RESET_ALL}\n")
    return result['value']

def launch_new_terminal():
    print_banner()
    script = f"python -m src.cli --default"
    cwd = os.getcwd()
    opcion = show_menu()
    if opcion == "cmd":
        print("Ejecutando en CMD...")
        abs_cwd = os.path.abspath(cwd)
        # Comando corregido: comillas bien ubicadas y ejecución directa
        cmd_command = f'start "" cmd /K "cd /d {abs_cwd} && {script}"'
        print(f"[DEBUG] Comando CMD generado: {cmd_command}")
        subprocess.Popen(cmd_command, shell=True)
        print("Se abrió una nueva ventana de CMD.")
        sys.exit(0)
    elif opcion == "powershell":
        print("Ejecutando en PowerShell...")
        abs_cwd = os.path.abspath(cwd)
        ps_command = f'start powershell -NoExit -Command "cd {abs_cwd}; {script}"'
        print(f"[DEBUG] Comando PowerShell generado: {ps_command}")
        subprocess.Popen(ps_command, shell=True)
        print("Se abrió una nueva ventana de PowerShell.")
        sys.exit(0)
    elif opcion == "bash":
        terminals = [
            ["gnome-terminal", "--"],
            ["x-terminal-emulator", "-e"],
            ["konsole", "-e"],
            ["xfce4-terminal", "-e"],
            ["lxterminal", "-e"],
            ["mate-terminal", "-e"],
            ["xterm", "-e"],
        ]
        for term in terminals:
            try:
                subprocess.Popen(term + [f"cd '{cwd}'; {script}"])
                print(f"Se abrió una nueva ventana de terminal: {' '.join(term)}")
                sys.exit(0)
            except FileNotFoundError:
                continue
        print("No se encontró un emulador de terminal compatible. Ejecuta manualmente: " + script)
        sys.exit(1)
    elif opcion == "actual":
        def is_vscode_terminal():
            return (
                "WT_SESSION" in os.environ or
                ("TERM_PROGRAM" in os.environ and os.environ["TERM_PROGRAM"].lower() == "vscode")
            )
        print("Ejecutando en la terminal actual...")
        run_console()
        return
    elif opcion == "salir" or opcion is None:
        print("Saliendo...")
        sys.exit(0)
    else:
        print(f"Opción seleccionada: {opcion}")
        sys.exit(0)

    @kb.add('down')
    def _(event):
        if selected[0] < len(menu_items) - 1:
            selected[0] += 1
        event.app.invalidate()

    @kb.add('enter')
    def _(event):
        result['value'] = menu_items[selected[0]][0]
        event.app.exit()

    @kb.add('escape')
    def _(event):
        result['value'] = None
        event.app.exit()

    style = Style.from_dict({
        'selected': 'reverse bold fg:#ff0000',
    })

    body = HSplit([
        Window(height=1, char=' '),
        Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
        Window(height=1, char=' '),
        Window(FormattedTextControl('Usa flechas y Enter para seleccionar (Esc para cancelar):'), height=1)
    ])

    app = Application(
        layout=Layout(body),
        key_bindings=kb,
        style=style,
        full_screen=False,
    )
    app.run()

    if result['value'] is not None:
        if result['value'] == "cmd":
            print("Ejecutando en CMD...")
            subprocess.Popen(["cmd.exe", "/K", f"cd /d {cwd} && {script}"], shell=True)
            print("Se abrió una nueva ventana de CMD.")
            sys.exit(0)
        elif result['value'] == "powershell":
            print("Ejecutando en PowerShell...")
            subprocess.Popen(["powershell", "-NoExit", f"cd '{cwd}'; {script}"], shell=True)
            print("Se abrió una nueva ventana de PowerShell.")
            sys.exit(0)
        elif result['value'] == "bash":
            terminals = [
                ["gnome-terminal", "--"],
                ["x-terminal-emulator", "-e"],
                ["konsole", "-e"],
                ["xfce4-terminal", "-e"],
                ["lxterminal", "-e"],
                ["mate-terminal", "-e"],
                ["xterm", "-e"],
            ]
            for term in terminals:
                try:
                    subprocess.Popen(term + [f"cd '{cwd}'; {script}"])
                    print(f"Se abrió una nueva ventana de terminal: {' '.join(term)}")
                    sys.exit(0)
                except FileNotFoundError:
                    continue
            print("No se encontró un emulador de terminal compatible. Ejecuta manualmente: " + script)
            sys.exit(1)
        elif result['value'] == "actual":
            print("Ejecutando en la terminal actual...")
            run_console()
            return
        elif result['value'] == "salir":
            print("Saliendo...")
            sys.exit(0)
        else:
            print(f"Opción seleccionada: {result['value']}")
            sys.exit(0)
    else:
        print("Selección cancelada.")
        sys.exit(0)


def print_help():
    print(f"{Fore.CYAN}Uso:{Style.RESET_ALL} python -m src.cli [--help]")
    print(f"{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
    print(f"  --help     Muestra esta ayuda y sale.")


# Mover main() después de launch_new_terminal()
def main():
    print("[DEBUG] custom-voice-cli entry point ejecutado correctamente.")
    parser = argparse.ArgumentParser(description="NOX CLI - Asistente de voz modular")
    parser.add_argument("--default", action="store_true", help="Ejecutar directamente en la terminal actual (sin menú)")
    parser.add_argument("--once", action="store_true", help="Procesar solo una línea de stdin y terminar (modo test)")
    args = parser.parse_args()

    # Si solo se pide ayuda, argparse la muestra y sale automáticamente
    if not args.default:
        launch_new_terminal()
    run_console(once=args.once)

if __name__ == "__main__":
    main()
