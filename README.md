# NOX - Custom Voice Assistant

NOX es un asistente local offline para ejecutar skills seguras desde una CLI o API. Esta rama queda cerrada como **MVP/POC/DEMO v0.5.0**: el foco es un core unico, comandos demostrables, permisos basicos y auditoria local.

## Que hace hoy

- Entiende comandos basicos sin llamar a una IA externa.
- Abre destinos seguros configurados en `src/config/apps.yaml`.
- Bloquea acciones riesgosas como cerrar procesos.
- Lista que puede abrir.
- Reporta estado/version del core.
- Expone CLI y API sobre el mismo orquestador.
- Registra auditoria local en `logs/audit.jsonl`.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Demo CLI

Modo interactivo:

```powershell
python -m src.cli --default
```

Modo de una sola frase:

```powershell
"que podes abrir" | python -m src.cli --default --once
"abrir youtube" | python -m src.cli --default --once
"abrir steam" | python -m src.cli --default --once
"abrir calculadora" | python -m src.cli --default --once
"cerrar steam" | python -m src.cli --default --once
"como estas" | python -m src.cli --default --once
```

Salida tecnica:

```powershell
"que podes abrir" | python -m src.cli --default --once --verbose
```

## Configurar destinos

Edita `src/config/apps.yaml`. Cada destino puede usar:

- `url`: URL web o protocolo del sistema, por ejemplo `steam://open/main`.
- `path`: nombre/ruta local, por ejemplo `calc`.
- `keywords`: frases que identifican el destino.

## API

```powershell
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Ejemplo:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/predict_intent `
  -ContentType "application/json" `
  -Body '{"text":"que podes abrir"}'
```

## Tests

```powershell
pytest -q
```

## Arquitectura

```text
CLI/API -> CoreEngine compatibility -> NoxOrchestrator -> IntentResult -> SkillRegistry -> SkillResult
```

Skills por defecto:

- `os.open_known_target`
- `os.process_control.blocked`
- `os.list_known_targets`
- `core.status`

## Documentacion

- Arquitectura: `docs/architecture/README.md`
- Contrato de skills: `docs/architecture/skills.md`
- TODO versionado: `docs/TODO.md`
- Runbooks: `docs/runbooks/`
- Changelog: `CHANGELOG.md`
