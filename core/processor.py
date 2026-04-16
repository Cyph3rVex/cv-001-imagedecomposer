from PIL import Image, ImageDraw, ImageOps
import io
import base64
import pytesseract

def process_image(image_bytes: bytes, roi: dict = None) -> dict:
    """
    Versión Termux-Optimized (Pillow Engine): 
    Segmenta la imagen, extrae texto y genera fondo limpio.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    if roi:
        img = img.crop((int(roi['x']), int(roi['y']), int(roi['x'] + roi['w']), int(roi['y'] + roi['h'])))

    # 1. Extracción de Texto y Máscara
    texts = []
    mask_draw = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask_draw)

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
                # Añadir a la máscara de eliminación (un poco más grande para limpieza)
                draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill=255)
    except Exception:
        pass

    # 2. Segmentación de Objetos (Basada en contraste)
    # En esta versión simplificada, trataremos áreas no-texto como objetos si tienen contraste
    objects = []
    # (Lógica simplificada para Termux: por ahora el usuario puede añadir capas manualmente)
    
    # 3. Reconstrucción de Fondo (Inpainting simplificado vía Blur/Expand)
    # Rellenamos los huecos del texto con el color promedio circundante
    bg = img.copy()
    for t in texts:
        # Muestrear color justo afuera del texto para rellenar
        sample_pixel = bg.getpixel((max(0, t['x']-5), max(0, t['y']-5)))
        bg_draw = ImageDraw.Draw(bg)
        bg_draw.rectangle([t['x'], t['y'], t['x']+10, t['y']+t['size']], fill=sample_pixel) # Placeholder de relleno

    # Convertir a Base64
    def to_b64(pil_img):
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    return {
        "base_background": to_b64(bg),
        "objects": objects,
        "texts": texts
    }
