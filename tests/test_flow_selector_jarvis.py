from src.skills.flow_selector import suggest_flow


def test_selects_play_game_smart_for_specific_game_phrase() -> None:
    ctx = {"hour": 19, "cpu_percent": 30}
    flow = suggest_flow("quiero jugar al god of war", ctx)
    assert flow == "play_game_smart"


def test_night_nudge_keeps_focus_flow() -> None:
    ctx = {"hour": 23, "cpu_percent": 90}
    flow = suggest_flow("", ctx)
    assert flow == "focus_pomodoro_flow"
