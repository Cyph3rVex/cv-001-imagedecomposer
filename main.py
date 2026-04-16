from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import router
import os

app = FastAPI(title="Cypher Vex // Image Surgeon", version="1.1.0")

# Montar las rutas API
app.include_router(router, prefix="/api")

# Montar frontend estático
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
