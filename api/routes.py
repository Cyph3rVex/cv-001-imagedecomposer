import json
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from core.processor import process_image
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/decompose")
@limiter.limit("5/minute") # Límite anti-abuso: 5 peticiones por minuto por IP
async def decompose(request: Request, file: UploadFile = File(...), roi: str = Form(None)):
    """
    Motor de Decomposición Público Protegido.
    """
    # 1. Validación de Seguridad de Archivo (Anti-Exploit)
    valid_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in valid_types:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Solo imágenes reales.")

    try:
        data = await file.read()
        
        # 2. Protección de Tamaño
        if len(data) > 5 * 1024 * 1024: # Máximo 5MB para proteger RAM de Termux
            raise HTTPException(status_code=400, detail="Archivo demasiado grande.")

        roi_dict = json.loads(roi) if roi else None
        result = process_image(data, roi_dict)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Fallo interno en motor IA."})
