# TODO versionado

## v0.4.4 - Core usable y catalogo seguro

- [x] Limitar pytest a `tests/` para evitar scripts interactivos.
- [x] Usar clasificador determinista por defecto y dejar sentence-transformers como opt-in.
- [x] Agregar Steam como destino seguro.
- [x] Desacoplar comandos `abrir/cerrar` del catalogo hardcodeado del clasificador.
- [x] Ampliar catalogo inicial de destinos seguros.
- [x] Migrar CLI/API para consumir `NoxOrchestrator.handle()` como fuente principal.

## v0.4.5 - Permisos y auditoria

- [x] Definir politica de permisos para acciones del sistema.
- [x] Registrar intent, skill, target y resultado de cada accion ejecutada.
- [x] Bloquear acciones ambiguas con mensajes accionables.
- [x] Agregar tests de acciones bloqueadas y permitidas.

## v0.4.6 - Skills pequenas y testeables

- [x] Separar skill de abrir apps/sitios de futuras skills de cerrar procesos.
- [x] Agregar skills de utilidad local de bajo riesgo.
- [x] Documentar contrato para nuevas skills.

## v0.5.0 - Interfaces sobre el core unico

- [x] Mejorar salida humana de CLI para respuestas informativas.
- [x] Agregar skill `core.status` para diagnostico local seguro.
- [x] Reintegrar API REST sobre el orquestador.
- [x] Estabilizar salida de CLI para uso humano y scripts.
- [x] Mantener `CoreEngine` solo como compatibilidad temporal.
- [x] Agregar auditoria persistente JSONL local.
- [x] Documentar demo MVP/POC.

## Backlog posterior

- [ ] Voz.
- [ ] Memoria.
- [ ] UI desktop/web.
- [ ] Clasificador ML entrenable con fallback offline.
