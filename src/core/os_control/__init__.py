"""Control del sistema operativo.

Proporciona una interfaz `OSController` y una implementación basada en
`subprocess`/`os` (`SubprocessOSController`). La implementación respeta
un modo `dry_run` para evitar efectos durante tests/local.

Buenas prácticas:
- Implementación pequeña y segura (no ejecutar comandos sin validación).
- `dry_run` por defecto cuando se activa `MOCK_ENGINE=1`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import subprocess
import os
import sys
from typing import Any, Dict, List, Optional, Union


class OSController(ABC):
    @abstractmethod
    def run_command(self, cmd: Union[str, List[str]], *, shell: bool = False, capture_output: bool = False, check: bool = False, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Ejecuta un comando y devuelve un dict con el resultado."""

    @abstractmethod
    def start_app(self, app_name: str) -> Dict[str, Any]:
        """Inicia una aplicación o ejecutable por nombre."""

    @abstractmethod
    def open_path(self, path: str) -> Dict[str, Any]:
        """Abre fichero/URL con la aplicación por defecto."""

    @abstractmethod
    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Intenta terminar un proceso por pid."""


class SubprocessOSController(OSController):
    def __init__(self, dry_run: bool = False):
        self.dry_run = bool(dry_run)

    def run_command(self, cmd: Union[str, List[str]], *, shell: bool = False, capture_output: bool = False, check: bool = False, timeout: Optional[int] = None) -> Dict[str, Any]:
        if self.dry_run:
            return {"ok": True, "dry_run": True, "cmd": cmd}
        try:
            # Normalizar a subprocess.run
            if isinstance(cmd, list) and not shell:
                proc = subprocess.run(cmd, capture_output=capture_output, check=check, timeout=timeout, text=True)
            else:
                proc = subprocess.run(cmd, shell=True, capture_output=capture_output, check=check, timeout=timeout, text=True)
            return {"ok": True, "returncode": proc.returncode, "stdout": proc.stdout if capture_output else None, "stderr": proc.stderr if capture_output else None}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "returncode": e.returncode, "stderr": getattr(e, "stderr", str(e))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def start_app(self, app_name: str) -> Dict[str, Any]:
        if self.dry_run:
            return {"ok": True, "dry_run": True, "action": "start_app", "app": app_name}
        try:
            if os.name == "nt":
                # Intentar abrir con startfile (archivos/URLs), si falla hacer un shell start
                try:
                    os.startfile(app_name)
                    return {"ok": True, "method": "os.startfile"}
                except Exception:
                    cmd = f'start "" "{app_name}"'
                    return self.run_command(cmd, shell=True)
            else:
                # Linux/macOS: intentar ejecutar por nombre o abrir con xdg-open/open
                return self.run_command(app_name, shell=True)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_path(self, path: str) -> Dict[str, Any]:
        if self.dry_run:
            return {"ok": True, "dry_run": True, "action": "open_path", "path": path}
        try:
            if os.name == "nt":
                os.startfile(path)
                return {"ok": True}
            if sys.platform == "darwin":
                return self.run_command(["open", path])
            return self.run_command(["xdg-open", path])
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def kill_process(self, pid: int) -> Dict[str, Any]:
        if self.dry_run:
            return {"ok": True, "dry_run": True, "action": "kill_process", "pid": pid}
        try:
            if os.name == "nt":
                return self.run_command(["taskkill", "/PID", str(pid), "/F"]) 
            else:
                os.kill(pid, 9)
                return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Utilidades adicionales que pueden ser útiles en el futuro.
    def list_processes(self, capture_output: bool = True) -> Dict[str, Any]:
        if self.dry_run:
            return {"ok": True, "dry_run": True, "action": "list_processes"}
        try:
            if os.name == "nt":
                return self.run_command(["tasklist"], capture_output=capture_output)
            else:
                return self.run_command(["ps", "-ef"], capture_output=capture_output)
        except Exception as e:
            return {"ok": False, "error": str(e)}
