# SPA Feature Flags

Esta carpeta contendrá una Single Page Application (SPA) para visualizar y editar los feature flags de NOX de forma gráfica.

- El backend lee y persiste los flags en `src/config/feature_flags.yaml`.
- Los cambios hechos desde la SPA o el CLI se reflejan en el mismo archivo YAML.
- La API REST expondrá endpoints `/feature_flags` (GET/POST) para consultar y modificar los flags desde la SPA.

## Stack sugerido
- Vite + React (o Vue/Svelte)
- fetch/axios para consumir la API REST

## Flujo
1. Levanta la API (`uvicorn src.api.main:app`)
2. Levanta la SPA (`npm run dev` o similar)
3. Accede a la SPA en `http://localhost:5173` (o el puerto que uses)
4. Cambia flags y observa el efecto en CLI/API/Desktop

## Persistencia
- Todos los cambios se guardan en `src/config/feature_flags.yaml`.
- El CLI y la API usan el mismo archivo, por lo que cualquier cambio es inmediato y global.
