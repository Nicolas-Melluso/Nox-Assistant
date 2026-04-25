# Contrato de skills

Una skill es una unidad pequena, testeable y registrable por `SkillRegistry`.

Cada skill debe declarar:

- `name`: identificador estable, por ejemplo `os.open_known_target`.
- `description`: descripcion humana breve.
- `permissions`: permisos que necesita para operar.
- `supported_intents`: intents que puede manejar.
- `healthcheck()`: devuelve `SkillHealth`.
- `run(intent_result, context=None)`: devuelve `SkillResult`.

## Reglas de diseno

- Una skill debe tener una responsabilidad clara.
- Las acciones riesgosas deben bloquearse con un mensaje accionable hasta tener politica explicita.
- El orquestador valida permisos antes de ejecutar una skill.
- Los resultados deben pasar por `SkillResult`, incluso cuando la accion se bloquea.
- El catalogo de destinos seguros vive en configuracion, no en el clasificador.

## Skills actuales

- `os.open_known_target`: abre URLs, protocolos o apps configuradas.
- `os.process_control.blocked`: rechaza cierre/control de procesos hasta que exista permiso explicito.
- `os.list_known_targets`: lista los destinos seguros configurados.
- `core.status`: informa version, skills registradas y permisos activos.
