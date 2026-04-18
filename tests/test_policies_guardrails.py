from src.skills.policies import get_policy, requires_confirmation


def test_shutdown_policy_is_critical_and_confirmed() -> None:
    policy = get_policy("shutdown")
    assert policy["risk"] == "critical"
    assert policy["confirm"] is True
    assert requires_confirmation("shutdown") is True


def test_restart_policy_is_critical_and_confirmed() -> None:
    policy = get_policy("restart")
    assert policy["risk"] == "critical"
    assert policy["confirm"] is True
    assert requires_confirmation("restart") is True


def test_unknown_tool_still_requires_confirmation() -> None:
    assert requires_confirmation("tool_no_existente") is True
