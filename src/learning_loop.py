from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrainingSignal:
    ts: str
    user_text: str
    predicted_intent: str
    source: str
    note: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _log_file() -> Path:
    return _repo_root() / "results" / "autonomous_agent_logs.jsonl"


def _feedback_file() -> Path:
    return _repo_root() / "data" / "raw" / "nox_feedback.csv"


def extract_signals(max_items: int = 300) -> list[TrainingSignal]:
    log_path = _log_file()
    if not log_path.exists():
        return []

    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-max_items:]
    run_to_input: dict[str, str] = {}
    signals: list[TrainingSignal] = []

    for line in lines:
        try:
            item = json.loads(line)
        except Exception:
            continue

        run_id = str(item.get("run_id", ""))
        stage = str(item.get("stage", ""))

        if stage == "plan" and run_id and item.get("user_input"):
            run_to_input[run_id] = str(item.get("user_input"))

        if stage == "execute" and run_id and item.get("tool"):
            status = str(item.get("status", ""))
            user_text = run_to_input.get(run_id, "")
            if not user_text:
                continue
            signals.append(
                TrainingSignal(
                    ts=str(item.get("ts", "")),
                    user_text=user_text,
                    predicted_intent=str(item.get("tool")),
                    source="auto_log",
                    note="ok" if status == "ok" else "error",
                )
            )
    return signals


def append_signals_to_feedback(signals: list[TrainingSignal]) -> dict:
    out = _feedback_file()
    out.parent.mkdir(parents=True, exist_ok=True)

    exists = out.exists()
    seen: set[tuple[str, str, str]] = set()
    if exists:
        with out.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen.add((row.get("text", ""), row.get("predicted", ""), row.get("source", "")))

    added = 0
    with out.open("a", encoding="utf-8", newline="") as f:
        fieldnames = ["ts", "text", "predicted", "correct", "source", "note"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()

        for s in signals:
            key = (s.user_text, s.predicted_intent, s.source)
            if key in seen:
                continue
            writer.writerow(
                {
                    "ts": s.ts,
                    "text": s.user_text,
                    "predicted": s.predicted_intent,
                    "correct": "",
                    "source": s.source,
                    "note": s.note,
                }
            )
            seen.add(key)
            added += 1

    return {"added": added, "total_signals": len(signals), "feedback_file": str(out)}
