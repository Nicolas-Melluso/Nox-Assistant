from __future__ import annotations

import json
import subprocess
import threading
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path

from src.skills.context import default_picture_folder
from src.skills.voice_offline import speak_text, start_voice_control, stop_voice_control


def _tool_take_photos(count: int = 1) -> dict:
    try:
        import cv2

        pictures_dir = Path(default_picture_folder())
        pictures_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {"error": "No se pudo acceder a la camara."}

        paths = []
        for i in range(max(1, min(count, 8))):
            for _ in range(4):
                cap.read()
            ok, frame = cap.read()
            if ok:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                p = str(pictures_dir / f"nox_cam_{ts}_{i+1}.jpg")
                cv2.imwrite(p, frame)
                paths.append(p)

        cap.release()
        return {"paths": paths, "count": len(paths)}
    except Exception as e:
        return {"error": f"Fallo al tomar fotos: {e}"}


def _tool_show_photo_picker(paths: list[str]) -> dict:
    try:
        import tkinter as tk
        from PIL import Image, ImageTk

        chosen = {"path": None}

        root = tk.Tk()
        root.title("NOX - Elige tu foto")
        root.configure(bg="#0D0D0D")
        root.attributes("-topmost", True)

        tk.Label(root, text="Elige una foto", bg="#0D0D0D", fg="#FFFFFF", font=("Segoe UI", 12, "bold")).pack(pady=8)
        frame = tk.Frame(root, bg="#0D0D0D")
        frame.pack(padx=8, pady=6)

        cols = 2
        for idx, path in enumerate(paths[:4]):
            try:
                img = Image.open(path)
                img.thumbnail((320, 220))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                continue
            btn = tk.Button(
                frame,
                image=photo,
                command=lambda p=path: (chosen.__setitem__("path", p), root.destroy()),
                bg="#1A0000",
                activebackground="#3B0000",
                relief="flat",
            )
            btn.image = photo
            btn.grid(row=idx // cols, column=idx % cols, padx=5, pady=5)

        tk.Button(root, text="Cancelar", command=root.destroy, bg="#7F1D1D", fg="#FFFFFF").pack(pady=(0, 8))
        root.mainloop()

        return {"chosen": chosen["path"]}
    except Exception as e:
        return {"error": f"Fallo en picker: {e}"}


def _tool_take_screenshot() -> dict:
    try:
        from PIL import ImageGrab

        pictures_dir = Path.home() / "Pictures" / "Screenshots"
        pictures_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(pictures_dir / f"nox_screen_{ts}.jpg")
        ImageGrab.grab().save(path)
        return {"path": path}
    except Exception as e:
        return {"error": f"Fallo screenshot: {e}"}


def _tool_set_volume(value: int) -> dict:
    val = max(0, min(100, int(value)))
    try:
        from ctypes import POINTER, cast

        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(val / 100, None)
        return {"set": val, "method": "pycaw"}
    except Exception:
        try:
            import keyboard

            for _ in range(50):
                keyboard.press_and_release("volumedown")
            for _ in range(int(val / 2)):
                keyboard.press_and_release("volumeup")
            return {"set": val, "method": "keyboard_fallback"}
        except Exception as e:
            return {"error": f"Fallo volumen: {e}"}


def _tool_set_brightness(value: int) -> dict:
    val = max(0, min(100, int(value)))
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode == 0:
        return {"set": val}
    return {"error": p.stderr.strip() or "No se pudo ajustar brillo."}


def _tool_open_app(target: str) -> dict:
    t = str(target).lower().strip()
    protocols = {"steam": "steam://open/main", "discord": "discord://", "spotify": "spotify:"}
    if t in protocols:
        webbrowser.open(protocols[t])
        return {"opened": t}

    if t in {"chrome", "vscode", "code"}:
        cmd = ["cmd", "/c", "start", "", "code" if t in {"vscode", "code"} else "chrome"]
        subprocess.Popen(cmd)
        return {"opened": t}

    if t in {"explorer", "notepad"}:
        subprocess.Popen(["explorer.exe"] if t == "explorer" else ["notepad.exe"])
        return {"opened": t}

    if t.startswith("http://") or t.startswith("https://"):
        webbrowser.open(target)
        return {"opened": target}

    try:
        subprocess.Popen(["cmd", "/c", "start", "", target])
        return {"opened": target}
    except Exception as e:
        return {"error": f"No se pudo abrir {target}: {e}"}


def _tool_open_folder(path: str) -> dict:
    resolved = str(Path(path).expanduser())
    subprocess.Popen(["explorer.exe", resolved])
    return {"opened": resolved}


def _tool_search_youtube(query: str) -> dict:
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(str(query))}"
    webbrowser.open(url)
    return {"query": query, "url": url}


