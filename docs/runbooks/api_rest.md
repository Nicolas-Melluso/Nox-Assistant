# Runbook: API REST para integración externa

## Objetivo
Exponer el motor de NLU (CoreEngine) mediante una API REST para permitir integración con servicios externos.

## Endpoints iniciales
- POST `/predict_intent`: Recibe texto, devuelve intención y score.
- POST `/extract_entities`: Recibe texto, devuelve entidades detectadas.

## Framework
- FastAPI (Python)
- Uvicorn para desarrollo/despliegue

## Uso local
```bash
uvicorn src.api.main:app --reload
```

## Ejemplo de request
```json
{
  "text": "Quiero reservar un vuelo a Madrid mañana"
}
```

## Próximos pasos
- Añadir autenticación y CORS
- Pruebas unitarias y e2e
- Documentar endpoints y contrato

## Tareas futuras para evolución de la API REST

- Añadir autenticación y autorización (API Key, OAuth2, JWT).
- Implementar rate limiting para evitar abuso.
- Mejorar manejo de errores y mensajes de respuesta.
- Documentar y versionar la API (OpenAPI, changelog de endpoints).
- Agregar pruebas unitarias y e2e específicas para la API.
- Desacoplar la API como producto/servicio independiente (microservicio).
- Añadir soporte para webhooks y callbacks.
- Mejorar la experiencia de usuario (mensajes claros, ejemplos, docs interactivas).
- Soporte para CORS y control de orígenes permitidos.
- Monitoreo, logging y métricas de uso de la API.
- Implementar paginación y filtros en endpoints futuros.
- Soporte para batch requests y procesamiento asíncrono.
- Validación avanzada de payloads y schemas.
- Pruebas de carga y stress.
- Automatizar despliegue y CI/CD para la API.
