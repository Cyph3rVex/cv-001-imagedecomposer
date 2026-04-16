# CV-001: Image Decomposer & Professional Layer Editor

Herramienta de élite impulsada por IA para segmentar, extraer y editar componentes de una imagen (texto, logotipos, objetos) de manera automatizada. Utiliza técnicas avanzadas de inpainting para reconstruir el fondo dinámicamente y un motor de renderizado web para una edición no destructiva.

## Alcance
Extrae y convierte imágenes planas en lienzos interactivos con capas jerárquicas (1 a N).

## Requisitos Previos
- Python 3.10+
- Tesseract-OCR (Instalado a nivel de sistema operativo para soporte de texto)
- Dependencias listadas en `requirements.txt`

## Instalación

1. **Clonar repositorio**
   ```bash
   git clone https://github.com/cyph3rv3x/cv-001-imagedecomposer.git
   cd cv-001-imagedecomposer
   ```
2. **Entorno Virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Iniciar el servidor backend:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. Abre tu navegador en `http://localhost:8000`.
3. Sube una imagen. La IA extraerá los objetos y textos, y generará un fondo limpio.

## Contribución
Consulta `CONTRIBUTING.md`. Reporta issues detallados. No se aceptan PRs sin pruebas unitarias.

## Licencia
MIT License. Ver `LICENSE`.