def _tool_start_timer(minutes: int, label: str = "NOX Timer") -> dict:
    import ctypes

    mins = max(1, int(minutes))

    def _done() -> None:
        ctypes.windll.user32.MessageBoxW(0, f"{label} completado!", "NOX", 0x40)

    t = threading.Timer(mins * 60, _done)
    t.daemon = True
    t.start()
    try:
        subprocess.Popen(["explorer.exe", "ms-clock:timers"])
    except Exception:
        pass
    return {"started": True, "minutes": mins, "label": label}


def _tool_get_system_info() -> dict:
    try:
        import psutil

        info: dict = {
            "cpu_percent": psutil.cpu_percent(interval=0.4),
            "ram_percent": psutil.virtual_memory().percent,
        }
        bat = psutil.sensors_battery()
        if bat:
            info["battery_percent"] = bat.percent
            info["plugged"] = bat.power_plugged
        return info
    except Exception as e:
        return {"error": f"No se pudo leer info de sistema: {e}"}


def _tool_notify(title: str, message: str) -> dict:
    import ctypes

    ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0x40)
    return {"sent": True}


def _tool_activate_focus_mode() -> dict:
    r1 = _tool_set_volume(25)
    r2 = _tool_set_brightness(45)
    r3 = _tool_open_app("vscode")
    return {"ok": "error" not in r1 and "error" not in r2 and "error" not in r3, "steps": [r1, r2, r3]}


def _tool_activate_gaming_mode() -> dict:
    r1 = _tool_set_volume(65)
    r2 = _tool_set_brightness(70)
    r3 = _tool_open_app("steam")
    r4 = _tool_open_app("discord")
    return {"ok": all("error" not in x for x in [r1, r2, r3, r4]), "steps": [r1, r2, r3, r4]}


def _score_photo(path: str) -> dict:
    try:
        import cv2
        import numpy as np

        img = cv2.imread(path)
        if img is None:
            return {"path": path, "score": 0.0}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        brightness_score = max(0.0, 100.0 - abs(128.0 - brightness))
        final = sharpness * 0.7 + brightness_score * 0.3
        return {"path": path, "score": round(final, 2), "sharpness": round(sharpness, 2), "brightness": round(brightness, 2)}
    except Exception:
        return {"path": path, "score": 0.0}


def _tool_photo_pro_flow(count: int = 4) -> dict:
    taken = _tool_take_photos(count=max(2, min(6, int(count))))
    if "error" in taken:
        return taken
    paths = taken.get("paths", [])
    if not paths:
        return {"error": "No se tomaron fotos."}

    scored = sorted([_score_photo(p) for p in paths], key=lambda x: x.get("score", 0), reverse=True)
    best = scored[0]["path"] if scored else None

    picked = _tool_show_photo_picker(paths)
    chosen = picked.get("chosen") if isinstance(picked, dict) else None
    final_choice = chosen or best

    _tool_open_folder(default_picture_folder())
    return {
        "flow": "photo_pro",
        "count": len(paths),
        "scores": scored,
        "best_auto": best,
        "chosen_final": final_choice,
    }


def _tool_gaming_setup_flow(game_query: str = "") -> dict:
    steps = [
        _tool_set_volume(65),
        _tool_set_brightness(70),
        _tool_open_app("steam"),
        _tool_open_app("discord"),
    ]
    if game_query:
        steps.append(_tool_search_youtube(f"{game_query} settings"))
    return {"flow": "gaming_setup", "ok": all("error" not in s for s in steps), "steps": steps}


def _tool_focus_pomodoro_flow(minutes: int = 25) -> dict:
    mins = max(10, min(90, int(minutes)))
    steps = [
        _tool_set_volume(25),
        _tool_set_brightness(45),
        _tool_open_app("vscode"),
        _tool_start_timer(mins, "Pomodoro NOX"),
        _tool_notify("NOX", f"Modo foco activado por {mins} minutos."),
    ]
    return {"flow": "focus_pomodoro", "ok": all("error" not in s for s in steps), "steps": steps}


def _normalize_skill_args(name: str, args: dict) -> dict:
    normalized = dict(args or {})

    def _move_alias_to(target_key: str, aliases: tuple[str, ...]) -> None:
        if target_key not in normalized:
            for alias in aliases:
                if alias in normalized:
                    normalized[target_key] = normalized[alias]
                    break
        for alias in aliases:
            if alias != target_key:
                normalized.pop(alias, None)

    if name in {"set_brightness", "set_volume"}:
        _move_alias_to("value", ("value", "level", "percent", "brightness", "volume", "amount"))

    if name == "start_timer":
        _move_alias_to("minutes", ("minutes", "duration_minutes", "mins", "duration"))

    if name == "open_app" and "target" not in normalized:
        _move_alias_to("target", ("target", "app", "application", "name"))

    if name == "speak_text" and "text" not in normalized and "message" in normalized:
        normalized["text"] = normalized["message"]
    if name == "speak_text":
        normalized.pop("message", None)

    if name == "notify":
        if "title" not in normalized:
            normalized["title"] = "NOX"
        if "message" not in normalized and "text" in normalized:
            normalized["message"] = normalized["text"]
        normalized.pop("text", None)

    return normalized


