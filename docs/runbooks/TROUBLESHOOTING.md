# Troubleshooting NOX CLI y Asistente de Voz

Esta guía cubre problemas frecuentes y soluciones para el CLI y el entorno de desarrollo/producción.

## Problemas comunes y soluciones

### 1. El banner no se muestra en color
- Asegúrate de tener instalada la librería `colorama`.
- Si usas Windows, ejecuta la terminal en modo CMD o PowerShell, no en terminales antiguas.
- En VS Code, verifica que la terminal soporte colores ANSI.

### 2. Ctrl+C no cierra el CLI correctamente
- Desde la versión 0.4.0, Ctrl+C termina el proceso de forma segura en cualquier terminal.
- Si necesitas forzar la salida, puedes escribir `exit`, `quit` o `salir`.

### 3. Error: Windows no encuentra el archivo "\\"
- Ocurre si la ruta de trabajo está vacía o mal formada.
- Solución: ejecuta el CLI desde la carpeta raíz del proyecto (`custom-voice-assistant`).

### 4. El CLI abre una ventana nueva pero no ejecuta nada
- Verifica que la variable de entorno `cwd` apunte a la carpeta correcta.
- Si usas Docker, asegúrate de mapear correctamente los volúmenes y rutas.

### 5. Problemas con PowerShell en la terminal integrada de VS Code
- Se recomienda usar CMD o PowerShell en ventana externa para evitar bloqueos.
- Si la terminal queda inutilizable, cierra y vuelve a abrir la terminal integrada.

### 6. Tests no pasan o hay errores de importación
- Ejecuta siempre desde la carpeta `custom-voice-assistant`.
- Si usas Docker, revisa los comandos de build y test en el README.

### 7. Problemas con dependencias
- Ejecuta `pip install -r requirements.txt` en tu entorno virtual.
- Si falta `colorama`, instálalo manualmente: `pip install colorama`.

### 8. El CLI no responde o se traba
- Prueba en una terminal externa (CMD o PowerShell).
- Verifica que no haya procesos zombie de Python ejecutándose.

---

## Más ayuda
- Consulta los archivos README.md y la documentación en `/docs`.
- Si el problema persiste, abre un issue en el repositorio o contacta al responsable del proyecto.
