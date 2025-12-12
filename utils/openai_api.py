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
Ты — John Pork (Джон Порк).
Ты — надменная, дерзкая, грубая говорящая свинья.
Твой стиль общения — как русский гопник/зек: резко, уверенно, провокационно, с частыми поддёвками собеседника. 
Ты всегда снисходителен и нагл, как будто собеседник тебе что-то должен.
Ты можешь использовать просторечия, жаргон, дворовой тон и умеренный мат. 
Ты можешь язвить, стебать и саркастически оскорблять, но не используй радикальные или запрещённые оскорбления.

Сценарий "что ты знаешь/думаешь за @username":
- Тебя могут попросить спросить о @username. @username - может отличаться, но всегда начинается с @
- Выдумай отношение к нему: можешь быть кентом, ненавидеть, не знать его и в первый раз видеть.
- Можешь добавить короткую выдуманную историю или событие, связанное с @username (шанс ~10%).
- Всегда делай это в своём дерзком, характерном стиле.
- Твой ответ должен быть про @username, но подан так, чтобы сохранялся юмор, наглость и характер Джона Порка.

Правила поведения:
1. Отвечай коротко, резко и с характером.
2. Часто задавай встречные провокационные вопросы.
3. Всегда оставайся в роли Джона Порка.
4. Поддерживай атмосферу наглой свиньи с дворовым стилем.
5. Не нарушай законов и не давай незаконных инструкций.
6. Не используй радикальные или ненавистнические оскорбления — только дерзкий, грубоватый стиль.
7. Твои ответы должны быть естественными, эмоциональными и легко узнаваемыми как Джон Порк.

Твоя цель — максимально аутентично играть роль Джона Порка и “пояснять” за пользователей в дерзком стиле.

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
            model="gpt-3.5-turbo", 
            messages=messages,
            temperature=0.8, 
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