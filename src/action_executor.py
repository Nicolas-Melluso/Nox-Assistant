"""
Ejecutor de acciones para NOX — Fase 3.

Dado un intent y sus entidades, ejecuta la accion real en Windows.
Retorna un dict: {"status": "ok" | "error" | "confirm_required" | "not_implemented", "message": str}

Intents marcados como RISKY_INTENTS requieren confirmacion antes de ejecutarse.
El caller (chat_nox) es responsable de pedir la confirmacion y luego llamar con force=True.
"""

import ctypes
import datetime
import os
import subprocess
import threading
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Optional

# ── Intents peligrosos (requieren confirmacion) ───────────────────────────────

RISKY_INTENTS = {
    "pc_shutdown",
    "pc_restart",
    "pc_hibernate",
    "delete_file",
    "delete_folder",
    "empty_recycle_bin",
}

# ── Virtual key codes de Windows ─────────────────────────────────────────────

_VK_MEDIA_NEXT_TRACK  = 0xB0
_VK_MEDIA_PREV_TRACK  = 0xB1
_VK_MEDIA_STOP        = 0xB2
_VK_MEDIA_PLAY_PAUSE  = 0xB3
_VK_VOLUME_MUTE       = 0xAD
_VK_VOLUME_DOWN       = 0xAE
_VK_VOLUME_UP         = 0xAF


def _press_key(vk: int) -> None:
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)


# ── Volumen exacto via pycaw (con fallback a teclas) ─────────────────────────

