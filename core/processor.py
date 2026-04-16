from PIL import Image, ImageDraw, ImageFilter
import io
import base64
import pytesseract

MAX_DIMENSION = 1920  # Límite de seguridad 1080p para evitar OOM en Termux

def process_image(image_bytes: bytes, roi: dict = None) -> dict:
    """
    Versión Termux-Optimized (Pillow Engine) V2:
    Inpainting Avanzado y Protección contra desbordamiento de memoria.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # [EDGE CASE 1]: Protección contra Out-Of-Memory (OOM)
    # Si la imagen es masiva (ej. fotos de cámara raw), la redimensionamos preservando el ratio
    if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    
    if roi:
        # Se asume que el ROI viene escalado respecto a la imagen redimensionada del frontend
        img = img.crop((int(roi['x']), int(roi['y']), int(roi['x'] + roi['w']), int(roi['y'] + roi['h'])))

    texts = []
    bg = img.copy()

    try:
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i in range(len(d['text'])):
            if int(d['conf'][i]) > 60 and d['text'][i].strip():
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                
                # Muestreo de color
                color = img.getpixel((x + w//2, y + h//2))
                hex_color = "#{:02x}{:02x}{:02x}".format(*color)

                texts.append({
                    "text": d['text'][i], 
                    "x": x, "y": y,
                    "size": h,
                    "font": "Arial", 
                    "color": hex_color
                })
                
                # [EDGE CASE 2]: Inpainting Suavizado
                # Extraemos un recuadro un poco más grande alrededor del texto
                margin = 8
                box = (max(0, x - margin), max(0, y - margin), min(img.width, x + w + margin), min(img.height, y + h + margin))
                region = img.crop(box)
                
                # Aplicamos un desenfoque gaussiano agresivo a la región para difuminar los bordes
                # y simular la clonación del fondo contiguo sin cortes abruptos.
                blurred_region = region.filter(ImageFilter.GaussianBlur(radius=10))
                bg.paste(blurred_region, box)
    except Exception:
        pass

    def to_b64(pil_img):
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    return {
        "base_background": to_b64(bg),
        "objects": [], # Los objetos complejos requerirían OpenCV, desactivado en esta build segura.
        "texts": texts
    }
