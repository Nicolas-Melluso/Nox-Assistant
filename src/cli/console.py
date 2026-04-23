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
    # Mostrar banner solo si estamos en terminal actual
    import sys
    if sys.stdout.isatty():
        print_banner()
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
        Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
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




def run_console(once=False, external_api_test=False):
    print_banner()
    EXTERNAL_SERVICES = {
        # "my_service": {
        #     "base_url": "https://api.ejemplo.com",
        #     "headers": {"Authorization": "Bearer ..."}
        # }
    }
    engine = CoreEngine(external_services=EXTERNAL_SERVICES)
    is_tty = sys.stdout.isatty()
    line = "─" * 52 if is_tty else "-" * 52
    if external_api_test:
        print(f"{Fore.CYAN}Prueba de integración con API externa{Style.RESET_ALL}")
        service = input("Nombre del servicio externo: ").strip()
        endpoint = input("Endpoint (ej: /datos): ").strip()
        method = input("Método HTTP [GET/POST]: ").strip().upper() or "GET"
        params = input("Params (JSON, opcional): ").strip()
        data = input("Data (JSON, opcional): ").strip()
        import json
        try:
            params_dict = json.loads(params) if params else None
        except Exception:
            params_dict = None
        try:
            data_dict = json.loads(data) if data else None
        except Exception:
            data_dict = None
        try:
            result = engine.call_external_api(service, endpoint, params=params_dict, method=method, data=data_dict)
            print(f"{Fore.GREEN}Respuesta:{Style.RESET_ALL} {result}")
        except Exception as e:
            print(f"{Fore.RED}Error:{Style.RESET_ALL} {e}")
        return
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
    import inspect
    frame = inspect.currentframe().f_back
    args = frame.f_locals.get('args', None)
    once = getattr(args, 'once', False) if args else False
    external_api_test = getattr(args, 'external_api_test', False) if args else False
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
        run_console(once=once, external_api_test=external_api_test)
        return
    elif opcion == "salir" or opcion is None:
        print("Saliendo...")
        sys.exit(0)
    else:
        print(f"Opción seleccionada: {opcion}")
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
    parser.add_argument("--external-api-test", action="store_true", help="Prueba integración con API externa")
    parser.add_argument("--config", action="store_true", help="Panel de configuración de feature flags (CLI)")
    parser.add_argument("--config-spa", action="store_true", help="Abrir SPA de configuración de feature flags en el navegador")
    args = parser.parse_args()

    # Abrir SPA de configuración visual servida por FastAPI si el flag está activo
    if args.config_spa:
        from src.config.feature_flags import FeatureFlags
        import socket
        import subprocess
        import time
        import webbrowser
        import sys
        flags = FeatureFlags().list_flags()
        spa_enabled = False
        for interfaz in flags:
            for categoria in flags[interfaz]:
                cat_val = flags[interfaz][categoria]
                if isinstance(cat_val, dict) and 'spa_server_enabled' in cat_val:
                    spa_enabled = cat_val['spa_server_enabled']
        if not spa_enabled:
            print(f"{Fore.YELLOW}El servidor SPA está desactivado por feature flag 'spa_server_enabled'. Actívalo para usar la SPA.{Style.RESET_ALL}")
            return
        # Verifica si el puerto 8000 está ocupado
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        uvicorn_proc = None
        if not is_port_in_use(8000):
            print(f"{Fore.CYAN}Levantando API FastAPI en background...{Style.RESET_ALL}")
            uvicorn_proc = subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'src.api.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'
            ])
            # Espera a que levante
            for _ in range(20):
                if is_port_in_use(8000):
                    break
                time.sleep(0.3)
            else:
                print(f"{Fore.RED}No se pudo levantar FastAPI en el puerto 8000.{Style.RESET_ALL}")
                if uvicorn_proc:
                    uvicorn_proc.terminate()
                return
        print(f"{Fore.CYAN}Abriendo SPA de configuración de feature flags en http://localhost:8000/spa ...{Style.RESET_ALL}")
        webbrowser.open("http://localhost:8000/spa")
        try:
            input(f"\nPresiona Enter para cerrar la SPA y detener el servidor...")
        except KeyboardInterrupt:
            pass
        if uvicorn_proc:
            print(f"{Fore.YELLOW}Cerrando servidor FastAPI...{Style.RESET_ALL}")
            uvicorn_proc.terminate()
            uvicorn_proc.wait()
        return

    # Configuración de feature flags desde CLI estilo menú flechitas
    if args.config:
        from src.config.feature_flags import FeatureFlags
        from prompt_toolkit.application import Application
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout import Layout
        from prompt_toolkit.layout.containers import HSplit, Window
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.styles import Style as PTStyle
        import sys
        flags = FeatureFlags()
        style = PTStyle.from_dict({
            'selected': 'reverse bold fg:#ff0000',
            'on': 'fg:#00ff00 bold',
            'off': 'fg:#ff0000 bold',
        })

        def menu_interfaz():
            all_flags = flags.list_flags()
            interfaces = list(all_flags.keys()) + ['Salir']
            selected = [0]
            result = {'value': None}
            def get_menu_text():
                lines = []
                for idx, label in enumerate(interfaces):
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
                if selected[0] < len(interfaces) - 1:
                    selected[0] += 1
                event.app.invalidate()
            @kb.add('enter')
            def _(event):
                result['value'] = interfaces[selected[0]]
                event.app.exit()
            @kb.add('escape')
            def _(event):
                result['value'] = None
                event.app.exit()
            body = HSplit([
                Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
                Window(FormattedTextControl('Usa flechas y Enter para seleccionar interfaz (Esc para salir):'), height=1)
            ])
            app = Application(layout=Layout(body), key_bindings=kb, style=style, full_screen=False)
            try:
                app.run()
            except (KeyboardInterrupt, EOFError):
                return None
            return result['value']

        def menu_categoria(interfaz):
            all_flags = flags.list_flags()
            categorias = list(all_flags[interfaz].keys()) + ['Volver']
            selected = [0]
            result = {'value': None}
            def get_menu_text():
                lines = []
                for idx, label in enumerate(categorias):
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
                if selected[0] < len(categorias) - 1:
                    selected[0] += 1
                event.app.invalidate()
            @kb.add('enter')
            def _(event):
                result['value'] = categorias[selected[0]]
                event.app.exit()
            @kb.add('escape')
            def _(event):
                result['value'] = None
                event.app.exit()
            body = HSplit([
                Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
                Window(FormattedTextControl('Selecciona categoría (Esc para volver):'), height=1)
            ])
            app = Application(layout=Layout(body), key_bindings=kb, style=style, full_screen=False)
            try:
                app.run()
            except (KeyboardInterrupt, EOFError):
                return None
            return result['value']

        def menu_feature(interfaz, categoria):
            all_flags = flags.list_flags()
            feats = all_flags[interfaz][categoria]
            # Solo features booleanos
            if isinstance(feats, dict):
                features = [f for f in feats if isinstance(feats[f], bool)]
            else:
                features = []
            features += ['Volver']
            selected = [0]
            result = {'value': None}
            def get_menu_text():
                lines = []
                for idx, feature in enumerate(features):
                    if feature == 'Volver':
                        label = 'Volver'
                        style_frag = ''
                    else:
                        val = feats[feature]
                        if val:
                            label = f"{feature} [ON]"
                            style_frag = 'class:on'
                        else:
                            label = f"{feature} [OFF]"
                            style_frag = 'class:off'
                    if idx == selected[0]:
                        lines.append(('class:selected', f'> {label} <\n'))
                    elif feature != 'Volver':
                        lines.append((style_frag, f'  {label}\n'))
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
                if selected[0] < len(features) - 1:
                    selected[0] += 1
                event.app.invalidate()
            @kb.add('enter')
            def _(event):
                result['value'] = features[selected[0]]
                event.app.exit()
            @kb.add('escape')
            def _(event):
                result['value'] = None
                event.app.exit()
            body = HSplit([
                Window(FormattedTextControl(lambda: get_menu_text()), always_hide_cursor=True),
                Window(FormattedTextControl('Selecciona feature (Enter para alternar, Esc para volver):'), height=1)
            ])
            app = Application(layout=Layout(body), key_bindings=kb, style=style, full_screen=False)
            try:
                app.run()
            except (KeyboardInterrupt, EOFError):
                return None
            return result['value']

        # Menú principal
        while True:
            interfaz = menu_interfaz()
            if interfaz is None or interfaz == 'Salir':
                break
            while True:
                categoria = menu_categoria(interfaz)
                if categoria is None or categoria == 'Volver':
                    break
                while True:
                    feature = menu_feature(interfaz, categoria)
                    if feature is None or feature == 'Volver':
                        break
                    # Alternar valor
                    all_flags = flags.list_flags()
                    actual = all_flags[interfaz][categoria][feature]
                    nuevo = not actual
                    flags.set_flag(interfaz, categoria, feature, nuevo)
                    print(f"{'Habilitado' if nuevo else 'Deshabilitado'}: {interfaz} / {categoria} / {feature}")
        return

    # Si solo se pide ayuda, argparse la muestra y sale automáticamente
    # Si no se pide --default, mostrar menú y ejecutar en terminal actual
    if not args.default:
        opcion = show_menu()
        if opcion == "cmd":
            print("Ejecutando en CMD...")
            abs_cwd = os.path.abspath(os.getcwd())
            script = f"python -m src.cli --default"
            cmd_command = f'start "" cmd /K "cd /d {abs_cwd} && {script}"'
            print(f"[DEBUG] Comando CMD generado: {cmd_command}")
            subprocess.Popen(cmd_command, shell=True)
            print("Se abrió una nueva ventana de CMD.")
            sys.exit(0)
        elif opcion == "powershell":
            print("Ejecutando en PowerShell...")
            abs_cwd = os.path.abspath(os.getcwd())
            script = f"python -m src.cli --default"
            ps_command = f'start powershell -NoExit -Command "cd {abs_cwd}; {script}"'
            print(f"[DEBUG] Comando PowerShell generado: {ps_command}")
            subprocess.Popen(ps_command, shell=True)
            print("Se abrió una nueva ventana de PowerShell.")
            sys.exit(0)
        elif opcion == "bash":
            script = f"python -m src.cli --default"
            cwd = os.getcwd()
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
            print("Ejecutando en la terminal actual...")
            run_console(once=args.once, external_api_test=args.external_api_test)
            return
        elif opcion == "salir" or opcion is None:
            print("Saliendo...")
            sys.exit(0)
        else:
            print(f"Opción seleccionada: {opcion}")
            sys.exit(0)
    else:
        run_console(once=args.once, external_api_test=args.external_api_test)

if __name__ == "__main__":
    main()
