import cv2
import numpy as np
import os
import random
from PIL import Image
from io import BytesIO

def add_snouts_to_faces(image_bytes, snouts_folder):
    """
    Принимает байты изображения, находит лица и накладывает пятачки.
    Размер пятачка рассчитывается динамически относительно размера найденного лица.
    """

    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        return None

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

    snout_files = [f for f in os.listdir(snouts_folder) if f.endswith('.png')]
    if not snout_files:
        raise FileNotFoundError("В папке snouts/ нет PNG изображений!")

    for (x, y, w, h) in faces:
        face_width = w
        face_height = h
        
        snout_name = random.choice(snout_files)
        snout_path = os.path.join(snouts_folder, snout_name)
        snout_img = Image.open(snout_path).convert("RGBA")

        scale_factor = 0.4 
        new_snout_width = int(face_width * scale_factor)
        
        aspect_ratio = snout_img.height / snout_img.width
        new_snout_height = int(new_snout_width * aspect_ratio)
        
        snout_resized = snout_img.resize((new_snout_width, new_snout_height), Image.Resampling.LANCZOS)

        pos_x = int(x + (face_width // 2) - (new_snout_width // 2))

        vertical_offset_factor = 0.55
        pos_y = int(y + (face_height * vertical_offset_factor) - (new_snout_height // 2))

        # Накладываем пятачок
        img_pil.paste(snout_resized, (pos_x, pos_y), snout_resized)

    # 5. Сохраняем результат
    bio = BytesIO()
    img_pil.save(bio, 'JPEG')
    bio.seek(0)
    
    return bio