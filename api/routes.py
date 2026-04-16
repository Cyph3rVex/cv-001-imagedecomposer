import json
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from core.processor import process_image
from core.security import verify_token

router = APIRouter()

@router.post("/decompose")
async def decompose(
    file: UploadFile = File(...), 
    roi: str = Form(None),
    current_user: str = Depends(verify_token) # GUARDIA DE SEGURIDAD JWT INYECTADO
):
    """
    Descompone una imagen. ACCESO RESTRINGIDO.
    """
    try:
        data = await file.read()
        roi_dict = json.loads(roi) if roi else None
        result = process_image(data, roi_dict)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
