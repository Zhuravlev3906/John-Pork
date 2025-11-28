import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Ошибка: переменная окружения TG_BOT_TOKEN не установлена! Укажите TG_BOT_TOKEN в .env файле.")

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

# Антиспам
RATE_LIMIT_SECONDS = 5
