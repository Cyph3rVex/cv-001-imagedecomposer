from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as ai_router
from api.auth import router as auth_router
from core.database import init_db
import os

app = FastAPI(title="Cypher Vex // Enterprise Surgeon Vault", version="2.0.0")

# Inicializar Bóveda SQLite
init_db()

# Seguridad perimetral CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar las rutas
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(ai_router, prefix="/api", tags=["Motor IA"])

# Montar frontend estático
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import socket
    
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
        
    print("\n" + "="*50)
    print(f"🔒 BÓVEDA ENTERPRISE INICIADA")
    print(f"👤 Admin por defecto: Oliboli_12 / VexProtocol2026")
    print(f"📡 Acceso Seguro: http://{local_ip}:8000")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
