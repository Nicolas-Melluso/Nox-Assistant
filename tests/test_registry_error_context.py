from src.skills.registry import execute_skill


def test_execute_skill_unknown_tool() -> None:
    result = execute_skill("tool_no_existente", {})
    assert "error" in result


def test_execute_skill_includes_error_context() -> None:
    # open_folder requiere argumento path: fuerza TypeError controlado
    result = execute_skill("open_folder", {})
    assert "error" in result
    assert result.get("error_type")
    assert result.get("traceback")
    assert result.get("tool") == "open_folder"
