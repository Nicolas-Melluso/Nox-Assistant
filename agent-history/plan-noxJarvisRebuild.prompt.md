# Retrospectiva y Reconstrucción NOX -> Jarvis

## 1. Resumen ejecutivo
Hicimos un MVP potente para validar capacidades reales de tu PC y de la IA local/híbrida. El experimento cumplió su objetivo: demostrar que el asistente ya puede entender intenciones, ejecutar acciones en Windows, manejar voz básica y operar con interfaz desktop.
Ahora conviene reconstruir desde cero con una arquitectura limpia y unificada para evitar deuda técnica y escalar en serio hacia un Jarvis personal.

## 2. Qué hicimos bien
- Construimos base ML sólida de intenciones con muy buena precisión.
- Validamos integración real de acciones Windows (control del sistema, apps, flujos útiles).
- Agregamos seguridad temprana con políticas y confirmación por riesgo.
- Implementamos observabilidad base con logs estructurados.
- Probamos múltiples interfaces: CLI, servicio de voz y desktop.
- Introdujimos personalidad y tono del asistente.
- Detectamos rápido problemas reales de operación (wake, parcial, TTS, estado).
- Mantuvimos iteración rápida y validación práctica orientada a producto.

## 3. Qué hicimos mal
- Mezclamos demasiadas decisiones de arquitectura mientras construíamos features.
- Acoplamiento alto entre capas (voz, agente, API, UI) en algunos puntos.
- Fragmentación de interfaces sin un core único totalmente limpio.
- Flujo de voz inestable por callbacks/threading/async en varias iteraciones.
- Configuración dispersa y behavior flags no totalmente centralizados desde el día 1.
- Testing insuficiente de integración end-to-end para voz + UI + acciones.
- Se introdujeron cambios operativos sin un release flow claro.
- Falta de contrato estable entre motor y clientes (CLI/Desktop/Web).

## 4. Qué se puede mejorar (priorizado)
0. Entrenar con p99 y base 500 ejemplos por clase desde el día 1 para evitar sesgo de muestra y mejorar robustez con 100 corridas reales.
1. Unificar “motor central” y hacer que CLI/Desktop/Web sean clientes del mismo core.
2. Definir contratos claros: intent result, action result, voice events, error schema.
3. Separar voz en pipeline explícito: wake -> partial -> command -> execute -> respond.
4. Feature flags centralizados para activar/desactivar capacidades sin tocar código.
5. Política de seguridad por capability (filesystem, network, apps, system control).
6. Memoria por capas: sesión, usuario, aprendizaje validado.
7. Entrenamiento continuo con dataset versionado y evaluación por intent crítico.
8. Observabilidad real: métricas, health, tracing de cada comando.
9. Plan de releases: dev, staging local, release estable.
10. Suite de tests por niveles: unit, integration, e2e de voz y acciones.
11. Documentación de arquitectura, runbooks de operación y learning path para nuevos devs.

## 5. Puntajes actuales (1-100)
- Autonomía actual: 38/100
  Justificación: muy bien en intención + acciones locales, bajo en multi-paso robusto y aprendizaje continuo.
- Similitud con Jarvis real: 28/100
  Justificación: falta proactividad fuerte, planificación compleja, memoria robusta y ejecución web confiable.
- Estructura del repo para escalar: 62/100
  Justificación: ya hay modularidad útil, pero falta separación estricta de dominios y contratos entre capas.

## 6. Estructura objetivo del repositorio (reconstrucción prolija)
- src
  - src/core
  - src/agent
  - src/intent
  - src/skills
    - src/skills/flows
        - src/skills/flows/start_steam_with_specific_game_and_set_pc_in_performance_mode.py
        - src/skills/flows/open_default_browser_and_search_with_context.py
  - src/voice
    - src/voice/stt
    - src/voice/tts
    - src/voice/config
  - src/memory
  - src/personality
  - src/security
  - src/config
  - src/observability
  - src/api
  - src/cli
  - src/desktop-bridge
  - src/web-bridge
- training
  - datasets
    - datasets/raw
    - datasets/processed
  - runs
    - runs/100_examples_p99.py
    - runs/10_games_on_steam.py
- models
  - models/vosk
    - vosk/model-small-es-0.22
    - models/vosk/model-small-en-us-0.15
  - models/nox_v1.joblib
  - models/nox_v2.joblib
