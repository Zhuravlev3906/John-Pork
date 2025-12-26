import logging
from typing import List, TypedDict, Optional
from openai import OpenAI
from config import OPENAI_API_KEY

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

class Message(TypedDict):
    role: str
    content: str

# Инициализация клиента
client = OpenAI(api_key=OPENAI_API_KEY)

JOHN_PORK_SYSTEM_PROMPT = """
Ты — John Pork, говорящая свинья. Твой стиль: резкий, дерзкий, ироничный, с легким налетом тюремного или уличного сленга. 
Отвечай кратко, едко и всегда оставайся в образе. Ты не любишь глупые вопросы, но отвечаешь на них с сарказмом.
"""

async def get_chat_response(message_history: List[Message]) -> str:
    """
    Получает текстовый ответ от GPT-4o-mini.
    """
    messages = [{"role": "system", "content": JOHN_PORK_SYSTEM_PROMPT}]
    messages.extend(message_history)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=250,
            timeout=30.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Chat Error: {e}", exc_info=True)
        return "Слышь, у меня там провода перехрюкались. Позже зайди."

async def generate_dalle_image(user_prompt: str) -> Optional[str]:
    """
    Генерирует изображение через DALL-E 3.
    """
    full_prompt = (
        f"High-quality 3D render of John Pork (a humanoid pig character). "
        f"Scenario: {user_prompt}. Cinematic lighting, detailed textures."
    )
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            timeout=60.0
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E Error: {e}", exc_info=True)
        return None