import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cli.runner import _format_action_response, _handle_text
from src.core.orchestrator import NoxOrchestrator
from src.core.os_control import SubprocessOSController


@pytest.mark.parametrize(
    "input_text",
    [
        "Quiero reservar un vuelo a Madrid manana",
        "responde a la pregunta",
        "escribe un texto",
        "pon la alarma",
        "enciende la luz",
    ],
)
def test_cli_predict_intent(input_text):
    process = subprocess.Popen(
        [sys.executable, "-m", "src.cli", "--default", "--once"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "MOCK_ENGINE": "1"},
    )
    stdout, stderr = process.communicate(input=input_text + "\n", timeout=60)
    if process.returncode != 0:
        print(f"STDERR:\n{stderr}")
    assert process.returncode == 0
    assert stdout.strip()


def test_cli_verbose_shows_technical_details():
    process = subprocess.Popen(
        [sys.executable, "-m", "src.cli", "--default", "--once", "--verbose"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "MOCK_ENGINE": "1"},
    )
    stdout, stderr = process.communicate(input="que podes abrir\n", timeout=60)
    if process.returncode != 0:
        print(f"STDERR:\n{stderr}")
    assert process.returncode == 0
    assert "intent" in stdout.lower()
    assert "skill" in stdout.lower()


def test_runner_accepts_orchestrator_result_directly():
    orchestrator = NoxOrchestrator(os_controller=SubprocessOSController(dry_run=True))

    result, action = _handle_text(orchestrator, "abrir steam")

    assert result["intent"] == "open"
    assert action["skill"] == "os.open_known_target"
    assert action["success"] is True


def test_cli_formats_known_targets_as_human_sentence():
    action = {
        "success": True,
        "data": {
            "targets": [
                {"name": "steam"},
                {"name": "youtube"},
                {"name": "vscode"},
            ]
        },
    }

    assert _format_action_response(action) == "Puedo abrir: steam, youtube y vscode."
