import subprocess
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import pytest

@pytest.mark.parametrize("input_text", [
    "Quiero reservar un vuelo a Madrid mañana",
    "responde a la pregunta",
    "escribe un texto",
    "pon la alarma",
    "enciende la luz",
])
def test_cli_predict_intent(input_text):
    # Ejecuta el CLI como subprocess y pasa el texto por stdin
    process = subprocess.Popen(
        [sys.executable, "-m", "src.cli", "--default", "--once"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "MOCK_ENGINE": "1"}
    )
    stdout, stderr = process.communicate(input=input_text + "\n", timeout=60)
    if process.returncode != 0:
        print(f"STDERR:\n{stderr}")
    assert process.returncode == 0
    assert "intent" in stdout.lower() or "intención" in stdout.lower()
    assert input_text.split()[0] in stdout
