"""FastAPI server para Nox - backend para app Electron."""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent_logging import append_step_log, get_log_path
from src.autonomous_agent import run_agent
from src.skills.voice_offline import speak_text, start_voice_control, stop_voice_control, voice_status

app = FastAPI(title="Nox API", version="0.4.0")

# CORS para Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str
    auto_confirm: bool = False


class AgentResponse(BaseModel):
    message: str
    tools_used: list[str]
    providers_used: list[str]
    run_id: str


# Estado global del servicio
service_state = {
    "running": False,
    "listening": False,
    "connected_clients": set(),
    "last_wake": "",
    "last_partial": "",
    "last_command": "",
    "last_event_at": 0.0,
}


def _tts_enabled() -> bool:
    # Por defecto OFF en Electron API: evitar locuciones largas y popups molestos de TTS.
    return os.getenv("NOX_API_TTS_ENABLED", "false").strip().lower() in {"1", "true", "yes", "si", "on"}


def _should_skip_tts_line(line: str) -> bool:
    low = (line or "").strip().lower()
    if not low:
        return True

    technical_markers = [
        "herramientas usadas",
        "providers usados",
        "run id",
        "tool:",
        "args:",
        "stage:",
        "traceback",
        "open_app(",
        "play_game_smart(",
        "search_youtube(",
        "set_volume(",
        "set_brightness(",
        "[response]",
    ]
    return any(m in low for m in technical_markers)


def _message_for_tts(message: str) -> str:
    lines = [ln.strip() for ln in (message or "").splitlines()]
    clean_lines = [ln for ln in lines if not _should_skip_tts_line(ln)]
    if not clean_lines:
        return "Listo."
    spoken = " ".join(clean_lines)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    if len(spoken) > 180:
        spoken = spoken[:177].rstrip() + "..."
    return spoken


async def broadcast_event(event_type: str, data: dict[str, Any]) -> None:
    """Envía evento a todos los clientes WebSocket conectados."""
    event = {"type": event_type, "data": data}
    for client in list(service_state["connected_clients"]):
        try:
            await client.send_json(event)
        except Exception:
            service_state["connected_clients"].discard(client)


@app.post("/api/command")
async def execute_command(req: CommandRequest) -> AgentResponse:
    """Ejecuta un comando a través del agente autónomo."""
    try:
        append_step_log({"stage": "api_command", "command": req.command})

        def on_confirm(tool: str, action: str, policy: dict) -> bool:
            risk = str(policy.get("risk", "low")).lower()
            return req.auto_confirm or risk == "low"

        result = run_agent(req.command, on_confirm=on_confirm)

        append_step_log(
            {
                "stage": "api_response",
                "command": req.command,
                "message": result.message,
                "tools_used": result.tools_used,
                "run_id": result.run_id,
            }
        )

        # Broadcast a clientes conectados
        await broadcast_event("command_result", {
            "message": result.message,
            "tools_used": result.tools_used,
            "run_id": result.run_id,
        })

        return AgentResponse(
            message=result.message,
            tools_used=result.tools_used,
            providers_used=result.providers_used,
            run_id=result.run_id,
        )
    except Exception as e:
        error_msg = str(e)
        append_step_log({"stage": "api_error", "error": error_msg})
        await broadcast_event("error", {"message": error_msg})
        raise


@app.get("/api/status")
async def get_status() -> dict[str, Any]:
    """Retorna estado del servicio."""
    vstatus = voice_status()
    return {
        "running": service_state["running"],
        "listening": service_state["listening"],
        "log_file": str(get_log_path()),
        "connected_clients": len(service_state["connected_clients"]),
        "last_wake": service_state.get("last_wake", ""),
        "last_partial": service_state.get("last_partial", ""),
        "last_command": service_state.get("last_command", ""),
        "last_event_at": service_state.get("last_event_at", ""),
        "voice_device": vstatus.get("voice_device"),
        "voice_sample_rate": vstatus.get("voice_sample_rate"),
        "voice_last_error": vstatus.get("last_error"),
        "tts_enabled": _tts_enabled(),
    }


