import pytest
from src.core.external_api import ExternalAPIClient
import requests

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"Status {self.status_code}")


def test_fetch_data(monkeypatch):
    def mock_get(url, headers=None, params=None, auth=None):
        assert url == "https://api.ejemplo.com/datos"
        return DummyResponse({"ok": True, "data": [1,2,3]})
    monkeypatch.setattr(requests, "get", mock_get)
    client = ExternalAPIClient({
        "my_service": {"base_url": "https://api.ejemplo.com"}
    })
    resp = client.fetch_data("my_service", "/datos")
    assert resp["ok"] is True
    assert resp["data"] == [1,2,3]

def test_send_command(monkeypatch):
    def mock_post(url, headers=None, json=None, auth=None):
        assert url == "https://api.ejemplo.com/accion"
        assert json == {"cmd": "run"}
        return DummyResponse({"success": True})
    monkeypatch.setattr(requests, "post", mock_post)
    client = ExternalAPIClient({
        "my_service": {"base_url": "https://api.ejemplo.com"}
    })
    resp = client.send_command("my_service", "/accion", data={"cmd": "run"}, method="POST")
    assert resp["success"] is True
