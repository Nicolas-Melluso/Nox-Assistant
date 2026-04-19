Technical debt: `src/cli/console.py`

Notas y acciones recomendadas:

- El import absoluto `from src.core.engine import CoreEngine` funciona cuando ejecutás desde la raíz del repo y `src` está en el `PYTHONPATH` (por ejemplo `python -m src.cli`). Si ejecutás `python src/cli/console.py` directamente puede fallar por el path.
- `run_console()` no tiene tipado ni `logging`; todo va a `stdout`/`stderr`.
- No hay control fino de signals ni `timeout` para `input()` (pero está bien para CLI simple).
- No hay sanitización/normalización del texto antes de enviarlo al motor (podés añadir `lowercase`/`strip`/normalización).
- Cambiar el docstring por uno atemporal.
- Aceptar un `engine` como argumento (inyección) para facilitar tests y reutilización:
  ```python
  def run_console(engine: Optional[CoreEngine] = None):
      ...
  ```
- Reemplazar `print` por `logging` o al menos permitir un `verbose` flag.
- Añadir manejo de errores alrededor de `engine.predict_intent` (try/except) para no romper el loop.
- Normalizar input antes de predecir: `text = text.strip()` y validar longitud.
- Añadir un prompt más informativo o `help` (`help`/`?` command).

Estado: pendiente de revisión y priorización. Marcar acciones concretas cuando se priorice.
