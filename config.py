import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TG_BOT_TOKEN не установлен")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не установлен")

PROXYAPI_API_KEY = os.getenv("PROXYAPI_API_KEY")
if not PROXYAPI_API_KEY:
    raise ValueError("PROXYAPI_API_KEY не установлен")
