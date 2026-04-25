from typing import Any, Dict, List

from ..contracts import IntentResult, SkillHealth, SkillResult


class Skill:
    name: str
    description: str
    permissions: tuple[str, ...]
    supported_intents: tuple[str, ...]

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in self.supported_intents

    def handles(self, intent_result: Dict[str, Any]) -> bool:
        return self.can_handle((intent_result.get("intent") or "").lower())

    def healthcheck(self) -> SkillHealth:
        return SkillHealth(ok=True)

    def run(
        self,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        raise NotImplementedError


class SkillRegistry:
    def __init__(self, skills: List[Skill] | None = None):
        self._skills: List[Skill] = []
        for skill in skills or []:
            self.register(skill)

    def register(self, skill: Skill):
        validate_skill_contract(skill)
        self._skills.append(skill)

    def list_skills(self) -> list[Skill]:
        return list(self._skills)

    def find_for_intent(self, intent_name: str) -> Skill | None:
        for skill in self._skills:
            if skill.can_handle(intent_name):
                return skill
        return None

    def run(
        self,
        skill: Skill,
        intent_result: Dict[str, Any] | IntentResult,
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        if not self._is_enabled(skill):
            return SkillResult(
                success=False,
                message=f"La skill '{skill.name}' esta deshabilitada por feature flag.",
                data={"enabled": False},
            )
        try:
            result = skill.run(intent_result, context=context)
            if isinstance(result, SkillResult):
                return result
            if isinstance(result, dict):
                return SkillResult(
                    success=bool(result.get("success", False)),
                    message=str(result.get("message") or result.get("error") or ""),
                    data=result,
                    error=result.get("error"),
                )
            return SkillResult(success=False, message="La skill devolvio un resultado invalido.")
        except Exception as exc:
            return SkillResult(success=False, message="Error ejecutando skill.", error=str(exc))

    def dispatch(self, intent_result: Dict[str, Any]) -> SkillResult:
        intent = (intent_result.get("intent") or "").lower()
        if intent == "noop":
            return SkillResult(success=True, message="Sin accion requerida.", data={"skill": "noop"})
        skill = self.find_for_intent(intent)
        if skill is None:
            return SkillResult(success=False, message=f"No hay skill para '{intent}'.", data={"skill": "noop"})
        return self.run(skill, intent_result)

    def _is_enabled(self, skill: Skill) -> bool:
        feature_flag = getattr(skill, "feature_flag", None)
        if not feature_flag:
            return True
        try:
            try:
                from src.config.feature_flags import FeatureFlags
            except Exception:
                from config.feature_flags import FeatureFlags
            ff = FeatureFlags()
            iface, category, feature = feature_flag
            return ff.is_enabled(iface, category, feature)
        except Exception:
            return True


def validate_skill_contract(skill: Skill) -> None:
    for field_name in ("name", "description"):
        value = getattr(skill, field_name, None)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Skill must define a non-empty {field_name}")

    for field_name in ("permissions", "supported_intents"):
        value = getattr(skill, field_name, None)
        if not isinstance(value, tuple) or not value:
            raise ValueError(f"Skill must define a non-empty {field_name} tuple")

    health = skill.healthcheck()
    if not isinstance(health, SkillHealth):
        raise ValueError("Skill healthcheck must return SkillHealth")