def execute_skill(name: str, args: dict) -> dict:
    handler = SKILL_HANDLERS.get(name)
    if not handler:
        return {"error": f"Skill desconocida: {name}"}
    try:
        return handler(_normalize_skill_args(name, args))
    except Exception as e:
        return {"error": str(e)}


SKILL_HANDLERS = {
    "take_photos": lambda a: _tool_take_photos(**a),
    "show_photo_picker": lambda a: _tool_show_photo_picker(**a),
    "take_screenshot": lambda a: _tool_take_screenshot(),
    "set_volume": lambda a: _tool_set_volume(**a),
    "set_brightness": lambda a: _tool_set_brightness(**a),
    "open_app": lambda a: _tool_open_app(**a),
    "open_folder": lambda a: _tool_open_folder(**a),
    "search_youtube": lambda a: _tool_search_youtube(**a),
    "start_timer": lambda a: _tool_start_timer(**a),
    "get_system_info": lambda a: _tool_get_system_info(),
    "notify": lambda a: _tool_notify(**a),
    "activate_focus_mode": lambda a: _tool_activate_focus_mode(),
    "activate_gaming_mode": lambda a: _tool_activate_gaming_mode(),
    "photo_pro_flow": lambda a: _tool_photo_pro_flow(**a),
    "gaming_setup_flow": lambda a: _tool_gaming_setup_flow(**a),
    "focus_pomodoro_flow": lambda a: _tool_focus_pomodoro_flow(**a),
    "speak_text": lambda a: speak_text(**a),
    "voice_control_start": lambda a: start_voice_control(),
    "voice_control_stop": lambda a: stop_voice_control(),
}


def get_tool_names() -> set[str]:
    return set(SKILL_HANDLERS.keys())


def get_tools_manifest() -> list[dict]:
    return [
        {"type": "function", "function": {"name": "take_photos", "description": "Captura N fotos.", "parameters": {"type": "object", "properties": {"count": {"type": "integer", "default": 1}}, "required": []}}},
        {"type": "function", "function": {"name": "show_photo_picker", "description": "Muestra fotos para elegir una.", "parameters": {"type": "object", "properties": {"paths": {"type": "array", "items": {"type": "string"}}}, "required": ["paths"]}}},
        {"type": "function", "function": {"name": "take_screenshot", "description": "Toma screenshot.", "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {"name": "set_volume", "description": "Ajusta volumen 0-100.", "parameters": {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}}},
        {"type": "function", "function": {"name": "set_brightness", "description": "Ajusta brillo 0-100.", "parameters": {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}}},
        {"type": "function", "function": {"name": "open_app", "description": "Abre app o URL.", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}},
        {"type": "function", "function": {"name": "open_folder", "description": "Abre carpeta.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "search_youtube", "description": "Busca en YouTube.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
        {"type": "function", "function": {"name": "start_timer", "description": "Inicia timer.", "parameters": {"type": "object", "properties": {"minutes": {"type": "integer"}, "label": {"type": "string", "default": "NOX Timer"}}, "required": ["minutes"]}}},
        {"type": "function", "function": {"name": "get_system_info", "description": "Devuelve estado del sistema.", "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {"name": "notify", "description": "Notificacion local.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}}, "required": ["title", "message"]}}},
        {"type": "function", "function": {"name": "activate_focus_mode", "description": "Activa modo foco." , "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {"name": "activate_gaming_mode", "description": "Activa modo gaming." , "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {"name": "photo_pro_flow", "description": "Toma varias fotos, rankea y permite elegir la mejor.", "parameters": {"type": "object", "properties": {"count": {"type": "integer", "default": 4}}, "required": []}}},
        {"type": "function", "function": {"name": "gaming_setup_flow", "description": "Flujo premium gaming (ajustes + apps + opcional youtube).", "parameters": {"type": "object", "properties": {"game_query": {"type": "string", "default": ""}}, "required": []}}},
        {"type": "function", "function": {"name": "focus_pomodoro_flow", "description": "Flujo premium foco con pomodoro.", "parameters": {"type": "object", "properties": {"minutes": {"type": "integer", "default": 25}}, "required": []}}},
        {"type": "function", "function": {"name": "speak_text", "description": "Habla texto por TTS offline (si disponible).", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    ]
