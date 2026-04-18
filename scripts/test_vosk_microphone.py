"""Test de microfono con Vosk (adaptado del ejemplo oficial).

Uso:
  python scripts/test_vosk_microphone.py
  python scripts/test_vosk_microphone.py --list-devices
  python scripts/test_vosk_microphone.py --device 1
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys

import sounddevice as sd
from dotenv import load_dotenv
from vosk import KaldiRecognizer, Model, SetLogLevel

q: queue.Queue[bytes] = queue.Queue()


def int_or_str(text: str):
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):  # noqa: ANN001
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def _model_path() -> str:
    load_dotenv()
    return os.getenv("NOX_VOSK_MODEL_PATH", "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test microphone Vosk")
    parser.add_argument("--list-devices", action="store_true", help="Listar dispositivos y salir")
    parser.add_argument("--device", type=int_or_str, help="ID o nombre parcial de dispositivo")
    parser.add_argument("--samplerate", type=int, help="Sample rate")
    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return 0

    model_path = _model_path()
    if not model_path or not os.path.isdir(model_path):
        print("Modelo Vosk no encontrado. Ejecuta: python scripts/setup_vosk_es.py")
        return 1

    if args.samplerate is None:
        dev = sd.query_devices(args.device, "input")
        args.samplerate = int(dev["default_samplerate"])

    SetLogLevel(-1)
    model = Model(model_path)
    rec = KaldiRecognizer(model, args.samplerate)

    print("Escuchando... di 'Nox abre steam' y observa resultado.")
    print("Ctrl+C para salir.")

    with sd.RawInputStream(
        samplerate=args.samplerate,
        blocksize=8000,
        device=args.device,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = (result.get("text") or "").strip()
                if text:
                    print(f"[final] {text}")
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                if partial:
                    print(f"[partial] {partial}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nSaliendo...")
        raise SystemExit(0)
