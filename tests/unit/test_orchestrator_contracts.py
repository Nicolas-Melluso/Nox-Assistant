import pytest

from core.contracts import IntentResult, SkillHealth, SkillResult
from core.intent_classifier import RuleBasedIntentClassifier
from core.orchestrator import NoxOrchestrator
from core.os_control import SubprocessOSController
from core.security import FileAuditSink, InMemoryAuditSink, PermissionPolicy
from core.skills import Skill, SkillRegistry, validate_skill_contract
from core.skills.os_skill import BlockedProcessControlSkill, ListKnownTargetsSkill, OSSkill


def test_rule_based_classifier_detects_open_youtube():
    intent = RuleBasedIntentClassifier().classify("abrir youtube")

    assert intent.name == "open"
    assert intent.confidence >= 0.9
    assert intent.entities["target"] == "youtube"


def test_rule_based_classifier_detects_open_steam():
    intent = RuleBasedIntentClassifier().classify("abrir steam")

    assert intent.name == "open"
    assert intent.confidence >= 0.9
    assert intent.entities["target"] == "steam"


def test_rule_based_classifier_detects_generic_open_target():
    intent = RuleBasedIntentClassifier().classify("abrir discord")

    assert intent.name == "open"
    assert intent.entities["target"] == "discord"


def test_rule_based_classifier_detects_list_known_targets():
    intent = RuleBasedIntentClassifier().classify("que podes abrir")

    assert intent.name == "list_known_targets"
    assert intent.confidence >= 0.9


def test_rule_based_classifier_detects_core_status():
    intent = RuleBasedIntentClassifier().classify("como estas")

    assert intent.name == "core_status"
    assert intent.confidence >= 0.9


def test_orchestrator_dispatches_safe_open_skill():
    controller = SubprocessOSController(dry_run=True)
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
    )

    result = orchestrator.handle("abrir youtube")

    assert result.intent.name == "open"
    assert result.skill_name == "os.open_known_target"
    assert result.result.success is True
    assert result.result.data["result"]["dry_run"] is True


def test_orchestrator_dispatches_safe_steam_skill():
    controller = SubprocessOSController(dry_run=True)
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
    )

    result = orchestrator.handle("abrir steam")

    assert result.intent.name == "open"
    assert result.skill_name == "os.open_known_target"
    assert result.result.success is True
    assert result.result.data["target"] == "steam"
    assert result.result.data["url"] == "steam://open/main"


def test_orchestrator_dispatches_configured_local_app():
    controller = SubprocessOSController(dry_run=True)
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
    )

    result = orchestrator.handle("abrir calculadora")

    assert result.intent.name == "open"
    assert result.result.success is True
    assert result.result.data["target"] == "calc"
    assert result.result.data["result"]["action"] == "start_app"


def test_orchestrator_lists_known_targets():
    result = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([ListKnownTargetsSkill()]),
    ).handle("que podes abrir")

    assert result.intent.name == "list_known_targets"
    assert result.skill_name == "os.list_known_targets"
    assert result.result.success is True
    assert result.result.data["count"] >= 1
    names = {item["name"] for item in result.result.data["targets"]}
    assert "steam" in names
    assert "youtube" in names


def test_orchestrator_reports_core_status():
    result = NoxOrchestrator(classifier=RuleBasedIntentClassifier()).handle("como estas")

    assert result.intent.name == "core_status"
    assert result.skill_name == "core.status"
    assert result.result.success is True
    assert result.result.data["skill_count"] >= 4
    assert "core.status" in result.result.data["skills"]


def test_orchestrator_blocks_skill_without_permission():
    controller = SubprocessOSController(dry_run=True)
    audit = InMemoryAuditSink()
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
        permission_policy=PermissionPolicy(allowed_permissions={"os.open_path"}),
        audit_sink=audit,
    )

    result = orchestrator.handle("abrir calculadora")

    assert result.result.success is False
    assert result.result.data["blocked"] is True
    assert result.result.data["reason"] == "permission_denied"
    assert audit.events[-1].blocked is True
    assert audit.events[-1].target == "calculator"


def test_orchestrator_audits_allowed_action():
    controller = SubprocessOSController(dry_run=True)
    audit = InMemoryAuditSink()
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
        audit_sink=audit,
    )

    result = orchestrator.handle("abrir steam")

    assert result.result.success is True
    assert len(audit.events) == 1
    assert audit.events[0].intent == "open"
    assert audit.events[0].skill == "os.open_known_target"
    assert audit.events[0].target == "steam"
    assert audit.events[0].success is True


def test_file_audit_sink_writes_jsonl(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    audit = FileAuditSink(audit_path)
    controller = SubprocessOSController(dry_run=True)
    orchestrator = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
        audit_sink=audit,
    )

    orchestrator.handle("abrir steam")

    content = audit_path.read_text(encoding="utf-8")
    assert '"intent": "open"' in content
    assert '"skill": "os.open_known_target"' in content


def test_orchestrator_unknown_intent_does_not_execute_action():
    controller = SubprocessOSController(dry_run=True)
    result = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller)]),
        os_controller=controller,
    ).handle("contame una historia")

    assert result.intent.name == "unknown"
    assert result.skill_name is None
    assert result.result.success is False
    assert result.result.data["reason"] == "unknown_intent"


def test_close_action_is_blocked_with_actionable_message():
    controller = SubprocessOSController(dry_run=True)
    audit = InMemoryAuditSink()
    result = NoxOrchestrator(
        classifier=RuleBasedIntentClassifier(),
        registry=SkillRegistry([OSSkill(controller), BlockedProcessControlSkill()]),
        os_controller=controller,
        audit_sink=audit,
    ).handle("cerrar steam")

    assert result.intent.name == "close"
    assert result.skill_name == "os.process_control.blocked"
    assert result.result.success is False
    assert result.result.data["blocked"] is True
    assert "permisos explicitos" in result.result.message
    assert audit.events[-1].blocked is True


def test_registry_rejects_invalid_skill():
    class InvalidSkill(Skill):
        name = ""
        description = "Broken"
        permissions = ()
        supported_intents = ()

        def run(self, intent_result, context=None):
            return SkillResult(success=True, message="ok")

    with pytest.raises(ValueError):
        SkillRegistry([InvalidSkill()])


def test_valid_skill_contract_requires_health_object():
    class ValidSkill(Skill):
        name = "test.valid"
        description = "Valid test skill"
        permissions = ("test.run",)
        supported_intents = ("test",)

        def healthcheck(self):
            return SkillHealth(ok=True)

        def run(self, intent_result, context=None):
            return SkillResult(success=True, message="ok")

    validate_skill_contract(ValidSkill())


def test_intent_result_legacy_shape_is_preserved():
    intent = IntentResult(name="open", confidence=0.9, raw_text="abrir youtube", entities={"target": "youtube"})

    assert intent.to_legacy_dict() == {
        "intent": "open",
        "confidence": 0.9,
        "input_text": "abrir youtube",
        "entities": {"target": "youtube"},
    }
