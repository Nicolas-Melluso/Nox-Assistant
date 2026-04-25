"""Single entrypoint for understanding text and dispatching NOX skills."""

from __future__ import annotations

from typing import Any

from .contracts import IntentResult, OrchestratorResult, SkillResult
from .intent_classifier import RuleBasedIntentClassifier
from .security import AuditEvent, AuditSink, PermissionPolicy
from .skills import SkillRegistry
from .skills.core_skill import CoreStatusSkill
from .skills.os_skill import BlockedProcessControlSkill, ListKnownTargetsSkill, OSSkill
from .os_control import OSController, SubprocessOSController


class NoxOrchestrator:
    def __init__(
        self,
        classifier: Any | None = None,
        registry: SkillRegistry | None = None,
        os_controller: OSController | None = None,
        permission_policy: PermissionPolicy | None = None,
        audit_sink: AuditSink | None = None,
    ) -> None:
        self.classifier = classifier or RuleBasedIntentClassifier()
        self.registry = registry or default_registry(os_controller=os_controller)
        self.permission_policy = permission_policy or PermissionPolicy()
        self.audit_sink = audit_sink

    def handle(self, text: str, context: dict[str, Any] | None = None) -> OrchestratorResult:
        intent = self._classify(text)
        skill = self.registry.find_for_intent(intent.name)

        target = self._extract_target(intent)

        if skill is None:
            orchestrator_result = OrchestratorResult(
                intent=intent,
                skill_name=None,
                result=SkillResult(
                    success=False,
                    message=f"No hay una skill segura para manejar '{intent.name}'.",
                    data={"reason": "unknown_intent" if intent.name == "unknown" else "no_skill"},
                ),
            )
            self._audit(orchestrator_result, target=target, blocked=True)
            return orchestrator_result

        decision = self.permission_policy.check(skill.permissions)
        if not decision.allowed:
            orchestrator_result = OrchestratorResult(
                intent=intent,
                skill_name=skill.name,
                result=SkillResult(
                    success=False,
                    message=decision.reason,
                    data={"blocked": True, "reason": "permission_denied", "target": target},
                ),
            )
            self._audit(orchestrator_result, target=target, blocked=True, reason=decision.reason)
            return orchestrator_result

        run_context = self._build_context(context)
        result = self.registry.run(skill, intent, context=run_context)
        orchestrator_result = OrchestratorResult(intent=intent, skill_name=skill.name, result=result)
        self._audit(orchestrator_result, target=target)
        return orchestrator_result

    def _classify(self, text: str) -> IntentResult:
        if hasattr(self.classifier, "classify"):
            result = self.classifier.classify(text)
        else:
            result = self.classifier.predict(text)
        if isinstance(result, IntentResult):
            return result
        intent = IntentResult.from_legacy(result)
        if not intent.raw_text:
            return IntentResult(
                name=intent.name,
                confidence=intent.confidence,
                raw_text=text,
                entities=intent.entities,
            )
        return intent

    def _build_context(self, context: dict[str, Any] | None) -> dict[str, Any]:
        run_context = dict(context or {})
        run_context.setdefault("skills", [skill.name for skill in self.registry.list_skills()])
        run_context.setdefault("allowed_permissions", set(self.permission_policy.allowed_permissions))
        return run_context

    def _extract_target(self, intent: IntentResult) -> str | None:
        if isinstance(intent.entities, dict):
            target = intent.entities.get("target")
            return str(target) if target else None
        return None

    def _audit(
        self,
        result: OrchestratorResult,
        *,
        target: str | None,
        blocked: bool = False,
        reason: str = "",
    ) -> None:
        if self.audit_sink is None:
            return
        event = AuditEvent.build(
            intent=result.intent.name,
            skill=result.skill_name,
            target=target,
            success=result.result.success,
            blocked=blocked or bool(result.result.data.get("blocked")),
            reason=reason or result.result.error or result.result.message,
        )
        self.audit_sink.record(event)


def default_registry(os_controller: OSController | None = None) -> SkillRegistry:
    return SkillRegistry(
        skills=[
            OSSkill(os_controller or SubprocessOSController(dry_run=False)),
            BlockedProcessControlSkill(),
            ListKnownTargetsSkill(),
            CoreStatusSkill(),
        ]
    )
