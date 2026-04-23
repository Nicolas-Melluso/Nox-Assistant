# FastAPI app para exponer CoreEngine como API REST
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.engine import CoreEngine

app = FastAPI(title="NOX API v0.0.1", description="API REST para integración externa del motor de NLU", version="0.1.0")

engine = CoreEngine()

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
