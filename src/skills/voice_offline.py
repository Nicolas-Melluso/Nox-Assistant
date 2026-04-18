from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
from pathlib import Path
from typing import Callable

_voice_stop_event = threading.Event()
_voice_active = False
_voice_thread: threading.Thread | None = None
_voice_queue: queue.Queue[str] = queue.Queue()
_voice_lock = threading.Lock()
_on_command_cb: Callable[[str], None] | None = None
_on_wake_cb: Callable[[str], None] | None = None
_on_partial_cb: Callable[[str], None] | None = None
_last_error: str | None = None
_tts_lock = threading.Lock()
_tts_engine = None
_wake_word = "nox"
_wake_aliases: set[str] = {"nox", "noc", "nov"}

# Palabras comunes en español que podrían estar a distancia ≤1 de 'nox' o alias.
# Se excluyen explícitamente para evitar falsos positivos.
_WAKE_DENYLIST: frozenset[str] = frozenset({
    "nos", "no", "not", "nor", "now", "lot", "got", "pot", "dot", "hot",
    "fox", "box", "los", "las", "uno", "una", "hay", "hoy", "voy",
    "soy", "boy", "toy", "joy", "roy", "coy", "doy",
    "knox",  # 'k' + 'nox' = distancia 1, pero no es la palabra objetivo
})


