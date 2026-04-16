# 👁️ ImageDecomposer: The Surgeon (CV-002)

[![Security: Verified by Vex](https://img.shields.io/badge/Security-Verified%20by%20Vex-red.svg)](https://github.com/Cyph3rVex/cv-001-imagedecomposer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**ImageDecomposer** es una suite avanzada de Visión por Computadora diseñada por **Cypher Vex**. Analiza imágenes en bruto, extrae sus componentes (logotipos, patrones, tipografías) y convierte el resultado en un lienzo dinámico en capas, reconstruyendo el fondo dañado mediante redes de **Inpainting**.

## 🚀 Características Principales

*   **Inpainting Autónomo (Telea):** Regeneración matemática de los huecos dejados en el lienzo tras la extracción.
*   **Extracción Textual Precisa:** OCR con detección de Bounding Boxes y clonación de color dinámico.
*   **Selección Quirúrgica (ROI):** Define coordenadas de recorte elástico para enfocar la segmentación.
*   **Z-Index Hierarchy Layering:** Motor de renderizado web de grado profesional.

## 🛠️ Instalación

El sistema requiere dependencias criptográficas y de visión avanzadas. Usa el entorno virtual para mantener la higiene de tu terminal.

### En Termux / Android (Modo Supervivencia)
Debido a las estrictas restricciones de compilación de C++ en ARM64, el código ha sido optimizado para evitar la compilación desde cero. Ejecuta este arsenal nativo:

```bash
# 1. Instalar dependencias binarias del sistema Termux
pkg update -y
pkg install -y x11-repo science-repo python-pillow tesseract

# 2. Clonar y aislar el entorno
git clone https://github.com/Cyph3rVex/cv-001-imagedecomposer.git
cd cv-001-imagedecomposer

# 3. Crear entorno virtual heredando los paquetes del sistema (Crucial para Pillow)
python -m venv --system-site-packages venv
source venv/bin/activate

# 4. Instalar dependencias ligeras
pip install fastapi uvicorn python-multipart pytesseract requests
```

## 🔑 Configuración

Si utilizas redes restringidas, el sistema está preparado. Inicializa el servidor central.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Abre tu navegador apuntando a `http://localhost:8000`.

## 🔍 Estructura del Core (Clean Architecture)

El código ha sido reescrito bajo estándares de élite:
*   `api/` - Enrutadores RESTful y validación de esquemas (Pydantic).
*   `core/` - Motor de Inpainting y Segmentación (Visión Artificial).
*   `models/` - Estructuras de datos para objetos y capas.
*   `static/` - Interfaz balística reactiva (Fabric.js + Tailwind).

---

*“No cometo errores. Los elimino.”* — **Cypher Vex**
