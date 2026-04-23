# Documentación técnica NOX

## Novedades CLI v0.4.0
- Banner completamente rojo y soporte de colores ANSI.
- Ctrl+C cierra el CLI de forma segura (no requiere doble Ctrl+C).
- Mejor manejo de rutas y errores en Windows.
- Troubleshooting centralizado en `docs/runbooks/TROUBLESHOOTING.md`.

## Instalación y uso rápido
```bash
python -m venv .venv
source .venv/Scripts/activate  # o equivalente
pip install -r requirements.txt
python -m src.cli
```

## Troubleshooting
Consulta la guía en `docs/runbooks/TROUBLESHOOTING.md` para problemas frecuentes.


## Resumen

NOX es un asistente de voz modular para Windows, con pipeline reproducible y extracción avanzada de entidades en español.

### Capacidades
- Clasificación de intenciones (scikit-learn)
- Extracción robusta de entidades (spaCy + patrones custom)
- Reconocimiento de variantes, sinónimos y errores comunes
- Soporte para negaciones, preguntas, fechas, horas y dispositivos
- Nuevos tipos de entidades: Google Maps, Control de Windows, Asus Rog, Código de programación
- Modularidad y fácil extensión

### Ejemplo de entidades avanzadas y cobertura

```
Frase: "Abrí Google Maps y generá un código Python para calcular la ruta"
Entidades: [
    {"label": "GOOGLE_MAPS", "text": "Google Maps"},
    {"label": "CODIGO_PROGRAMACION", "text": "código Python"},
    {"label": "COMANDO", "text": "abrí"},
    {"label": "COMANDO", "text": "generá"},
    {"label": "COMANDO", "text": "calcular"},
    {"label": "DISPOSITIVO", "text": "ruta"}
]
```

**Cobertura:**
Todos los tests unitarios cubren entidades avanzadas y patrones compuestos (multi-palabra) como "Google Maps", "panel de control", "modo turbo". La integración es robusta en local y Docker.

### Estructura
- `src/` - Código fuente principal
- `training/` - Datasets y scripts de entrenamiento
- `models/` - Modelos entrenados
- `results/` - Resultados y logs

### Ejemplo de uso

```python
from src.core.entity_extraction import extract_entities
frase = "Prendé la luz del baño y apaga el ventiladorcito"
print(extract_entities(frase))
```

### Ejemplos avanzados

- "Pon la alarma a las 7:30 y despiértame después"
- "Subí el volumen del televisor y baja la música"
- "¿Puedes abrir la puerta y encender la alarma?"
- "Apaga la heladera y la nevera"

### Troubleshooting
- Si spaCy no detecta entidades, instala el modelo `es_core_news_sm`.
- Si hay errores de importación, ejecuta los comandos desde la raíz del proyecto.
