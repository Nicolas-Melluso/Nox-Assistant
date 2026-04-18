from __future__ import annotations

import os
import re
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SteamGame:
    appid: str
    name: str
    manifest_path: str


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _steam_root() -> Path:
    custom = os.getenv("NOX_STEAM_ROOT", "").strip()
    if custom:
        return Path(custom)

    candidates = [
        Path("C:/Program Files (x86)/Steam"),
        Path("C:/Program Files/Steam"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _parse_libraryfolders(vdf_path: Path) -> list[Path]:
    roots: list[Path] = []
    if not vdf_path.exists():
        return roots

    text = vdf_path.read_text(encoding="utf-8", errors="ignore")
    # path lines look like: "path" "D:\\SteamLibrary"
    matches = re.findall(r'"path"\s+"([^"]+)"', text)
    for m in matches:
        fixed = m.replace("\\\\", "/").replace("\\", "/")
        p = Path(fixed)
        if p.exists():
            roots.append(p)
    return roots


def _steam_libraries() -> list[Path]:
    root = _steam_root()
    libs = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    libs.extend(_parse_libraryfolders(vdf))

    uniq: list[Path] = []
    seen: set[str] = set()
    for p in libs:
        key = str(p.resolve()) if p.exists() else str(p)
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def scan_installed_games() -> list[SteamGame]:
    games: list[SteamGame] = []
    for lib in _steam_libraries():
        steamapps = lib / "steamapps"
        if not steamapps.exists():
            continue
        for manifest in steamapps.glob("appmanifest_*.acf"):
            text = manifest.read_text(encoding="utf-8", errors="ignore")
            appid_m = re.search(r'"appid"\s+"(\d+)"', text)
            name_m = re.search(r'"name"\s+"([^"]+)"', text)
            if not appid_m or not name_m:
                continue
            games.append(SteamGame(appid=appid_m.group(1), name=name_m.group(1), manifest_path=str(manifest)))
    return games


def find_game(game_name: str) -> list[SteamGame]:
    query = _norm(game_name)
    if not query:
        return []

    candidates = scan_installed_games()
    direct = [g for g in candidates if query in _norm(g.name)]
    if direct:
        return direct

    words = [w for w in query.split(" ") if len(w) > 2]
    if not words:
        return []
    soft = [g for g in candidates if sum(1 for w in words if w in _norm(g.name)) >= max(1, len(words) - 1)]
    return soft


def play_game_smart(game: str, appid: str | None = None, install_if_missing: bool = False) -> dict:
    if not (game or "").strip():
        return {"error": "Debes indicar un juego."}

    matches = find_game(game)
    if matches:
        selected = matches[0]
        webbrowser.open(f"steam://run/{selected.appid}")
        return {
            "flow": "play_game_smart",
            "status": "launched",
            "game": selected.name,
            "appid": selected.appid,
            "matches": [m.name for m in matches[:5]],
        }

    search_url = f"https://store.steampowered.com/search/?term={urllib.parse.quote_plus(game)}"
    webbrowser.open(search_url)

    if install_if_missing and appid:
        webbrowser.open(f"steam://install/{appid}")
        return {
            "flow": "play_game_smart",
            "status": "install_started",
            "game": game,
            "appid": str(appid),
            "store_search": search_url,
            "next_step": "Despues de instalar, pide abrir el juego para lanzarlo automaticamente.",
        }

    return {
        "flow": "play_game_smart",
        "status": "not_installed",
        "game": game,
        "store_search": search_url,
        "action_required": "Preguntar al usuario si desea instalarlo. Si responde si, ejecutar play_game_smart con install_if_missing=true y appid.",
    }
