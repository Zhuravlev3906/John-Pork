import cv2
import numpy as np
import os
import random
from PIL import Image
from io import BytesIO

def add_snouts_to_faces(image_bytes, snouts_folder):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        return None

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Если лиц нет, возвращаем None
    if len(faces) == 0:
        return None

    img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

    snout_files = [f for f in os.listdir(snouts_folder) if f.endswith('.png')]
    if not snout_files:
        raise FileNotFoundError("В папке snouts/ нет PNG изображений!")

    for (x, y, w, h) in faces:
        snout_name = random.choice(snout_files)
        snout_path = os.path.join(snouts_folder, snout_name)
        snout_img = Image.open(snout_path).convert("RGBA")

        c = 0.2 # Коэфицент
        snout_width = int(w * 0.2) 
        ratio = snout_width / float(snout_img.size[0])
        snout_height = int(float(snout_img.size[1]) * ratio)
        
        snout_resized = snout_img.resize((snout_width, snout_height), Image.Resampling.LANCZOS)

        pos_x = int(x + w / 2 - snout_width / 2)
        pos_y = int(y + h / 2 - snout_height / 2 + (h * 0.05))
        img_pil.paste(snout_resized, (pos_x, pos_y), snout_resized)

    bio = BytesIO()
    img_pil.save(bio, 'JPEG')
    bio.seek(0)
    
    return bio