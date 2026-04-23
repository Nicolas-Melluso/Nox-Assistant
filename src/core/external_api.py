"""
ExternalAPIClient: Cliente genérico para integración con APIs externas (REST, IoT, etc).

Permite realizar requests GET/POST configurables, soporta headers, autenticación y endpoints dinámicos.
Ejemplo de uso:
    client = ExternalAPIClient({
        "my_service": {
            "base_url": "https://api.ejemplo.com",
            "headers": {"Authorization": "Bearer ..."}
        }
    })
    resp = client.fetch_data("my_service", "/datos", params={"q": "valor"})
"""
import requests
from typing import Dict, Any, Optional

class ExternalAPIClient:
    def __init__(self, services_config: Optional[Dict[str, Any]] = None):
        """
        services_config: dict con configuración de servicios externos.
        Ejemplo:
        {
            "my_service": {
                "base_url": "https://api.ejemplo.com",
                "headers": {"Authorization": "Bearer ..."},
                "auth": None
            }
        }
        """
        self.services = services_config or {}

    def fetch_data(self, service: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Realiza un GET a un endpoint externo."""
        cfg = self.services.get(service)
        if not cfg:
            raise ValueError(f"Servicio externo '{service}' no configurado")
        url = cfg["base_url"].rstrip("/") + "/" + endpoint.lstrip("/")
        resp = requests.get(url, headers=cfg.get("headers"), params=params, auth=cfg.get("auth"))
        resp.raise_for_status()
        return resp.json()

    def send_command(self, service: str, endpoint: str, data: Optional[Dict[str, Any]] = None, method: str = "POST") -> Any:
        """Realiza un POST/PUT/PATCH a un endpoint externo."""
        cfg = self.services.get(service)
        if not cfg:
            raise ValueError(f"Servicio externo '{service}' no configurado")
        url = cfg["base_url"].rstrip("/") + "/" + endpoint.lstrip("/")
        method = method.upper()
        req_func = getattr(requests, method.lower(), None)
        if not req_func:
            raise ValueError(f"Método HTTP no soportado: {method}")
        resp = req_func(url, headers=cfg.get("headers"), json=data, auth=cfg.get("auth"))
        resp.raise_for_status()
        return resp.json()
