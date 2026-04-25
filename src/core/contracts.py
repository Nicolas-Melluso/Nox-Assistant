"""Stable contracts for the NOX core.

These dataclasses are the narrow boundary between intent detection, skill
execution, and interfaces such as the CLI or API. They intentionally include
small compatibility helpers while the older `CoreEngine` API is still present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IntentResult:
    name: str
    confidence: float
    raw_text: str
    entities: dict[str, Any] | list[Any] = field(default_factory=dict)

    @classmethod
    def from_legacy(cls, data: dict[str, Any]) -> "IntentResult":
        return cls(
            name=str(data.get("intent") or data.get("name") or "unknown"),
            confidence=float(data.get("confidence") or data.get("score") or 0.0),
            raw_text=str(data.get("input_text") or data.get("raw_text") or data.get("text") or ""),
            entities=data.get("entities") or {},
        )

    def to_legacy_dict(self) -> dict[str, Any]:
        return {
            "intent": self.name,
            "confidence": self.confidence,
            "input_text": self.raw_text,
            "entities": self.entities,
        }


@dataclass(frozen=True)
class SkillResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_legacy_dict(self, skill_name: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }
        if skill_name:
            payload["skill"] = skill_name
        if self.error:
            payload["error"] = self.error
        if "result" in self.data:
            payload["result"] = self.data["result"]
        return payload


@dataclass(frozen=True)
class SkillHealth:
    ok: bool
    message: str = "ok"


@dataclass(frozen=True)
class OrchestratorResult:
    intent: IntentResult
    skill_name: str | None
    result: SkillResult

    def to_legacy_dict(self) -> dict[str, Any]:
        payload = self.intent.to_legacy_dict()
        payload["skill"] = self.skill_name
        payload["action"] = self.result.to_legacy_dict(self.skill_name)
        return payload
