from __future__ import annotations

import datetime as dt
import subprocess
from pathlib import Path


def _safe_run(cmd: list[str]) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.returncode == 0, (p.stdout or p.stderr or "").strip()
    except Exception as e:
        return False, str(e)


def list_running_apps(limit: int = 20) -> list[str]:
    ok, out = _safe_run(["tasklist"])
    if not ok:
        return []
    apps: list[str] = []
    for line in out.splitlines()[3:]:
        parts = line.split()
        if parts:
            name = parts[0].lower()
            if name.endswith(".exe"):
                apps.append(name)
    uniq = sorted(set(apps))
    return uniq[:limit]


def get_runtime_context() -> dict:
    context = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "hour": dt.datetime.now().hour,
        "running_apps": list_running_apps(),
        "cpu_percent": None,
        "ram_percent": None,
        "battery_percent": None,
        "plugged": None,
    }
    try:
        import psutil

        context["cpu_percent"] = psutil.cpu_percent(interval=0.3)
        vm = psutil.virtual_memory()
        context["ram_percent"] = vm.percent
        try:
            bat = psutil.sensors_battery()
            if bat:
                context["battery_percent"] = bat.percent
                context["plugged"] = bat.power_plugged
        except Exception:
            pass
    except Exception:
        pass
    return context


def evaluate_precheck(tool: str, args: dict, context: dict) -> tuple[bool, str]:
    hour = int(context.get("hour") or 0)

    if tool in {"take_photos", "photo_pro_flow"}:
        try:
            import cv2

            cap = cv2.VideoCapture(0)
            ok = cap.isOpened()
            cap.release()
            if not ok:
                return False, "Camara no disponible en este momento."
        except Exception:
            return False, "No se pudo validar la camara."

    if tool == "set_brightness" and context.get("battery_percent") is not None:
        battery = float(context.get("battery_percent") or 0)
        target = int(args.get("value", 50))
        if battery < 15 and target > 70 and not bool(context.get("plugged")):
            return False, "Bateria baja: evitar brillo alto sin cargador."

    if tool == "open_app":
        target = str(args.get("target", "")).lower().strip()
        if target.startswith("http") and hour >= 2 and hour <= 6:
            return True, "OK (hora nocturna; navegacion web permitida)"

    return True, "OK"


def default_picture_folder() -> str:
    return str(Path.home() / "Pictures" / "Camera Roll")