def _levenshtein(a: str, b: str) -> int:
    """Distancia de edición mínima entre dos cadenas."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def _is_wake_token(tok: str) -> bool:
    """True si tok coincide con algún alias exacto o está a distancia ≤1 del wake word principal."""
    if not tok or tok in _WAKE_DENYLIST:
        return False
    if tok in _wake_aliases:
        return True
    return _levenshtein(tok, _wake_word) <= 1
_listen_window_sec = 8
_strict_wake_prefix = True
_allow_followup_after_wake = False
_last_partial_seen = ""
_last_partial_ts = 0.0
_last_command_seen = ""
_last_command_ts = 0.0
_last_wake_ts = 0.0
_active_input_device = None
_active_sample_rate = None


def _int_or_str(text: str):
    t = (text or "").strip()
    if t == "":
        return None
    try:
        return int(t)
    except ValueError:
        return t


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _normalize_text(text: str) -> str:
    content = (text or "").lower().strip()
    content = re.sub(r"[^\w\s]", " ", content, flags=re.UNICODE)
    content = re.sub(r"\s+", " ", content).strip()
    return content


def _extract_after_wake(content: str) -> tuple[bool, str]:
    tokens = content.split()
    if not tokens:
        return False, ""

    # Modo estricto: la frase debe empezar por wake word ("nox ...").
    if _strict_wake_prefix:
        if _is_wake_token(tokens[0]):
            return True, " ".join(tokens[1:]).strip()
        return False, ""

    for i, tok in enumerate(tokens):
        if _is_wake_token(tok):
            remainder = " ".join(tokens[i + 1 :]).strip()
            return True, remainder
    return False, ""


def _dispatch_command_async(command_text: str) -> None:
    global _last_error, _last_command_seen, _last_command_ts

    cmd = _normalize_text(command_text)
    now = time.time()
    if cmd and cmd == _last_command_seen and (now - _last_command_ts) < 2.5:
        return
    _last_command_seen = cmd
    _last_command_ts = now

    def _runner() -> None:
        global _last_error
        try:
            if _on_command_cb:
                _on_command_cb(cmd or command_text)
        except Exception as e:
            _last_error = str(e)

    threading.Thread(target=_runner, daemon=True, name="nox-voice-cmd").start()


def _process_transcript(text: str, is_partial: bool = False) -> None:
    global _last_error, _last_wake_ts
    content = _normalize_text(text)
    if not content:
        return

    try:
        if _on_partial_cb:
            _on_partial_cb(content)
    except Exception as e:
        _last_error = str(e)

    now = time.time()
    state = getattr(_process_transcript, "_state", {"armed_until": 0.0})
    armed_until = float(state.get("armed_until", 0.0))

    has_wake, inline_command = _extract_after_wake(content)
    if has_wake:
        # Debounce: ignorar wake duplicado si ya se disparó hace menos de 2 segundos.
        if now - _last_wake_ts < 2.0:
            return
        _last_wake_ts = now
        state["armed_until"] = now + float(_listen_window_sec)
        setattr(_process_transcript, "_state", state)
        try:
            if _on_wake_cb:
                _on_wake_cb(content)
        except Exception as e:
            _last_error = str(e)

        # Caso "Nox <comando>" en la misma frase — solo si es resultado final.
        if inline_command and not is_partial:
            _voice_queue.put(inline_command)
            state["armed_until"] = 0.0
            setattr(_process_transcript, "_state", state)
            _dispatch_command_async(inline_command)
        elif not _allow_followup_after_wake:
            state["armed_until"] = 0.0
            setattr(_process_transcript, "_state", state)
        return

    # Ventana de follow-up: solo dispara en resultado final, no en parciales.
    if _allow_followup_after_wake and not is_partial and now <= armed_until:
        _voice_queue.put(content)
        state["armed_until"] = 0.0
        setattr(_process_transcript, "_state", state)
        _dispatch_command_async(content)


def _listener_loop() -> None:
    global _voice_active, _last_error, _last_partial_seen, _last_partial_ts, _active_input_device, _active_sample_rate
    try:
        import importlib

        sd = importlib.import_module("sounddevice")
        vosk = importlib.import_module("vosk")

        model_path = os.getenv("NOX_VOSK_MODEL_PATH", str(_workspace_root() / "models" / "vosk-model-small-es-0.42"))
        if not Path(model_path).exists():
            _last_error = (
                "Modelo Vosk no encontrado. Descarga uno en espanol y define NOX_VOSK_MODEL_PATH en .env"
            )
            _voice_active = False
            return

        device_env = os.getenv("NOX_VOICE_DEVICE", "")
        device_opt = _int_or_str(device_env)
        sample_rate_opt = os.getenv("NOX_VOICE_SAMPLE_RATE", "").strip()
        selected_device = device_opt

        def _pick_input_device() -> tuple[object | None, int]:
            # 1) Intento con device especificado
            if selected_device is not None:
                try:
                    dev_info = sd.query_devices(selected_device, "input")
                    sr = int(sample_rate_opt) if sample_rate_opt else int(dev_info["default_samplerate"])
                    return selected_device, sr
                except Exception:
                    pass

            # 2) Fallback al default de sistema
            try:
                dev_info = sd.query_devices(None, "input")
                sr = int(sample_rate_opt) if sample_rate_opt else int(dev_info["default_samplerate"])
                return None, sr
            except Exception:
                pass

            # 3) Fallback: primer dispositivo con entrada disponible
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                try:
                    if int(d.get("max_input_channels", 0)) > 0:
                        sr = int(sample_rate_opt) if sample_rate_opt else int(d["default_samplerate"])
                        return i, sr
                except Exception:
                    continue

            raise RuntimeError("No se encontro ningun dispositivo de entrada valido")

        selected_device, sample_rate = _pick_input_device()
        _active_input_device = selected_device
        _active_sample_rate = sample_rate

        model = vosk.Model(model_path)
        rec = vosk.KaldiRecognizer(model, sample_rate)
        audio_q: queue.Queue[bytes] = queue.Queue()
        _last_partial_seen = ""
        _last_partial_ts = 0.0

        def _audio_cb(indata, frames, _time_info, status):
            if status:
                return
            audio_q.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=sample_rate,
            blocksize=8000,
            device=selected_device,
            dtype="int16",
            channels=1,
            callback=_audio_cb,
        ):
            while not _voice_stop_event.is_set():
                try:
                    data = audio_q.get(timeout=0.4)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    try:
                        result = json.loads(rec.Result())
                    except Exception:
                        result = {}
                    text = (result.get("text") or "").strip()
                    _process_transcript(text)
                else:
                    # Detectar wake word en parcial evita depender de pausas largas.
                    try:
                        partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                    except Exception:
                        partial = ""

                    partial_norm = _normalize_text(partial)
                    if not partial_norm:
                        continue

                    now = time.time()
                    # Debounce para no reprocesar la misma parcial en loop.
                    if partial_norm == _last_partial_seen and (now - _last_partial_ts) < 0.8:
                        continue
                    _last_partial_seen = partial_norm
                    _last_partial_ts = now

                    _process_transcript(partial_norm, is_partial=True)
    except Exception as e:
        _last_error = f"Listener offline no disponible: {e}"
    finally:
        _voice_active = False
        _voice_stop_event.set()


def speak_text(text: str) -> dict:
    global _tts_engine
    try:
        import importlib

        pyttsx3 = importlib.import_module("pyttsx3")
        with _tts_lock:
            if _tts_engine is None:
                _tts_engine = pyttsx3.init()
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        return {"spoken": True, "text": text}
    except Exception as e:
        return {"error": f"TTS offline no disponible: {e}"}


def start_voice_control(
    on_command: Callable[[str], None] | None = None,
    on_wake: Callable[[str], None] | None = None,
    on_partial: Callable[[str], None] | None = None,
    wake_word: str | None = None,
    listen_window_sec: int | None = None,
) -> dict:
    global _voice_active, _voice_thread, _on_command_cb, _on_wake_cb, _on_partial_cb, _wake_word, _wake_aliases, _listen_window_sec, _strict_wake_prefix, _allow_followup_after_wake, _last_error
    with _voice_lock:
        if _voice_active:
            return {"started": False, "message": "Voice control ya estaba activo.", "wake_word": _wake_word}

        _voice_stop_event.clear()
        _on_command_cb = on_command
        _on_wake_cb = on_wake
        _on_partial_cb = on_partial
        _wake_word = (wake_word or os.getenv("NOX_WAKE_WORD", "nox")).strip().lower()
        aliases_raw = os.getenv("NOX_WAKE_ALIASES", "nox,noc,nov")
        aliases = {a.strip().lower() for a in aliases_raw.split(",") if a.strip()}
        aliases.add(_wake_word)
        _wake_aliases = aliases
        _listen_window_sec = int(listen_window_sec or int(os.getenv("NOX_LISTEN_WINDOW_SEC", "8")))
        _strict_wake_prefix = os.getenv("NOX_STRICT_WAKE_PREFIX", "true").strip().lower() in {"1", "true", "yes", "si", "on"}
        _allow_followup_after_wake = os.getenv("NOX_ALLOW_FOLLOWUP_AFTER_WAKE", "false").strip().lower() in {"1", "true", "yes", "si", "on"}
        _last_error = None
        _voice_active = True

        _voice_thread = threading.Thread(target=_listener_loop, daemon=True, name="nox-voice-listener")
        _voice_thread.start()

        # Arranque defensivo: si el hilo muere rapido (ej. modelo faltante), reportarlo como fallo.
        for _ in range(8):
            time.sleep(0.15)
            if _voice_active:
                continue
            if _last_error:
                break

        if not _voice_active and _last_error:
            return {
                "started": False,
                "wake_word": _wake_word,
                "listen_window_sec": _listen_window_sec,
                "message": _last_error,
            }

        return {
            "started": True,
            "wake_word": _wake_word,
            "wake_aliases": sorted(_wake_aliases),
            "listen_window_sec": _listen_window_sec,
            "strict_wake_prefix": _strict_wake_prefix,
            "allow_followup_after_wake": _allow_followup_after_wake,
            "message": "Modo escucha offline iniciado. Di 'Nox' y luego tu comando.",
        }


def stop_voice_control() -> dict:
    global _voice_active
    _voice_stop_event.set()
    _voice_active = False
    return {"stopped": True, "message": "Modo escucha detenido (panic stop)."}


def pop_voice_command(timeout: float = 0.0) -> str | None:
    try:
        if timeout > 0:
            return _voice_queue.get(timeout=timeout)
        return _voice_queue.get_nowait()
    except queue.Empty:
        return None


def voice_status() -> dict:
    return {
        "active": _voice_active,
        "wake_word": _wake_word,
        "wake_aliases": sorted(_wake_aliases),
        "listen_window_sec": _listen_window_sec,
        "strict_wake_prefix": _strict_wake_prefix,
        "allow_followup_after_wake": _allow_followup_after_wake,
        "voice_device": _active_input_device if _active_input_device is not None else os.getenv("NOX_VOICE_DEVICE", "default"),
        "voice_sample_rate": _active_sample_rate if _active_sample_rate is not None else os.getenv("NOX_VOICE_SAMPLE_RATE", "auto"),
        "last_error": _last_error,
    }
