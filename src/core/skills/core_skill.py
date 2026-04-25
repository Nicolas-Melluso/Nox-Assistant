from typing import Any, Dict

from ..contracts import IntentResult, SkillResult
from . import Skill


class CoreStatusSkill(Skill):
    name = "core.status"
    description = "Report core runtime status and registered skills."
    permissions = ("core.status",)
    supported_intents = ("core_status",)

    def run(
        self,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        context = context or {}
        skills = context.get("skills") if isinstance(context.get("skills"), list) else []
        permissions = context.get("allowed_permissions")
        dry_run = context.get("dry_run")
        version = context.get("version") or "v0.5.0-mvp"

        return SkillResult(
            success=True,
            message=f"NOX {version} operativo.",
            data={
                "version": version,
                "skills": skills,
                "skill_count": len(skills),
                "allowed_permissions": sorted(permissions) if permissions else [],
                "dry_run": dry_run,
            },
        )
