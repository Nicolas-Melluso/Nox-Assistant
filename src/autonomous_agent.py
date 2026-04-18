from __future__ import annotations

import json
import os
import re
import time
import uuid
from typing import Callable

from dotenv import load_dotenv
from openai import OpenAI

from src.agent_logging import append_step_log, get_log_path
from src.agent_memory import memory_snippet, remember_failure, remember_success
from src.skills.context import evaluate_precheck, get_runtime_context
from src.skills.flow_selector import suggest_flow
from src.skills.policies import get_policy, requires_confirmation
from src.skills.registry import execute_skill
from src.tools_manifest import TOOLS, TOOL_NAMES

load_dotenv()

_PROVIDER_PRIORITY = os.getenv("NOX_PROVIDER_PRIORITY", "github,ollama")
_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
_GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
_GITHUB_BASE_URL = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

_SYSTEM_PROMPT = """\
Eres NOX, un asistente autonomo para PC.
Siempre respondes en espanol.
Piensa en flujos completos y funcionales usando solo tools disponibles.
Si corresponde, usa flujos premium (photo_pro_flow, gaming_setup_flow, focus_pomodoro_flow).
"""


class AgentStep:
    def __init__(self, tool: str, args: dict, result: dict, policy: dict | None = None):
        self.tool = tool
        self.args = args
        self.result = result
        self.policy = policy or {}


class AgentResult:
    def __init__(self, message: str, steps: list[AgentStep], providers_used: list[str], run_id: str):
        self.message = message
        self.steps = steps
        self.providers_used = providers_used
        self.run_id = run_id

    @property
    def tools_used(self) -> list[str]:
        return [s.tool for s in self.steps]


def _provider_order() -> list[str]:
    order = [x.strip().lower() for x in _PROVIDER_PRIORITY.split(",") if x.strip()]
    valid = [x for x in order if x in {"github", "ollama"}]
    return valid or ["github", "ollama"]


def _make_client(provider: str) -> tuple[OpenAI, str]:
    if provider == "github":
        if not _GITHUB_TOKEN or _GITHUB_TOKEN == "your_github_token_here":
            raise ValueError("GITHUB_TOKEN no configurado para provider github")
        return OpenAI(base_url=_GITHUB_BASE_URL, api_key=_GITHUB_TOKEN), _GITHUB_MODEL
    if provider == "ollama":
        return OpenAI(base_url=_OLLAMA_BASE_URL, api_key="ollama"), _OLLAMA_MODEL
    raise ValueError(f"Provider invalido: {provider}")


def _extract_json(content: str) -> dict | list | None:
    text = (content or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"```(?:json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```", text, flags=re.IGNORECASE)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _chat_with_failover(messages: list[dict], tools: list[dict] | None = None, tool_choice: str | None = None) -> tuple[object, str, str | None]:
    providers = _provider_order()
    last_error = None
    used: list[str] = []
    for provider in providers:
        try:
            client, model = _make_client(provider)
            kwargs = {"model": model, "messages": messages}
            if tools is not None:
                kwargs["tools"] = tools
            if tool_choice is not None:
                kwargs["tool_choice"] = tool_choice
            response = client.chat.completions.create(**kwargs)
            fallback_from = used[-1] if used else None
            return response, provider, fallback_from
        except Exception as e:
            used.append(provider)
            last_error = f"{provider}: {e}"
            continue
    raise RuntimeError(f"No se pudo contactar ningun provider ({', '.join(providers)}). Ultimo error: {last_error}")


def _validate_plan(steps: list[dict]) -> tuple[bool, str]:
    if not steps:
        return False, "plan_vacio"
    if len(steps) > 10:
        return False, "plan_demasiado_largo"
    for step in steps:
        if not isinstance(step, dict):
            return False, "step_invalido"
        tool = step.get("tool")
        args = step.get("args", {})
        if tool not in TOOL_NAMES:
            return False, f"tool_desconocida:{tool}"
        if not isinstance(args, dict):
            return False, f"args_invalidos:{tool}"
    return True, "ok"


def _build_plan(user_input: str, context: dict) -> tuple[list[dict], str, str | None]:
    suggested = suggest_flow(user_input, context)
    prompt = (
        "Devuelve SOLO JSON valido con formato {\"steps\":[{\"tool\":\"...\",\"args\":{...},\"why\":\"...\"}]} sin texto extra.\n"
        "Reglas: maximo 7 pasos, usar tools disponibles, y priorizar flujos premium cuando tenga sentido.\n"
        f"Tools disponibles: {sorted(TOOL_NAMES)}\n"
        f"Flow sugerido por contexto: {suggested or 'none'}\n"
        f"Contexto: {json.dumps(context, ensure_ascii=False)}\n"
        f"Memoria: {memory_snippet()}\n"
        f"Pedido usuario: {user_input}"
    )

    response, provider, fallback_from = _chat_with_failover(
        messages=[
            {"role": "system", "content": "Eres planner de tools. Solo JSON."},
            {"role": "user", "content": prompt},
        ]
    )
    content = response.choices[0].message.content or ""
    parsed = _extract_json(content)
    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        return parsed["steps"], provider, fallback_from

    if suggested:
        return [{"tool": suggested, "args": {}, "why": "fallback_selector"}], provider, fallback_from
    return [], provider, fallback_from


