from typing import Dict, Any, List


class Skill:
    def handles(self, intent_result: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def run(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class SkillRegistry:
    def __init__(self):
        self._skills: List[Skill] = []

    def register(self, skill: Skill):
        self._skills.append(skill)

    def dispatch(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        for s in self._skills:
            try:
                # Si la skill declara una feature flag, comprobar que está habilitada
                feature_flag = getattr(s, "feature_flag", None)
                if feature_flag:
                    try:
                        from src.config.feature_flags import FeatureFlags
                        ff = FeatureFlags()
                        iface, category, feature = feature_flag
                        if not ff.is_enabled(iface, category, feature):
                            return {"skill": getattr(s, "__class__", type(s)).__name__, "enabled": False, "success": False}
                    except Exception:
                        # Si falla la comprobación de flags, seguir con la ejecución
                        pass
                if s.handles(intent_result):
                    return s.run(intent_result)
            except Exception as e:
                return {"skill": "error", "success": False, "error": str(e)}
        if intent_result.get("intent", "").lower() == "noop":
            return {"skill": "noop", "success": True}
        return {"skill": "noop", "success": False}
