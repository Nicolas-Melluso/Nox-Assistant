from src.autonomous_agent import _sanitize_user_input, _validate_user_input


def test_validate_user_input_accepts_normal_text() -> None:
    ok, reason = _validate_user_input("abre youtube y busca musica lofi")
    assert ok is True
    assert reason == "ok"


def test_validate_user_input_rejects_empty() -> None:
    ok, reason = _validate_user_input("   ")
    assert ok is False
    assert reason == "input_vacio"


def test_validate_user_input_rejects_control_chars() -> None:
    ok, reason = _validate_user_input("hola\x01mundo")
    assert ok is False
    assert reason == "input_con_control_chars"


def test_sanitize_user_input_normalizes_whitespace() -> None:
    sanitized = _sanitize_user_input("  abre\n\n youtube\r\nahora   ")
    assert sanitized == "abre youtube ahora"
