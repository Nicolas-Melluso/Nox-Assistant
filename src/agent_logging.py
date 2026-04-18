from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_LOG_DIR = Path(__file__).resolve().parent.parent / "results"
_LOG_FILE = _LOG_DIR / "autonomous_agent_logs.jsonl"


def append_step_log(entry: dict[str, Any]) -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = dict(entry)
    payload.setdefault("ts", datetime.now().isoformat(timespec="seconds"))
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def get_log_path() -> str:
    return str(_LOG_FILE)
