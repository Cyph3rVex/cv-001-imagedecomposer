import cv2
import numpy as np
import base64
import pytesseract

def process_image(image_bytes: bytes, roi: dict = None) -> dict:
    """
    Núcleo del procesador: Segmenta la imagen, extrae texto y regenera el fondo.
    Soporta ROI (Region of Interest) para descomposición parcial.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file.")

    # Si hay ROI, recortamos la imagen antes de procesar
    if roi:
        x, y, w, h = int(roi['x']), int(roi['y']), int(roi['w']), int(roi['h'])
        img = img[y:y+h, x:x+w]
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Segmentación de Objetos
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    objects = []
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    for c in contours:
        if cv2.contourArea(c) > 300:
            x, y, w, h = cv2.boundingRect(c)
            roi_obj = img[y:y+h, x:x+w]
            _, buffer = cv2.imencode('.png', roi_obj)
            objects.append({
                "x": int(x), "y": int(y),
                "width": int(w), "height": int(h),
                "img": base64.b64encode(buffer).decode('utf-8')
            })
            cv2.drawContours(mask, [c], -1, 255, -1)

    # 2. Extracción de Texto (OCR + Color Detection)
    texts = []
    try:
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i in range(len(d['text'])):
            if int(d['conf'][i]) > 60 and d['text'][i].strip():
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                
                # Muestrear el color central del texto
                sample_y, sample_x = y + h//2, x + w//2
                if 0 <= sample_y < img.shape[0] and 0 <= sample_x < img.shape[1]:
                    b, g, r = img[sample_y, sample_x]
                    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                else:
                    hex_color = "#000000"

                texts.append({
                    "text": d['text'][i], 
                    "x": int(x), "y": int(y),
                    "size": int(h),
                    "font": "Arial", 
                    "color": hex_color
                })
                cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    except Exception:
        pass

    # 3. Inpainting
    inpainted = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    _, bg_buffer = cv2.imencode('.png', inpainted)
    base_bg = base64.b64encode(bg_buffer).decode('utf-8')

    return {
        "base_background": base_bg,
        "objects": objects,
        "texts": texts
    }
