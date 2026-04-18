from src.skills.steam_game import play_game_smart


def test_play_game_smart_requires_game_name() -> None:
    result = play_game_smart("")
    assert "error" in result


def test_play_game_smart_not_installed(monkeypatch) -> None:
    monkeypatch.setattr("src.skills.steam_game.find_game", lambda game: [])
    opened = []
    monkeypatch.setattr("src.skills.steam_game.webbrowser.open", lambda url: opened.append(url))

    result = play_game_smart("God of War")
    assert result["status"] == "not_installed"
    assert opened
    assert "store.steampowered.com/search" in opened[0]