- tests
  - tests/unit
  - tests/integration
  - tests/e2e
- docs
  - docs/architecture
  - docs/runbooks
  - docs/learning-path
- scripts

Idea central: un solo motor, múltiples interfaces.

## 7. Cómo entrenar el modelo de intenciones de forma eficaz
- Dataset por intención con mínimo razonable por clase.
- Split estratificado reproducible con seed fija.
- Evaluación por clase, no solo accuracy global.
- Matriz de confusión como insumo principal de mejora.
- Ciclo de mejora por errores reales de producción.
- Re-entrenamiento por lote validado, no automático ciego.
- Versionado de modelos con metadata de entrenamiento.
- Gate de promoción: métricas mínimas + tests de regresión.
- Lista de intents críticos con umbrales más estrictos.
- Skills son flujos de acción, no parte del modelo de intención, es decir son habilidades especificas que se activan según la intención detectada, pero no forman parte del proceso de clasificación de intenciones en sí. Ejemplo: "abrir spotify" -> intención: "abrir_app", skill: "abrir_spotify_flow" que sabe cómo abrir spotify específicamente y poner una playlist segun el contexto.

## 8. Voz, respuesta y personalidad
- STT:
  - Wake detector robusto.
  - Reconocimiento parcial para feedback visual.
  - Reconocimiento final para comando.
- TTS:
  - Modo on/off por flag.
  - Filtro para no verbalizar texto técnico/logs.
  - Voz configurable por perfil.
- Personalidad:
  - Perfil configurable (formal, witty, etc).
  - Límite de estilo para no degradar claridad operativa.
  - Separar “contenido” de “estilo” para mantener control.

## 9. Configuración modular y feature flags
- Config en capas:
  - base config
  - env override
  - runtime override controlado
- Feature flags por capacidad:
  - voice_enabled
  - tts_enabled
  - web_actions_enabled
  - risky_actions_enabled
  - personality_mode
  - continuous_learning_enabled
- Capacidades por política:
  - allow/deny por skill
  - nivel de riesgo
  - confirmación requerida

## 10. Plan para alguien que arranca desde cero (agregar complejidad gradual)

0. Fase 0: Base de datasets y contratos
  - Dataset mínimo por intención con p99 desde el inicio.
  - Definir contratos claros: intent_result, skill_result, error_schema.
1. Fase 1: Motor central + CLI mínima
  - Intent classifier desacoplado.
  - CLI como cliente del core, sin lógica propia.
2. Fase 2: Router de skills
  - Skills como flujos independientes activados por intención.
  - Ejemplo: intención abrir_app → skill abrir_spotify_flow.
3. Fase 3: API única del motor
  - Core expuesto por API estable.
  - Contratos versionados y documentados.
4. Fase 4: Feature flags y políticas
  - Flags centralizados (voice_enabled, risky_actions_enabled).
  - Políticas de seguridad por skill/capability.
5. Fase 5: Voz modular
  - Pipeline explícito: wake → partial → command → execute → respond.
  - STT/TTS desacoplados con configuración independiente.
6. Fase 6: Personalidad y estilo
  - Configuración de perfiles (formal, witty, técnico).
  - Separación entre contenido y estilo.
7. Fase 7: Memoria por capas
  - Sesión → usuario → aprendizaje validado.
  - Persistencia modular y controlada.
8. Fase 8: Interfaces múltiples
  - Desktop/Web como clientes del mismo core.
  - Bridge modular (desktop-bridge, web-bridge).
9. Fase 9: Observabilidad y testing
  - Métricas, tracing, health checks.
  - Suite de tests: unit, integration, e2e (voz + acciones).
10. Fase 10: Entrenamiento continuo
  - Dataset versionado.
  - Ciclo de mejora con errores reales de producción.
  - Gate de promoción con métricas mínimas.
11. Fase 11: Hardening y releases
  - Plan de releases (dev → staging → estable).
  - Documentación de arquitectura y runbooks.
  - Learning path para nuevos devs.

## 11. Conclusión
Lo que hicimos estuvo muy bien para exploración de capacidades reales.
Para llegar a un Jarvis serio, el siguiente salto no es “más features”, sino “mejor arquitectura + contratos + operación estable”.
Si seguimos este plan, el crecimiento va a ser ordenado, medible y mucho más rápido.
