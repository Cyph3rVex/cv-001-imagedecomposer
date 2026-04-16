import json
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from core.processor import process_image

router = APIRouter()

@router.post("/decompose")
async def decompose(file: UploadFile = File(...), roi: str = Form(None)):
    """
    Descompone una imagen segmentando texto, logos y reconstruyendo el fondo.
    """
    try:
        data = await file.read()
        roi_dict = json.loads(roi) if roi else None
        result = process_image(data, roi_dict)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
