"""Descarga y prepara un modelo Vosk en espanol para NOX.

Uso:
  python scripts/setup_vosk_es.py
  python scripts/setup_vosk_es.py --model-url https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

from dotenv import load_dotenv

DEFAULT_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"


def _target_model_dir() -> Path:
    load_dotenv()
    env_path = os.getenv("NOX_VOSK_MODEL_PATH", "").strip()
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent.parent / "models" / "vosk-model-small-es-0.42"


def _download(url: str, out_file: Path) -> None:
    print(f"Descargando modelo desde: {url}")
    urlretrieve(url, out_file)


def _extract(zip_file: Path, out_dir: Path) -> None:
    print("Extrayendo modelo...")
    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.extractall(out_dir)


def _find_extracted_model(base_dir: Path) -> Path:
    candidates = [p for p in base_dir.iterdir() if p.is_dir() and p.name.startswith("vosk-model")]
    if not candidates:
        raise RuntimeError("No se encontro carpeta de modelo dentro del zip")
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup modelo Vosk ES para NOX")
    parser.add_argument("--model-url", default=DEFAULT_MODEL_URL, help="URL del zip del modelo")
    args = parser.parse_args()

    target_dir = _target_model_dir()
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"Modelo ya presente en: {target_dir}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_file = tmp_path / "vosk_model.zip"
        _download(args.model_url, zip_file)
        _extract(zip_file, tmp_path)
        extracted = _find_extracted_model(tmp_path)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(extracted), str(target_dir))

    print(f"Modelo listo en: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
