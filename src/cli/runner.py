import json
import sys
from typing import Callable, Optional

from colorama import Fore, Style

from src.cli.ui import format_entities


def _human_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " y " + items[-1]


def _format_action_response(action_res: dict) -> str:
    data = action_res.get("data") if isinstance(action_res.get("data"), dict) else {}
    targets = data.get("targets") if isinstance(data, dict) else None
    if isinstance(targets, list):
        names = [str(item.get("name")) for item in targets if isinstance(item, dict) and item.get("name")]
        if names:
            return f"Puedo abrir: {_human_join(names)}."

    message = action_res.get("message") or action_res.get("error") or ""
    if message:
        return str(message)
    return "Listo." if action_res.get("success") else "No pude completar la accion."


def _handle_text(engine, text: str) -> tuple[dict, Optional[dict]]:
    if hasattr(engine, "handle"):
        handled = engine.handle(text)
        if hasattr(handled, "to_legacy_dict"):
            handled = handled.to_legacy_dict()
        result = {
            "intent": handled.get("intent", "unknown"),
            "confidence": handled.get("confidence", 0.0),
            "input_text": handled.get("input_text", text),
            "entities": handled.get("entities", []),
        }
        return result, handled.get("action")

    result = engine.predict_intent(text)
    action_res = None
    if hasattr(engine, "execute_skill"):
        action_res = engine.execute_skill(result)
    return result, action_res


def _render_result(output_func: Callable, result: dict, action_res: Optional[dict], line: str, verbose: bool = False) -> None:
    intent = result.get("intent", "unknown")
    conf = result.get("confidence", 0.0)
    input_text = result.get("input_text", "")
    entities = result.get("entities", [])
    color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)

    if not verbose:
        if action_res:
            success = action_res.get("success")
            color_out = Fore.GREEN if success else Fore.YELLOW
            output_func(f"{color_out}{_format_action_response(action_res)}{Style.RESET_ALL}")
        else:
            output_func(f"{Fore.YELLOW}No tengo una accion segura para eso todavia.{Style.RESET_ALL}")
        return

    output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
    output_func(f"{Fore.CYAN}Entrada:{Style.RESET_ALL} {input_text}")
    output_func(
        f"{Fore.CYAN}Intent:{Style.RESET_ALL} {color}{intent}{Style.RESET_ALL}   "
        f"{Fore.CYAN}Confianza:{Style.RESET_ALL} {color}{conf:.2f}{Style.RESET_ALL}"
    )
    output_func(f"{Fore.CYAN}Entidades:{Style.RESET_ALL}\n{format_entities(entities)}")

    if action_res:
        skill = action_res.get("skill") or "(sin skill)"
        success = action_res.get("success")
        message = _format_action_response(action_res)
        output_func(f"{Fore.GREEN if success else Fore.YELLOW}{message}{Style.RESET_ALL}")
        output_func(f"{Fore.MAGENTA}Skill:{Style.RESET_ALL} {skill}   {Fore.MAGENTA}OK:{Style.RESET_ALL} {success}")
    output_func(f"{Fore.WHITE}{line}{Style.RESET_ALL}\n")


def run_console(
    engine,
    input_func: Callable = input,
    output_func: Callable = print,
    once: bool = False,
    external_api_test: bool = False,
    verbose: bool = False,
) -> Optional[dict]:
    """Run the CLI loop against the central core/orchestrator."""
    is_tty = sys.stdout.isatty()
    line = "-" * 52 if not is_tty else "─" * 52

    if external_api_test:
        output_func(f"{Fore.CYAN}Prueba de integracion con API externa{Style.RESET_ALL}")
        service = input_func("Nombre del servicio externo: ").strip()
        endpoint = input_func("Endpoint (ej: /datos): ").strip()
        method = input_func("Metodo HTTP [GET/POST]: ").strip().upper() or "GET"
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
        try:
            result, action_res = _handle_text(engine, text)
            _render_result(output_func, result, action_res, line, verbose=verbose)
            return result
        except Exception as exc:
            output_func(f"{Fore.RED}Error al ejecutar accion: {exc}{Style.RESET_ALL}")
            return None

    while True:
        try:
            prompt = f"{Fore.BLUE}{Style.BRIGHT}Frase > {Style.RESET_ALL}"
            text = input_func(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            output_func(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        if not text:
            continue
        if text.lower() in ("exit", "quit", "salir"):
            output_func(f"{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
            break
        try:
            result, action_res = _handle_text(engine, text)
            _render_result(output_func, result, action_res, line, verbose=verbose)
        except Exception as exc:
            output_func(f"{Fore.RED}Error al ejecutar accion: {exc}{Style.RESET_ALL}")
    return None
