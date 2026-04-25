"""Permission and audit helpers for the NOX orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Protocol


DEFAULT_ALLOWED_PERMISSIONS = frozenset(
    {
        "os.open_path",
        "os.start_app",
        "os.process_control.request",
        "os.list_known_targets",
        "core.status",
    }
)


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str = "allowed"


class PermissionPolicy:
    def __init__(self, allowed_permissions: set[str] | frozenset[str] | None = None) -> None:
        self.allowed_permissions = frozenset(allowed_permissions or DEFAULT_ALLOWED_PERMISSIONS)

    def check(self, permissions: tuple[str, ...]) -> PermissionDecision:
        denied = [permission for permission in permissions if permission not in self.allowed_permissions]
        if denied:
            return PermissionDecision(
                allowed=False,
                reason=f"Permisos no habilitados: {', '.join(denied)}",
            )
        return PermissionDecision(allowed=True)


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    intent: str
    skill: str | None
    target: str | None
    success: bool
    blocked: bool
    reason: str

    @classmethod
    def build(
        cls,
        *,
        intent: str,
        skill: str | None,
        target: str | None,
        success: bool,
        blocked: bool = False,
        reason: str = "",
    ) -> "AuditEvent":
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            intent=intent,
            skill=skill,
            target=target,
            success=success,
            blocked=blocked,
            reason=reason,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "intent": self.intent,
            "skill": self.skill,
            "target": self.target,
            "success": self.success,
            "blocked": self.blocked,
            "reason": self.reason,
        }


class AuditSink(Protocol):
    def record(self, event: AuditEvent) -> None:
        ...


@dataclass
class InMemoryAuditSink:
    events: list[AuditEvent] = field(default_factory=list)

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)


class FileAuditSink:
    def __init__(self, path: str | Path = "logs/audit.jsonl") -> None:
        self.path = Path(path)

    def record(self, event: AuditEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=True) + "\n")
