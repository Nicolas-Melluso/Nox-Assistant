import sys
import json
from typing import Optional, Callable
from colorama import Fore, Style
from src.cli.ui import format_entities


def run_console(engine, input_func: Callable = input, output_func: Callable = print, once: bool = False, external_api_test: bool = False) -> Optional[dict]:
    """Ejecuta el bucle interactivo usando el `engine` proporcionado.
    El `engine` debe implementar `predict_intent(text)` y `call_external_api(...)`.
    """
    is_tty = sys.stdout.isatty()
    line = "─" * 52 if is_tty else "-" * 52

    if external_api_test:
        output_func(f"{Fore.CYAN}Prueba de integración con API externa{Style.RESET_ALL}")
        service = input_func("Nombre del servicio externo: ").strip()
        endpoint = input_func("Endpoint (ej: /datos): ").strip()
        method = input_func("Método HTTP [GET/POST]: ").strip().upper() or "GET"
        params = input_func("Params (JSON, opcional): ").strip()
        data = input_func("Data (JSON, opcional): ").strip()
        try:
            params_dict = json.loads(params) if params else None
        except Exception:
            params_dict = None
        try:
            data_dict = json.loads(data) if data else None
        except Exception:
            data_dict = None
        result = engine.call_external_api(service, endpoint, params=params_dict, method=method, data=data_dict)
        output_func(f"{Fore.GREEN}Respuesta:{Style.RESET_ALL} {result}")
        return result

    if once:
        try:
            if sys.stdin.isatty():
                text = input_func().strip()
            else:
                text = sys.stdin.readline().strip()
        except (EOFError, KeyboardInterrupt):
            output_func(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            return None
        if not text:
            return None
        result = engine.predict_intent(text)
        intent = result.get('intent', 'unknown')
        conf = result.get('confidence', 0.0)
        entities = result.get('entities', [])
        color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)
        output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        output_func(f"{Fore.CYAN}Intención:{Style.RESET_ALL} {color}{intent}{Style.RESET_ALL}   {Fore.CYAN}Confianza:{Style.RESET_ALL} {color}{conf:.2f}{Style.RESET_ALL}")
        output_func(f"{Fore.CYAN}Entidades:{Style.RESET_ALL}\n{format_entities(entities)}")
        output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}\n")
        # Ejecutar acción asociada a la intención si el engine lo soporta
        try:
            if hasattr(engine, 'execute_skill'):
                action_res = engine.execute_skill(result)
                if action_res:
                    output_func(f"{Fore.MAGENTA}Acción ejecutada:{Style.RESET_ALL} {action_res}")
        except Exception as e:
            output_func(f"{Fore.RED}Error al ejecutar acción: {e}{Style.RESET_ALL}")
        return result

    while True:
        try:
            prompt = f"{Fore.BLUE}{Style.BRIGHT}🗣️  Frase > {Style.RESET_ALL}"
            text = input_func(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            output_func(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        if not text:
            continue
        if text.lower() in ("exit", "quit", "salir"):
            output_func(f"{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        result = engine.predict_intent(text)
        intent = result.get('intent', 'unknown')
        conf = result.get('confidence', 0.0)
        entities = result.get('entities', [])
        color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)
        output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        output_func(f"{Fore.CYAN}Intención:{Style.RESET_ALL} {color}{intent}{Style.RESET_ALL}   {Fore.CYAN}Confianza:{Style.RESET_ALL} {color}{conf:.2f}{Style.RESET_ALL}")
        output_func(f"{Fore.CYAN}Entidades:{Style.RESET_ALL}\n{format_entities(entities)}")
        output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}\n")
        # Ejecutar acción asociada a la intención si el engine lo soporta
        try:
            if hasattr(engine, 'execute_skill'):
                action_res = engine.execute_skill(result)
                if action_res:
                    output_func(f"{Fore.MAGENTA}Acción ejecutada:{Style.RESET_ALL} {action_res}")
        except Exception as e:
            output_func(f"{Fore.RED}Error al ejecutar acción: {e}{Style.RESET_ALL}")
    return None
