
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.engine import CoreEngine

app = FastAPI(title="NOX API v0.0.1", description="API REST para integración externa del motor de NLU", version="0.1.0")

# Montar la SPA en /spa y /spa/{path:path}
spa_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spa-feature-flags'))
app.mount("/spa", StaticFiles(directory=spa_dir, html=True), name="spa")

# Redirigir /spa a index.html si no hay archivo
@app.get("/spa", include_in_schema=False)
def spa_index():
    return FileResponse(os.path.join(spa_dir, "index.html"))

# Permitir CORS para la SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"]
)

# Endpoint para feature flags (GET y POST)
from config.feature_flags import FeatureFlags

@app.get("/feature_flags")
def get_feature_flags():
    flags = FeatureFlags().list_flags()
    return JSONResponse(content=flags)

@app.post("/feature_flags")
def set_feature_flags(new_flags: dict):
    import yaml, os
    FLAGS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "feature_flags.yaml")
    with open(FLAGS_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_flags, f, allow_unicode=True)
    return {"ok": True}


# Ejemplo de configuración de servicios externos
EXTERNAL_SERVICES = {
    # "my_service": {
    #     "base_url": "https://api.ejemplo.com",
    #     "headers": {"Authorization": "Bearer ..."}
    # }
}
engine = CoreEngine(external_services=EXTERNAL_SERVICES)
class ExternalAPIRequest(BaseModel):
    service: str
    endpoint: str
    method: str = "GET"
    params: dict = None
    data: dict = None


# Endpoint para llamar APIs externas vía CoreEngine
@app.post("/external_api")
def external_api(request: ExternalAPIRequest):
    try:
        result = engine.call_external_api(
            service=request.service,
            endpoint=request.endpoint,
            params=request.params,
            method=request.method,
            data=request.data
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TextRequest(BaseModel):
    text: str

@app.post("/predict_intent")
def predict_intent(request: TextRequest):
    try:
        result = engine.predict_intent(request.text)
        return {
            "intent": result["intent"],
            "score": result["confidence"],
            "entities": result["entities"],
            "input_text": result["input_text"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_entities")
def extract_entities(request: TextRequest):
    try:
        entities = engine.extract_entities(request.text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
