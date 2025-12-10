import os
from dotenv import load_dotenv

load_dotenv() # Переменные из окружения

TOKEN = os.getenv("TG_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Ошибка: переменная окружения TG_BOT_TOKEN не установлена! Укажите TG_BOT_TOKEN в .env файле.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Ошибка: переменная окружения OPENAI_API_KEY не установлена! Укажите OPENAI_API_KEY в .env файле.")