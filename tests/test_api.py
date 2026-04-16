import pytest
from fastapi.testclient import TestClient
from main import app
import numpy as np
import cv2
import io

client = TestClient(app)

def create_dummy_image():
    # Imagen negra con un cuadrado blanco simular objeto
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
    _, buffer = cv2.imencode('.png', img)
    return io.BytesIO(buffer)

def test_decompose_endpoint_success():
    dummy_file = create_dummy_image()
    response = client.post(
        "/api/decompose", 
        files={"file": ("test.png", dummy_file, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validar estructura de respuesta
    assert "base_background" in data
    assert "objects" in data
    assert "texts" in data

def test_decompose_endpoint_invalid_file():
    # Enviar archivo no-imagen
    response = client.post(
        "/api/decompose", 
        files={"file": ("test.txt", io.BytesIO(b"fake data"), "text/plain")}
    )
    
    assert response.status_code == 500
    assert "error" in response.json()
