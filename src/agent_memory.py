"""Memoria local persistente para AutonomousNox."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_MEMORY_DIR = Path(__file__).resolve().parent.parent / "data"
_MEMORY_FILE = _MEMORY_DIR / "autonomous_memory.json"

_DEFAULT_MEMORY: dict[str, Any] = {
    "preferences": {},
    "successful_flows": [],
    "failed_flows": [],
}


def load_memory() -> dict[str, Any]:
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not _MEMORY_FILE.exists():
        save_memory(_DEFAULT_MEMORY)
        return dict(_DEFAULT_MEMORY)

    try:
        data = json.loads(_MEMORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(_DEFAULT_MEMORY)
        for k, v in _DEFAULT_MEMORY.items():
            data.setdefault(k, v if not isinstance(v, list) else [])
        return data
    except Exception:
        return dict(_DEFAULT_MEMORY)


def save_memory(data: dict[str, Any]) -> None:
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    _MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def remember_success(user_input: str, tools: list[str], summary: str) -> None:
    data = load_memory()
    data.setdefault("successful_flows", [])
    data["successful_flows"].append(
        {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "input": user_input,
            "tools": tools,
            "summary": summary,
        }
    )
    data["successful_flows"] = data["successful_flows"][-80:]
    save_memory(data)


def remember_failure(user_input: str, tool: str, error: str) -> None:
    data = load_memory()
    data.setdefault("failed_flows", [])
    data["failed_flows"].append(
        {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "input": user_input,
            "tool": tool,
            "error": error,
        }
    )
    data["failed_flows"] = data["failed_flows"][-80:]
    save_memory(data)


def memory_snippet(max_items: int = 5) -> str:
    data = load_memory()
    ok = data.get("successful_flows", [])[-max_items:]
    bad = data.get("failed_flows", [])[-max_items:]

    lines = ["Memoria local reciente:"]
    if ok:
        lines.append("- Exitos recientes:")
        for item in ok:
            tools = ", ".join(item.get("tools", []))
            lines.append(f"  - {item.get('input','')} -> {tools}")
    if bad:
        lines.append("- Fallos recientes:")
        for item in bad:
            lines.append(f"  - {item.get('input','')} -> {item.get('tool','')}: {item.get('error','')}")
    return "\n".join(lines)
