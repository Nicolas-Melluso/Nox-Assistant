# NOX Desktop - Interfaz Gráfica con Electron

Aplicación desktop profesional para Nox con interfaz moderna, WebSocket en tiempo real y control de voz integrado.

## Arquitectura

```
NOX Desktop
├── Backend (Python)
│   ├── nox_api_server.py (FastAPI + WebSocket)
│   └── src/ (agent, skills, voice)
├── Frontend (Electron + React + Vite)
│   ├── electron/main.js (Proceso principal)
│   ├── src-electron/ (componentes React)
│   └── vite.config.js (compilador)
└── Comunicación: HTTP REST + WebSocket
```

## Instalación

### 1. Instalar dependencias de Node.js

```bash
cd custom-voice-assistant
npm install
```

### 2. Instalar dependencias de Python

```bash
source .venv312/Scripts/activate
pip install fastapi uvicorn python-multipart
```

## Desarrollo

### Terminal 1: Backend API

```bash
source .venv312/Scripts/activate
python scripts/nox_api_server.py
# API disponible en http://localhost:5000
```

### Terminal 2: Frontend (Vite dev server)

```bash
npm run dev
# Vite en http://localhost:5173
```

### Terminal 3: Electron (dev mode)

```bash
npm run electron-dev
# Inicia Electron + React devtools
```

## Compilación

### Build de producción

```bash
npm run build        # Compila React
npm run start        # Lanza Electron + API
```

### Crear instalador Windows

```bash
npm run dist         # Genera .exe y .msi en dist/
```

## Funcionalidades

### Control de Voz
- **Iniciar/Detener**: Botones en header
- **Wake Word**: Detecta "nox" y empieza a escuchar
- **Indicadores visuales**: Estado en tiempo real (escuchando, procesando, listo)

### Logs en Vivo
- Streaming vía WebSocket
- Colores por tipo (INFO, SUCCESS, WARNING, ERROR)
- Auto-scroll y limpieza manual
- Persistencia en `results/autonomous_agent_logs.jsonl`

### Comandos Manuales
- Envío de comandos por texto
- Auto-confirmación opcional
- Historial y respuestas en logs

### Integración API
- Endpoints: `/api/command`, `/api/speak`, `/api/voice/start`, `/api/status`
- WebSocket: `/ws` para eventos en tiempo real
- Manejo de errores con notificaciones

## Estructura de Directorios

```
custom-voice-assistant/
├── scripts/
│   ├── nox_api_server.py       # FastAPI backend
│   ├── nox_desktop_service.py  # (legacy) cmd-based service
│   └── autonomous_nox.py       # (legacy) CLI
├── electron/
│   ├── main.js                 # Proceso principal Electron
│   ├── preload.js              # Context bridge
│   └── package.json            # Deps de Electron
├── src-electron/
│   ├── App.jsx                 # Componente principal
│   ├── main.jsx                # Entry point React
│   ├── App.css                 # Estilos (vacío, usa index.css)
│   └── index.css               # Tema dark mode
├── index.html                  # HTML raíz
├── vite.config.js              # Config Vite
└── electron-builder.json       # Config empaquetador
```

## Variables de Entorno

```bash
# .env
NOX_API_PORT=5000          # Puerto del servidor FastAPI
NOX_PERSONA_MODE=1         # Modo Jarvis (sarcasmo)
NOX_ENABLE_JOKES=1         # Habilitar bromas
NOX_WAKE_WORD=nox          # Palabra de activación
NOX_TTS_RATE=150           # Velocidad de síntesis
NOX_TTS_VOLUME=0.8         # Volumen (0-1)
```

## Troubleshooting

### "No se puede conectar a API"
```bash
# Verificar que nox_api_server.py está corriendo
curl http://localhost:5000/api/status
```

### "WebSocket connection failed"
- Asegurar CORS habilitado en FastAPI ✓
- Revisar firewall/antivirus

### "Voz no detecta wake word"
- Verificar micrófono en Windows
- Revisar logs de Vosk en consola Python

### Build falla
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

## Next Steps

1. ✅ App Electron completa con UI moderna
2. 🔜 Persistencia de sesiones (historial de comandos)
3. 🔜 Themes oscuro/claro customizables
4. 🔜 Integración con Discord/Telegram notifications
5. 🔜 Auto-updater (ver versiones nuevas de Nox)

## Licencia

Same as parent project (custom-voice-assistant)
