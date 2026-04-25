import sys
import argparse

from src.cli.ui import print_banner, show_menu
from src.cli.runner import run_console
from src.cli.launcher import launch_new_terminal
from src.cli.config_cli import run_feature_flags_ui


def main(argv=None) -> int:
    print_banner()
    parser = argparse.ArgumentParser(description="NOX CLI - Asistente de voz modular")
    parser.add_argument("--default", action="store_true", help="Ejecutar directamente en la terminal actual (sin menú)")
    parser.add_argument("--once", action="store_true", help="Procesar solo una línea de stdin y terminar (modo test)")
    parser.add_argument("--external-api-test", action="store_true", help="Prueba integración con API externa")
    parser.add_argument("--config", action="store_true", help="Panel de configuración de feature flags (CLI)")
    parser.add_argument("--config-spa", action="store_true", help="Abrir SPA de configuración de feature flags en el navegador")
    parser.add_argument("--verbose", action="store_true", help="Mostrar intent, confianza, entidades y skill")
    args = parser.parse_args(argv)

    # SPA de configuración (mantener comportamiento previo)
    if args.config_spa:
        from src.config.feature_flags import FeatureFlags
        import socket
        import subprocess
        import time
        import webbrowser

        flags = FeatureFlags().list_flags()
        spa_enabled = False
        for interfaz in flags:
            for categoria in flags[interfaz]:
                cat_val = flags[interfaz][categoria]
                if isinstance(cat_val, dict) and 'spa_server_enabled' in cat_val:
                    spa_enabled = cat_val['spa_server_enabled']
        if not spa_enabled:
            print("El servidor SPA está desactivado por feature flag 'spa_server_enabled'. Actívalo para usar la SPA.")
            return 1

        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0

        uvicorn_proc = None
        if not is_port_in_use(8000):
            print("Levantando API FastAPI en background...")
            uvicorn_proc = subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'src.api.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'
            ])
            for _ in range(20):
                if is_port_in_use(8000):
                    break
                time.sleep(0.3)
            else:
                print("No se pudo levantar FastAPI en el puerto 8000.")
                if uvicorn_proc:
                    uvicorn_proc.terminate()
                return 1
        print("Abriendo SPA de configuración de feature flags en http://localhost:8000/spa ...")
        webbrowser.open("http://localhost:8000/spa")
        try:
            input("\nPresiona Enter para cerrar la SPA y detener el servidor...")
        except KeyboardInterrupt:
            pass
        if uvicorn_proc:
            uvicorn_proc.terminate()
            uvicorn_proc.wait()
        return 0

    # Interfaz de configuración con prompt_toolkit (delegada)
    if args.config:
        from src.config.feature_flags import FeatureFlags
        flags = FeatureFlags()
        run_feature_flags_ui(flags)
        return 0

    # Modo directo: crear engine e invocar runner
    if args.default:
        try:
            from src.core.engine import CoreEngine
            engine = CoreEngine()
        except Exception:
            engine = None
        if engine is None:
            # fallback dummy engine to allow local tests
            class DummyEngine:
                def predict_intent(self, text):
                    return {'intent': 'echo', 'confidence': 1.0, 'entities': [], 'text': text}
                def call_external_api(self, *a, **k):
                    return {'ok': True}
            engine = DummyEngine()
        run_console(
            engine,
            input_func=input,
            output_func=print,
            once=args.once,
            external_api_test=args.external_api_test,
            verbose=args.verbose,
        )
        return 0

    # Si no --default, delegar a launcher que decide dónde ejecutar
    launch_new_terminal(args=args, cwd=None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
