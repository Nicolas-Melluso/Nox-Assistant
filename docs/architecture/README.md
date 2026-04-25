# Arquitectura NOX

## Core unico

El punto central nuevo es `NoxOrchestrator.handle(text, context=None)`.

```text
Input de usuario
  -> clasificador de intencion
  -> IntentResult
  -> SkillRegistry
  -> SkillResult
  -> respuesta de CLI/API/UI
```

`CoreEngine` queda como capa de compatibilidad para la API y tests existentes. La direccion de crecimiento es que CLI, API y futuras UI usen el mismo orquestador.

## Contratos

- `IntentResult`: `name`, `confidence`, `raw_text`, `entities`.
- `SkillResult`: `success`, `message`, `data`, `error`.
- `Skill`: `name`, `description`, `permissions`, `supported_intents`, `healthcheck()`, `run()`.

El registry valida estos contratos al registrar una skill.

Detalle del contrato de skills: `docs/architecture/skills.md`.

## Politica MVP

- La CLI es el primer producto usable.
- Abrir destinos conocidos es una accion permitida.
- Cerrar procesos o ejecutar comandos ambiguos queda bloqueado hasta tener permisos y auditoria.
- `sentence-transformers`, voz, memoria, desktop y web bridge quedan como capacidades futuras, no como camino critico.

## Roadmap aislado

Estas areas existen como direccion futura, pero no deben mezclarse con el core hasta que haya contratos y tests suficientes:

- `src/voice`
- `src/memory`
- `src/personality`
- `src/desktop-bridge`
- `src/web-bridge`
