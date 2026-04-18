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
BIG_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip"


def _target_model_dir(url: str = DEFAULT_MODEL_URL) -> Path:
    load_dotenv()
    env_path = os.getenv("NOX_VOSK_MODEL_PATH", "").strip()
    if env_path:
        return Path(env_path)
    # Inferir nombre de carpeta desde la URL del zip
    zip_name = url.rstrip("/").split("/")[-1].replace(".zip", "")
    return Path(__file__).resolve().parent.parent / "models" / zip_name


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
    parser.add_argument("--big", action="store_true", help="Descargar modelo grande (vosk-model-es-0.42, ~1.4 GB)")
    args = parser.parse_args()

    model_url = BIG_MODEL_URL if args.big else args.model_url
    target_dir = _target_model_dir(model_url)
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"Modelo ya presente en: {target_dir}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_file = tmp_path / "vosk_model.zip"
        _download(model_url, zip_file)
        _extract(zip_file, tmp_path)
        extracted = _find_extracted_model(tmp_path)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(extracted), str(target_dir))

    print(f"Modelo listo en: {target_dir}")
    print(f"\nActualiza tu .env con:")
    print(f"  NOX_VOSK_MODEL_PATH={target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
