from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.database import get_db_connection
from core.security import verify_password, create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (request.username,)).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o brecha detectada.")

    if not verify_password(request.password, user['hashed_password'], user['salt']):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta. Intento registrado.")

    # Generar Token JWT
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}