@app.post("/api/speak")
async def speak(req: CommandRequest) -> dict[str, str]:
    """Ejecuta síntesis de voz."""
    try:
        result = speak_text(req.command)
        append_step_log({"stage": "api_speak", "text": req.command, "result": result})
        await broadcast_event("speak_done", {"text": req.command})
        return {"status": "ok", "result": result}
    except Exception as e:
        error_msg = str(e)
        append_step_log({"stage": "api_speak_error", "error": error_msg})
        await broadcast_event("error", {"message": error_msg})
        raise


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket para streaming de eventos en tiempo real."""
    await websocket.accept()
    service_state["connected_clients"].add(websocket)
    
    try:
        await broadcast_event("client_connected", {"clients": len(service_state["connected_clients"])})
        
        while True:
            # Mantener conexión viva
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        service_state["connected_clients"].discard(websocket)
        await broadcast_event("client_disconnected", {"clients": len(service_state["connected_clients"])})
    except Exception:
        service_state["connected_clients"].discard(websocket)


@app.post("/api/voice/start")
async def start_voice() -> dict[str, Any]:
    """Inicia escucha de voz en background."""
    if service_state["running"]:
        return {"status": "already_running"}

    service_state["running"] = True
    service_state["listening"] = False
    service_state["last_wake"] = ""
    service_state["last_partial"] = ""
    service_state["last_command"] = ""
    service_state["last_event_at"] = 0.0

    async def voice_task():
        loop = asyncio.get_running_loop()

        def emit_from_callback(event_type: str, payload: dict[str, Any]) -> None:
            """Permite emitir eventos async desde callbacks no-async/threaded."""
            def _schedule_emit() -> None:
                asyncio.create_task(broadcast_event(event_type, payload))

            loop.call_soon_threadsafe(_schedule_emit)

        def schedule_command(cmd: str) -> None:
            """Agenda el procesamiento async del comando desde hilo de voz."""
            def _schedule_cmd() -> None:
                asyncio.create_task(_on_command(cmd))

            loop.call_soon_threadsafe(_schedule_cmd)

        def _on_wake(raw: str) -> None:
            service_state["last_wake"] = raw
            service_state["listening"] = True
            service_state["last_event_at"] = time.time()
            emit_from_callback("voice_wake", {"text": raw})
            append_step_log({"stage": "voice_wake", "text": raw})

        def _on_partial(text: str) -> None:
            service_state["last_partial"] = text
            service_state["listening"] = True
            service_state["last_event_at"] = time.time()
            emit_from_callback("voice_partial", {"text": text})

        async def _on_command(cmd: str) -> None:
            service_state["listening"] = False
            service_state["last_command"] = cmd
            service_state["last_event_at"] = time.time()
            append_step_log({"stage": "voice_command", "command": cmd})
            await broadcast_event("voice_command", {"command": cmd})

            result = run_agent(cmd, on_confirm=lambda t, a, p: str(p.get("risk", "low")).lower() == "low")
            await broadcast_event("voice_result", {
                "message": result.message,
                "tools_used": result.tools_used,
                "run_id": result.run_id,
            })

            # En modo Electron API no hablar por defecto: solo mostrar en UI/logs.
            if _tts_enabled():
                speak_text(_message_for_tts(result.message))
            service_state["listening"] = True
            service_state["last_event_at"] = time.time()
            await broadcast_event("listening", {})

        info = start_voice_control(
            on_command=schedule_command,
            on_wake=_on_wake,
            on_partial=_on_partial,
        )

        if info.get("started"):
            service_state["listening"] = True
            await broadcast_event("listening", {"wake_word": info.get("wake_word", "nox")})
            append_step_log({"stage": "voice_started", "wake_word": info.get("wake_word")})

            try:
                while service_state["running"]:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                stop_voice_control()
                service_state["running"] = False
                service_state["listening"] = False
                append_step_log({"stage": "voice_stopped"})
                await broadcast_event("stopped", {})
        else:
            service_state["running"] = False
            await broadcast_event("error", {"message": info.get("message", "Could not start voice")})

    # Ejecutar en background
    asyncio.create_task(voice_task())

    return {"status": "starting"}


@app.post("/api/voice/stop")
async def stop_voice() -> dict[str, str]:
    """Detiene escucha de voz."""
    service_state["running"] = False
    return {"status": "stopping"}


@app.get("/api/logs")
async def get_logs(limit: int = 100) -> dict[str, Any]:
    """Lee últimas líneas del log."""
    try:
        log_path = get_log_path()
        if not Path(log_path).exists():
            return {"logs": [], "total": 0}

        with open(log_path) as f:
            lines = f.readlines()[-limit:]
            logs = [json.loads(line) for line in lines if line.strip()]
        return {"logs": logs, "total": len(logs)}
    except Exception as e:
        return {"logs": [], "error": str(e), "total": 0}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("NOX_API_PORT", 5000))
    uvicorn.run(app, host="127.0.0.1", port=port)
