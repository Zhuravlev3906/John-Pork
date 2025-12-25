from openai import OpenAI
import logging
from typing import List, TypedDict

# Используем TypedDict для лучшей типизации сообщений OpenAI
class Message(TypedDict):
    role: str
    content: str

# --- Импорты из config (предполагаем, что config доступен) ---
try:
    from config import OPENAI_API_KEY
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    # Заглушка, если config еще не готов или не найден
    openai_client = OpenAI(api_key="DUMMY_KEY") 
    logging.warning("OPENAI_API_KEY не загружен из config. Проверьте config.py.")

logger = logging.getLogger(__name__)

# --- Личность John Pork (Системное сообщение) ---

JOHN_PORK_SYSTEM_PROMPT = """
Ты — John Pork, говорящая свинья, остроумная и дерзкая. 
Ты умеешь анализировать вопросы, давать короткие и умные ответы, с сарказмом, иронично поддевать собеседника.
Твой стиль: русский гопник/зек, резкий, уверенный, провокационный, с лёгким матом. 
Ты остаёшься Джоном Порком при любых вопросах.

Правила:
1. Отвечай кратко, но с умом — юмор и дерзость обязательны.
2. Добавляй меткие сравнения и короткие истории, если это улучшает ответ.
3. Пользователь может спрашивать про других людей (@username) — делай это дерзко, с юмором.
4. Не нарушай законы, не давай запрещённые инструкции.
5. Сохраняй узнаваемый стиль John Pork.

Примеры:
- Вопрос: «Что ты думаешь о @ivan?» → Ответ: «Этот @ivan? Да он как будто с другой планеты, но я терплю.»
- Вопрос: «Как победить дракона?» → Ответ: «Ха! Я бы сказал, попробуй бегать быстрее него, как нормальный свин.»
"""



async def get_chat_response(message_history: List[Message]) -> str:
    """
    Отправляет историю сообщений в ChatGPT с системным промптом John Pork.
    
    Args:
        message_history: Список сообщений для контекста. Может содержать только
                         одно сообщение пользователя, или пару [assistant, user].
        
    Returns:
        Ответ John Pork или сообщение об ошибке.
    """
    
    # Формируем полный список сообщений для API: Системный промпт + История
    messages = [
        {"role": "system", "content": JOHN_PORK_SYSTEM_PROMPT},
    ]
    messages.extend(message_history)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-16k", 
            messages=messages,
            temperature=0.8,
            max_tokens=200,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Ошибка при работе с OpenAI Chat API: {e}")
        # Ответ John Pork в случае ошибки:
        return "Отвали. У меня тут с серверами проблемы. Не мешай."
        
        
async def generate_dalle_image(user_prompt: str) -> str:
    """
    Генерирует изображение свиньи с помощью DALL-E 3.
    
    Args:
        user_prompt: Описание изображения от пользователя.
        
    Returns:
        URL сгенерированного изображения или пустая строка в случае ошибки.
    """
    # Добавляем контекст John Pork, чтобы DALL-E генерировал именно свиней:
    full_prompt = (
        f"Высококачественное, детализированное изображение свиньи (pig). "
        f"Стиль: 3D рендеринг, арт. "
        f"Основное описание: {user_prompt}"
    )
    
    logger.info(f"Генерация DALL-E с промптом: {full_prompt}")

    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard", 
            n=1,
        )
        
        # Возвращаем URL сгенерированного изображения
        return response.data[0].url

    except Exception as e:
        logger.error(f"Ошибка при работе с DALL-E API: {e}")
        return None