def _set_volume_exact(pct: int) -> bool:
    """Setea el volumen del sistema al porcentaje dado. Retorna True si ok."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0, min(100, pct)) / 100.0, None)
        return True
    except Exception:
        return False


def _get_volume() -> Optional[int]:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return round(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return None


def _set_volume_with_fallback(target_pct: int) -> tuple[bool, str]:
    target = max(0, min(100, int(target_pct)))

    # Primer intento: ajuste exacto con pycaw.
    if _set_volume_exact(target):
        return True, "exact"

    # Fallback: aproximacion por teclas multimedia.
    current = _get_volume()
    if current is None:
        for _ in range(5):
            _press_key(_VK_VOLUME_UP)
        return True, "fallback_unknown"

    if target > current:
        steps = max(1, min(50, (target - current) // 2))
        for _ in range(steps):
            _press_key(_VK_VOLUME_UP)
    elif target < current:
        steps = max(1, min(50, (current - target) // 2))
        for _ in range(steps):
            _press_key(_VK_VOLUME_DOWN)

    return True, "fallback_steps"


# ── Screenshot via Pillow ─────────────────────────────────────────────────────

def _take_screenshot() -> str:
    from PIL import ImageGrab

    screenshots_dir = Path.home() / "Pictures" / "Screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = screenshots_dir / f"nox_screenshot_{ts}.png"
    img = ImageGrab.grab()
    img.save(path)
    return str(path)


def _take_camera_photo() -> str:
    """
    Toma una foto desde la camara principal y la guarda en Pictures/Camera Roll.
    """
    import cv2

    photos_dir = Path.home() / "Pictures" / "Camera Roll"
    photos_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = photos_dir / f"nox_camera_{ts}.jpg"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la camara")

    frame = None
    for _ in range(8):
        ok, current = cap.read()
        if ok:
            frame = current

    cap.release()

    if frame is None:
        raise RuntimeError("No se pudo capturar imagen de la camara")

    ok = cv2.imwrite(str(path), frame)
    if not ok:
        raise RuntimeError("No se pudo guardar la foto")
    return str(path)


# ── Timer en background ───────────────────────────────────────────────────────

_active_timers: dict[str, threading.Timer] = {}


def _start_timer(seconds: int, label: str = "NOX Timer") -> None:
    def _on_done():
        ctypes.windll.user32.MessageBoxW(0, f"{label} completado!", "NOX", 0x40)

    timer = threading.Timer(seconds, _on_done)
    timer.daemon = True
    timer.start()
    _active_timers[label] = timer


# ── Utilidades subprocess ─────────────────────────────────────────────────────

def _run(cmd: list[str]) -> bool:
    try:
        subprocess.Popen(cmd, shell=False)
        return True
    except Exception:
        return False


def _run_ps(script: str) -> bool:
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
            shell=False,
        )
        return True
    except Exception:
        return False


def _open_app(app_name: str) -> bool:
    return _run(["cmd", "/c", "start", "", app_name])


def _close_app(process_name: str) -> bool:
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", process_name],
            capture_output=True,
        )
        return True
    except Exception:
        return False


def _open_folder(path: str) -> bool:
    return _run(["explorer.exe", path])


# ── Mapa de apps conocidas ────────────────────────────────────────────────────

_APP_OPEN = {
    "open_spotify":   ("spotify",          None),
    "open_youtube":   (None,               "https://youtube.com"),
    "open_netflix":   (None,               "https://netflix.com"),
    "open_discord":   (None,               "discord://"),
    "open_whatsapp":  ("whatsapp",         None),
    "open_steam":     (None,               "steam://open/main"),
    "open_chrome":    ("chrome",           None),
    "open_edge":      ("msedge",           None),
}

_APP_CLOSE = {
    "close_spotify":  "Spotify.exe",
    "close_youtube":  "chrome.exe",
    "close_netflix":  "chrome.exe",
    "close_discord":  "Discord.exe",
    "close_whatsapp": "WhatsApp.exe",
    "close_steam":    "steam.exe",
    "close_chrome":   "chrome.exe",
    "close_edge":     "msedge.exe",
}

_FOLDER_OPEN = {
    "open_downloads":         str(Path.home() / "Downloads"),
    "open_documents":         str(Path.home() / "Documents"),
    "open_desktop_folder":    str(Path.home() / "Desktop"),
    "open_screenshots_folder": str(Path.home() / "Pictures" / "Screenshots"),
}

# ── Ejecutor principal ────────────────────────────────────────────────────────

def execute_action(intent: str, entities: dict, force: bool = False) -> dict:
    """
    Ejecuta la accion correspondiente al intent.

    Args:
        intent:   intent clasificado
        entities: entidades extraidas
        force:    si True, omite la verificacion de RISKY_INTENTS

    Returns:
        {"status": "ok"|"error"|"confirm_required"|"not_implemented", "message": str}
    """

    if intent in RISKY_INTENTS and not force:
        return {"status": "confirm_required", "message": f"'{intent}' es una accion irreversible. ¿Confirmas?"}

    # ── PC ────────────────────────────────────────────────────────────────────

    if intent == "pc_shutdown":
        _run(["shutdown", "/s", "/t", "5"])
        return {"status": "ok", "message": "Apagando la PC en 5 segundos."}

    if intent == "pc_restart":
        _run(["shutdown", "/r", "/t", "5"])
        return {"status": "ok", "message": "Reiniciando la PC en 5 segundos."}

    if intent == "pc_sleep":
        _run_ps("Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)")
        return {"status": "ok", "message": "Entrando en suspension."}

    if intent == "pc_hibernate":
        _run(["shutdown", "/h"])
        return {"status": "ok", "message": "Hibernando la PC."}

    if intent == "pc_lock":
        ctypes.windll.user32.LockWorkStation()
        return {"status": "ok", "message": "PC bloqueada."}

    if intent == "pc_unlock":
        return {"status": "not_implemented", "message": "Desbloquear requiere ingresar la contrasena manualmente."}

    # ── Volumen ───────────────────────────────────────────────────────────────

    if intent == "set_volume":
        value = entities.get("value")
        if value is None:
            return {"status": "error", "message": "No se detecto valor de volumen."}
        ok, mode = _set_volume_with_fallback(value)
        if ok:
            if mode == "exact":
                return {"status": "ok", "message": f"Volumen configurado al {value}%."}
            return {"status": "ok", "message": f"Volumen ajustado cerca de {value}% (fallback)."}
        return {"status": "error", "message": "No se pudo ajustar volumen."}

    if intent == "volume_up":
        value = entities.get("value")
        if value is not None:
            ok, mode = _set_volume_with_fallback(value)
            if ok:
                if mode == "exact":
                    return {"status": "ok", "message": f"Volumen ajustado al {value}%."}
                return {"status": "ok", "message": f"Volumen ajustado cerca de {value}% (fallback)."}
        _press_key(_VK_VOLUME_UP)
        return {"status": "ok", "message": "Volumen subido."}

    if intent == "volume_down":
        value = entities.get("value")
        if value is not None:
            ok, mode = _set_volume_with_fallback(value)
            if ok:
                if mode == "exact":
                    return {"status": "ok", "message": f"Volumen ajustado al {value}%."}
                return {"status": "ok", "message": f"Volumen ajustado cerca de {value}% (fallback)."}
        _press_key(_VK_VOLUME_DOWN)
        return {"status": "ok", "message": "Volumen bajado."}

    if intent == "volume_mute":
        _press_key(_VK_VOLUME_MUTE)
        return {"status": "ok", "message": "Audio silenciado."}

    if intent == "volume_unmute":
        _press_key(_VK_VOLUME_MUTE)
        return {"status": "ok", "message": "Audio activado."}

    if intent == "mute_microphone":
        return {"status": "not_implemented", "message": "Mutear microfono requiere configuracion de dispositivo especifica."}

    # ── Brillo ────────────────────────────────────────────────────────────────

    if intent == "set_brightness":
        value = entities.get("value")
        if value is None:
            return {"status": "error", "message": "No se detecto valor de brillo."}
        _run_ps(
            f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)."
            f"WmiSetBrightness(1,{value})"
        )
        return {"status": "ok", "message": f"Brillo configurado al {value}%."}

    if intent in {"brightness_up", "brightness_down"}:
        value = entities.get("value")
        if value is not None:
            _run_ps(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{value})")
            return {"status": "ok", "message": f"Brillo ajustado al {value}%."}
        direction = "aumentado" if intent == "brightness_up" else "reducido"
        step = 10 if intent == "brightness_up" else -10
        _run_ps(
            f"$b=(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods);"
            f"$cur=(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness;"
            f"$b.WmiSetBrightness(1,[Math]::Max(0,[Math]::Min(100,$cur+({step}))))"
        )
        return {"status": "ok", "message": f"Brillo {direction}."}

    # ── Wifi / Bluetooth / Modos ──────────────────────────────────────────────

    if intent == "wifi_on":
        _run_ps("Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false")
        return {"status": "ok", "message": "WiFi activado."}

    if intent == "wifi_off":
        _run_ps("Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false")
        return {"status": "ok", "message": "WiFi desactivado."}

    if intent == "bluetooth_on":
        _run_ps("Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false")
        return {"status": "ok", "message": "Bluetooth activado."}

    if intent == "bluetooth_off":
        _run_ps("Get-PnpDevice -Class Bluetooth | Disable-PnpDevice -Confirm:$false")
        return {"status": "ok", "message": "Bluetooth desactivado."}

    if intent in {"airplane_mode_on", "airplane_mode_off", "night_mode_on", "night_mode_off"}:
        return {"status": "not_implemented", "message": "Este modo requiere configuracion manual desde el Centro de actividades de Windows."}

    # ── Apps ──────────────────────────────────────────────────────────────────

    if intent in _APP_OPEN:
        exe, url = _APP_OPEN[intent]
        app_label = intent.replace("open_", "").capitalize()
        if intent == "open_youtube" and entities.get("query"):
            query = urllib.parse.quote_plus(str(entities["query"]))
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return {"status": "ok", "message": f"Abriendo YouTube y buscando: {entities['query']}"}
        if exe:
            _open_app(exe)
        else:
            webbrowser.open(url)
        return {"status": "ok", "message": f"Abriendo {app_label}."}

    if intent in _APP_CLOSE:
        proc = _APP_CLOSE[intent]
        _close_app(proc)
        app_label = intent.replace("close_", "").capitalize()
        return {"status": "ok", "message": f"Cerrando {app_label}."}

    # ── Carpetas del sistema ──────────────────────────────────────────────────

    if intent in _FOLDER_OPEN:
        _open_folder(_FOLDER_OPEN[intent])
        return {"status": "ok", "message": f"Abriendo carpeta."}

    # ── Task Manager ─────────────────────────────────────────────────────────

    if intent == "open_task_manager":
        _run(["taskmgr.exe"])
        return {"status": "ok", "message": "Abriendo Administrador de tareas."}

    if intent == "mode_focus_on":
        _set_volume_exact(25)
        _run_ps("(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,45)")
        _open_app("code")
        _open_app("chrome")
        return {
            "status": "ok",
            "message": "Modo foco activado: volumen bajo, brillo medio y entorno de trabajo abierto.",
        }

    if intent == "mode_gaming_on":
        _set_volume_exact(65)
        _run_ps("(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,70)")
        webbrowser.open("steam://open/main")
        webbrowser.open("discord://")
        return {
            "status": "ok",
            "message": "Modo gaming activado: Steam y Discord abiertos, perfil multimedia ajustado.",
        }

    if intent == "close_background_apps":
        return {"status": "not_implemented", "message": "Cierre de apps en background requiere especificar que procesos cerrar."}

    # ── Docker ────────────────────────────────────────────────────────────────

    if intent == "restart_docker":
        _run_ps("Restart-Service com.docker.service -Force")
        return {"status": "ok", "message": "Reiniciando servicio Docker."}

    # ── Turn on PC (WoL) ──────────────────────────────────────────────────────

    if intent == "turn_on_pc":
        return {"status": "not_implemented", "message": "Encender otra PC requiere Wake-on-LAN configurado con la MAC de destino."}

    # ── Browser ───────────────────────────────────────────────────────────────

    if intent == "browser_search_web":
        query = entities.get("query", "")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}" if query else "https://www.google.com"
        webbrowser.open(url)
        return {"status": "ok", "message": f"Buscando: {query}" if query else "Abriendo Google."}

    if intent == "browser_open_history":
        webbrowser.open("chrome://history/")
        return {"status": "ok", "message": "Abriendo historial del navegador."}

    if intent in {
        "browser_new_tab", "browser_close_tab", "browser_next_tab",
        "browser_prev_tab", "browser_refresh", "browser_back",
        "browser_forward", "browser_home",
    }:
        return {"status": "not_implemented", "message": "Control del navegador requiere pyautogui. Pendiente Fase 3b."}

    # ── Media ─────────────────────────────────────────────────────────────────

    if intent == "media_play":
        _press_key(_VK_MEDIA_PLAY_PAUSE)
        return {"status": "ok", "message": "Reproduciendo."}

    if intent == "media_pause":
        _press_key(_VK_MEDIA_PLAY_PAUSE)
        return {"status": "ok", "message": "Pausado."}

    if intent == "media_next_track":
        _press_key(_VK_MEDIA_NEXT_TRACK)
        return {"status": "ok", "message": "Siguiente cancion."}

    if intent == "media_prev_track":
        _press_key(_VK_MEDIA_PREV_TRACK)
        return {"status": "ok", "message": "Cancion anterior."}

    if intent == "media_stop":
        _press_key(_VK_MEDIA_STOP)
        return {"status": "ok", "message": "Reproduccion detenida."}

    if intent in {"media_seek_forward", "media_seek_backward"}:
        return {"status": "not_implemented", "message": "Seek requiere control especifico de la app activa. Pendiente Fase 3b."}

    if intent in {"media_shuffle_on", "media_shuffle_off", "media_repeat_on", "media_repeat_off"}:
        return {"status": "not_implemented", "message": "Shuffle/repeat requiere integracion con Spotify API. Pendiente Fase 4."}

    # ── Timer ─────────────────────────────────────────────────────────────────

    if intent == "start_timer":
        seconds = entities.get("duration_seconds")
        if seconds:
            mins = seconds // 60
            secs = seconds % 60
            label = f"Timer {mins}m {secs}s" if secs else f"Timer {mins}m"
            _start_timer(seconds, label)
            try:
                subprocess.Popen(["explorer.exe", "ms-clock:timers"])
            except Exception:
                pass
            return {"status": "ok", "message": f"Timer iniciado: {label}. Abriendo app Reloj. Te avisare cuando termine."}
        return {"status": "error", "message": "No se pudo determinar la duracion del timer."}

    if intent == "stop_timer":
        for label, timer in list(_active_timers.items()):
            timer.cancel()
        _active_timers.clear()
        return {"status": "ok", "message": "Todos los timers cancelados."}

    # ── Alarma ────────────────────────────────────────────────────────────────

    if intent == "set_alarm":
        time_val = entities.get("time")
        if time_val:
            _run_ps(
                f"$action = New-ScheduledTaskAction -Execute 'powershell.exe' "
                f"-Argument '-WindowStyle Normal -Command \"[System.Windows.Forms.MessageBox]::Show(\\\"Alarma NOX!\\\")\"'; "
                f"$trigger = New-ScheduledTaskTrigger -Daily -At '{time_val}'; "
                f"Register-ScheduledTask -TaskName 'NOX_Alarm' -Action $action -Trigger $trigger -Force"
            )
            return {"status": "ok", "message": f"Alarma programada para las {time_val}."}
        return {"status": "error", "message": "No se detecto la hora de la alarma."}

    if intent == "cancel_alarm":
        _run_ps("Unregister-ScheduledTask -TaskName 'NOX_Alarm' -Confirm:$false")
        return {"status": "ok", "message": "Alarma cancelada."}

    # ── Info del sistema ──────────────────────────────────────────────────────

    if intent == "get_time":
        now = datetime.datetime.now().strftime("%H:%M")
        return {"status": "ok", "message": f"Son las {now}."}

    if intent == "get_date":
        today = datetime.date.today()
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        nombre_dia = dias[today.weekday()]
        nombre_mes = meses[today.month - 1]
        return {"status": "ok", "message": f"Hoy es {nombre_dia} {today.day} de {nombre_mes} de {today.year}."}

    if intent == "get_cpu_usage":
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            return {"status": "ok", "message": f"Uso de CPU: {cpu}%."}
        except ImportError:
            return {"status": "error", "message": "psutil no esta instalado."}

    if intent == "get_ram_usage":
        try:
            import psutil
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            return {"status": "ok", "message": f"RAM: {used_gb:.1f} GB usados de {total_gb:.1f} GB ({mem.percent}%)."}
        except ImportError:
            return {"status": "error", "message": "psutil no esta instalado."}

    if intent == "get_battery_status":
        try:
            import psutil
            bat = psutil.sensors_battery()
            if bat is None:
                return {"status": "ok", "message": "No se detecto bateria (PC de escritorio)."}
            estado = "cargando" if bat.power_plugged else "descargando"
            return {"status": "ok", "message": f"Bateria: {bat.percent:.0f}% — {estado}."}
        except ImportError:
            return {"status": "error", "message": "psutil no esta instalado."}

    if intent == "get_network_status":
        try:
            import psutil
            stats = psutil.net_if_stats()
            activos = [name for name, s in stats.items() if s.isup]
            return {"status": "ok", "message": f"Interfaces activas: {', '.join(activos)}."}
        except ImportError:
            return {"status": "error", "message": "psutil no esta instalado."}

    if intent == "get_weather":
        city = entities.get("city", "tu ciudad")
        return {"status": "not_implemented", "message": f"Clima de {city}: requiere API key de OpenWeatherMap. Pendiente Fase 4."}

    # ── Screenshot ────────────────────────────────────────────────────────────

    if intent == "take_screenshot":
        try:
            source = entities.get("source", "screen")
            if source == "camera":
                path = _take_camera_photo()
                return {"status": "ok", "message": f"Foto tomada con camara y guardada en: {path}"}

            path = _take_screenshot()
            return {"status": "ok", "message": f"Captura de pantalla guardada en: {path}"}
        except Exception as e:
            return {"status": "error", "message": f"Error al capturar pantalla: {e}"}

    if intent == "start_screen_recording":
        _run(["explorer.exe", "ms-screenclip:"])
        return {"status": "ok", "message": "Abriendo herramienta de grabacion de Windows."}

    if intent == "stop_screen_recording":
        return {"status": "not_implemented", "message": "Detener grabacion requiere integracion con la herramienta activa."}

    # ── Archivos ──────────────────────────────────────────────────────────────

    if intent == "create_file":
        filename = entities.get("filename")
        if filename:
            path = Path.home() / "Desktop" / filename
            path.touch()
            return {"status": "ok", "message": f"Archivo '{filename}' creado en el escritorio."}
        return {"status": "error", "message": "No se especifico nombre de archivo."}

    if intent == "delete_file":
        filename = entities.get("filename")
        if filename:
            path = Path.home() / "Desktop" / filename
            if path.exists():
                path.unlink()
                return {"status": "ok", "message": f"Archivo '{filename}' eliminado."}
            return {"status": "error", "message": f"Archivo '{filename}' no encontrado en el escritorio."}
        return {"status": "error", "message": "No se especifico nombre de archivo."}

    if intent == "create_folder":
        folder = entities.get("folder_name")
        if folder:
            path = Path.home() / "Desktop" / folder
            path.mkdir(exist_ok=True)
            return {"status": "ok", "message": f"Carpeta '{folder}' creada en el escritorio."}
        return {"status": "error", "message": "No se especifico nombre de carpeta."}

    if intent == "delete_folder":
        folder = entities.get("folder_name")
        if folder:
            path = Path.home() / "Desktop" / folder
            if path.exists() and path.is_dir():
                import shutil
                shutil.rmtree(path)
                return {"status": "ok", "message": f"Carpeta '{folder}' eliminada."}
            return {"status": "error", "message": f"Carpeta '{folder}' no encontrada en el escritorio."}
        return {"status": "error", "message": "No se especifico nombre de carpeta."}

    if intent == "empty_recycle_bin":
        _run_ps("Clear-RecycleBin -Force")
        return {"status": "ok", "message": "Papelera vaciada."}

    if intent in {"rename_file", "move_file", "copy_file"}:
        return {"status": "not_implemented", "message": "Esta operacion requiere origen y destino. Pendiente Fase 3b."}

    # ── Smart home ────────────────────────────────────────────────────────────

    if intent in {
        "smart_lights_on", "smart_lights_off", "smart_lights_dim", "smart_lights_brighten",
        "thermostat_set_temp", "thermostat_temp_up", "thermostat_temp_down",
        "door_lock", "door_unlock", "camera_view_frontdoor",
    }:
        return {"status": "not_implemented", "message": "Smart home requiere integracion con tu hub (Home Assistant / Google Home). Pendiente Fase 4."}

    # ── Comunicacion ──────────────────────────────────────────────────────────

    if intent in {"send_email", "send_whatsapp_message", "call_contact", "join_meeting", "read_unread_emails"}:
        return {"status": "not_implemented", "message": "Comunicacion requiere integracion con Gmail/WhatsApp API. Pendiente Fase 4."}

    # ── Fallback ──────────────────────────────────────────────────────────────

    return {"status": "not_implemented", "message": f"Accion '{intent}' aun no implementada."}
