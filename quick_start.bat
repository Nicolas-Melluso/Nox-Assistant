@echo off
setlocal enabledelayedexpansion

echo ===================================
echo NOX Desktop - Quick Start
echo ===================================

REM Verificar si Node.js está instalado
node -v >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no está instalado
    echo Descarga desde: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está disponible
    echo Activa el venv: .venv312\Scripts\activate
    pause
    exit /b 1
)

REM Instalar dependencias si no existen
if not exist "node_modules" (
    echo Instalando dependencias npm...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install falló
        pause
        exit /b 1
    )
)

echo.
echo ✓ Verificaciones completadas
echo.
echo Para desarrollo, ejecuta en 3 terminales:
echo.
echo Terminal 1 - Backend API:
echo   source .venv312/Scripts/activate ^&^& python scripts/nox_api_server.py
echo.
echo Terminal 2 - Frontend (Vite):
echo   npm run dev
echo.
echo Terminal 3 - Electron:
echo   npm run electron-dev
echo.
echo Para producción:
echo   npm run start
echo.
pause