def _replan_after_error(user_input: str, context: dict, failed_tool: str, error: str, execution_log: list[dict]) -> tuple[list[dict], str, str | None]:
    prompt = (
        "Devuelve SOLO JSON valido con formato {\"steps\":[...]} para continuar el objetivo.\n"
        "Reglas: maximo 3 pasos, no repetir la herramienta fallida salvo que justifiques alternativa por args.\n"
        f"Herramienta fallida: {failed_tool}\n"
        f"Error: {error}\n"
        f"Contexto actual: {json.dumps(context, ensure_ascii=False)}\n"
        f"Log previo: {json.dumps(execution_log[-5:], ensure_ascii=False)}\n"
        f"Objetivo: {user_input}"
    )
    response, provider, fallback_from = _chat_with_failover(
        messages=[
            {"role": "system", "content": "Eres replanner de tools. Solo JSON."},
            {"role": "user", "content": prompt},
        ]
    )
    parsed = _extract_json(response.choices[0].message.content or "")
    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        return parsed["steps"], provider, fallback_from
    return [], provider, fallback_from


def _summarize(user_input: str, execution_log: list[dict], context: dict) -> tuple[str, str, str | None]:
    prompt = (
        "Resume en espanol en 2-4 lineas: que se pidio, que se ejecuto y resultado final.\n"
        f"Pedido: {user_input}\n"
        f"Contexto final: {json.dumps(context, ensure_ascii=False)}\n"
        f"Ejecucion: {json.dumps(execution_log, ensure_ascii=False)}"
    )
    response, provider, fallback_from = _chat_with_failover(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    return (response.choices[0].message.content or "Listo.").strip(), provider, fallback_from


def run_agent(
    user_input: str,
    on_step: Callable[[str, dict, dict], None] | None = None,
    on_confirm: Callable[[str, dict, dict], bool] | None = None,
    max_iterations: int = 8,
) -> AgentResult:
    run_id = str(uuid.uuid4())
    context = get_runtime_context()
    providers_used: list[str] = []

    plan_steps, provider_plan, fallback_plan = _build_plan(user_input, context)
    providers_used.append(provider_plan)

    append_step_log(
        {
            "run_id": run_id,
            "stage": "plan",
            "provider": provider_plan,
            "fallback_from": fallback_plan,
            "user_input": user_input,
            "context": context,
            "plan_steps": plan_steps,
        }
    )

    valid, reason = _validate_plan(plan_steps)
    if not valid:
        plan_steps = []

    steps: list[AgentStep] = []
    execution_log: list[dict] = []

    queue = plan_steps[:max_iterations]
    idx = 0
    while idx < len(queue):
        step = queue[idx]
        idx += 1

        tool = step.get("tool")
        args = step.get("args", {})
        policy = get_policy(tool)

        pre_ok, pre_msg = evaluate_precheck(tool, args, context)
        if not pre_ok:
            result = {"error": f"precheck_failed: {pre_msg}"}
            cur = AgentStep(tool=tool, args=args, result=result, policy=policy)
            steps.append(cur)
            execution_log.append({"tool": tool, "args": args, "result": result, "precheck": pre_msg})
            remember_failure(user_input, tool, result["error"])

            append_step_log(
                {
                    "run_id": run_id,
                    "stage": "precheck",
                    "tool": tool,
                    "args": args,
                    "status": "blocked",
                    "reason": pre_msg,
                    "risk": policy.get("risk"),
                }
            )
            continue

        if requires_confirmation(tool):
            allowed = False
            if on_confirm:
                allowed = bool(on_confirm(tool, args, policy))
            if not allowed:
                result = {"error": "cancelado_por_usuario", "policy": policy}
                cur = AgentStep(tool=tool, args=args, result=result, policy=policy)
                steps.append(cur)
                execution_log.append({"tool": tool, "args": args, "result": result})
                append_step_log(
                    {
                        "run_id": run_id,
                        "stage": "confirm",
                        "tool": tool,
                        "args": args,
                        "status": "denied",
                        "risk": policy.get("risk"),
                    }
                )
                continue

        t0 = time.perf_counter()
        result = execute_skill(tool, args)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        if "error" in result:
            remember_failure(user_input, tool, str(result["error"]))

        cur = AgentStep(tool=tool, args=args, result=result, policy=policy)
        steps.append(cur)
        execution_log.append({"tool": tool, "args": args, "result": result, "duration_ms": elapsed_ms})

        if on_step:
            on_step(tool, args, result)

        append_step_log(
            {
                "run_id": run_id,
                "stage": "execute",
                "tool": tool,
                "args": args,
                "status": "error" if "error" in result else "ok",
                "duration_ms": elapsed_ms,
                "risk": policy.get("risk"),
                "result": result,
            }
        )

        if "error" in result:
            context = get_runtime_context()
            replan_steps, provider_replan, fallback_replan = _replan_after_error(
                user_input=user_input,
                context=context,
                failed_tool=tool,
                error=str(result["error"]),
                execution_log=execution_log,
            )
            providers_used.append(provider_replan)
            ok_replan, _ = _validate_plan(replan_steps)
            append_step_log(
                {
                    "run_id": run_id,
                    "stage": "replan",
                    "provider": provider_replan,
                    "fallback_from": fallback_replan,
                    "failed_tool": tool,
                    "replan_steps": replan_steps,
                    "valid": ok_replan,
                }
            )
            if ok_replan:
                queue.extend(replan_steps[: max_iterations - len(queue)])

    context = get_runtime_context()
    summary, provider_summary, fallback_summary = _summarize(user_input, execution_log, context)
    providers_used.append(provider_summary)

    remember_success(user_input, [s.tool for s in steps], summary)

    append_step_log(
        {
            "run_id": run_id,
            "stage": "summary",
            "provider": provider_summary,
            "fallback_from": fallback_summary,
            "providers_used": providers_used,
            "tools_used": [s.tool for s in steps],
            "log_file": get_log_path(),
            "summary": summary,
        }
    )

    return AgentResult(
        message=summary,
        steps=steps,
        providers_used=providers_used,
        run_id=run_id,
    )
