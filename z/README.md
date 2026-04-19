# Scripts automáticos (carpeta z)

Esta carpeta contiene scripts utilitarios para automatizar tareas del proyecto. Aquí se documenta cada script para que puedas copiar y pegar el comando fácilmente.

## t.py

Despachador para ejecutar scripts de `training/runs/scripts` usando un alias simple.

**Uso:**

```bash
python z/t.py --NOMBRE_DEL_SCRIPT.py
```

Por ejemplo, para ejecutar el script `run_intent_dataset_initial.py`:

```bash
python z/t.py --run_intent_dataset_initial.py
```

El script buscará el archivo en `training/runs/scripts` y lo ejecutará. Si el nombre no existe, mostrará un error.

---

Agrega aquí la documentación de nuevos scripts a medida que los vayas creando.
