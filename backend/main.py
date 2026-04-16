from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from backend.processor import process_image
import os

app = FastAPI(title="Cypher Vex Image Decomposer", version="1.0.0")

import json
from fastapi import FastAPI, UploadFile, File, Form

@app.post("/api/decompose")
async def decompose(file: UploadFile = File(...), roi: str = Form(None)):
    """
    Recibe una imagen y opcionalmente un ROI.
    """
    try:
        data = await file.read()
        roi_dict = json.loads(roi) if roi else None
        result = process_image(data, roi_dict)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Montaje de archivos estáticos para el frontend web.
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
