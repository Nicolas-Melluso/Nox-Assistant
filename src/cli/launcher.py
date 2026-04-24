import os
import sys
import subprocess
from src.cli.ui import show_menu


def launch_new_terminal(args=None, cwd=None):
    """Intento de abrir la CLI en otra terminal de forma segura.
    - En 'actual' ejecuta en la terminal actual.
    - En Windows intenta abrir CMD o PowerShell con CREATE_NEW_CONSOLE.
    - En otros sistemas muestra instrucciones o intenta abrir terminal emulators.
    """
    if cwd is None:
        cwd = os.getcwd()
    opcion = show_menu()
    once = getattr(args, 'once', False) if args else False
    external_api_test = getattr(args, 'external_api_test', False) if args else False

    if opcion == 'actual' or opcion is None:
        # Ejecutar en la terminal actual: crear engine y delegar al runner
        try:
            # Permitir forzar engine simulado con MOCK_ENGINE=1
            if os.environ.get('MOCK_ENGINE', '0') == '1':
                raise RuntimeError('mock engine')
            from src.core.engine import CoreEngine
            engine = CoreEngine()
        except Exception:
            class DummyEngine:
                def predict_intent(self, text):
                    return {'intent': 'echo', 'confidence': 1.0, 'entities': [], 'text': text}
                def call_external_api(self, *a, **k):
                    return {'ok': True}
            engine = DummyEngine()
        from src.cli.runner import run_console
        return run_console(engine, once=once, external_api_test=external_api_test)

    # Construir comando base
    script = [sys.executable, '-m', 'src.cli', '--default']

    if opcion == 'cmd':
        if os.name == 'nt':
            try:
                subprocess.Popen(script, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return None
            except Exception as e:
                print(f"No se pudo abrir CMD automáticamente: {e}\nEjecuta manualmente: {' '.join(script)}")
                return None
        else:
            print(f"Para abrir en CMD ejecuta manualmente:\n  {' '.join(script)}")
            return None

    if opcion == 'powershell':
        if os.name == 'nt':
            try:
                ps_cmd = ['powershell.exe', '-NoExit', '-Command', f"& '{sys.executable}' -m src.cli --default"]
                subprocess.Popen(ps_cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return None
            except Exception as e:
                print(f"No se pudo abrir PowerShell automáticamente: {e}\nEjecuta manualmente: {' '.join(script)}")
                return None
        else:
            print(f"Para abrir en PowerShell ejecuta manualmente:\n  {' '.join(script)}")
            return None

    if opcion == 'bash':
        if os.name != 'nt':
            terminals = [
                ['gnome-terminal', '--'],
                ['x-terminal-emulator', '-e'],
                ['konsole', '-e'],
                ['xfce4-terminal', '-e'],
                ['lxterminal', '-e'],
                ['mate-terminal', '-e'],
                ['xterm', '-e'],
            ]
            for term in terminals:
                try:
                    subprocess.Popen(term + [' '.join(script)])
                    return None
                except FileNotFoundError:
                    continue
            print(f"No se encontró un emulador de terminal compatible. Ejecuta manualmente: {' '.join(script)}")
            return None
        else:
            print(f"En Windows, para bash ejecuta manualmente:\n  {' '.join(script)}")
            return None

    if opcion == 'salir':
        print('Saliendo...')
        return None

    print(f"Opción no implementada: {opcion}")
    return None
