Technical debt: `src/core/__init__.py`

Resumen
- Archivo: `src/core/__init__.py`.
- Actual: contiene una línea que reexporta `CoreEngine` desde `.engine` y un comentario de tipo "scaffold v0".
- Propósito: facilitar importaciones (p.ej. `from src.core import CoreEngine`).

Observaciones
- El comentario actual es temporal (menciona "scaffold v0"); conviene un docstring atemporal y descriptivo.
- La re-exportación es útil para consumir la API del paquete con imports más cortos y claros.
- Uso de importaciones relativas vs absolutas: `.engine` es correcto dentro del paquete y evita problemas si el paquete se instala o se usa como dependencia. La forma actual (`from .engine import CoreEngine`) es preferible a `from src.core.engine import CoreEngine` dentro del paquete.
- No hay `__all__` declarado; puede ser conveniente para definir la API pública del paquete.
- No existen tests que validen que la exportación funciona como paquete (por ejemplo, import usando `python -m` o al instalar el paquete).

Riesgos/Limitaciones
- Si el paquete se usa ejecutando archivos sueltos desde rutas diferentes, los imports pueden fallar si `PYTHONPATH` no está correctamente configurado. Esto es una cuestión de cómo se ejecuta Python, no del archivo en sí.

Acciones recomendadas
1. Reemplazar el comentario temporal por un docstring atemporal explicando el propósito del paquete:
   - Ejemplo: "Core motor package for NOX — re-exports `CoreEngine` and helpers."
2. Declarar explícitamente la API pública con `__all__ = ["CoreEngine"]`.
3. Preferir import relativo dentro del paquete (`from .engine import CoreEngine`) — si no está así, corregirlo.
4. Añadir un test pequeño que importe `CoreEngine` desde `src.core` para verificar la re-exportación:
   ```python
   def test_core_import():
       from src.core import CoreEngine
       assert callable(CoreEngine)
   ```
5. Documentar en `docs/architecture` la responsabilidad de `src.core` y su API pública.
6. Mantener el archivo pequeño: no poner lógica aquí; solo re-exports y docstring.

Estado: pendiente — aplicar cambios cuando se priorice.
