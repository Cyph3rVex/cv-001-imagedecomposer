from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.routes import router as ai_router
import os

# Limiter para evitar abuso público (Nivel Enterprise)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Cypher Vex // Public Surgeon", version="3.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Seguridad perimetral CORS: Solo permitiremos dominios autorizados en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambiar a dominio real al subir a la web
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(ai_router, prefix="/api", tags=["Motor IA"])

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
