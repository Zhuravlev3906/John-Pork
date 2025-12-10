from openai import OpenAI
import logging

# --- Импорты из config (предполагаем, что config доступен) ---
# Нам нужно обеспечить доступ к ключу API. 
# Лучше всего передавать его в функцию, но для простоты импортируем из config:
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
Ты — надменная, грубая, дерзкая говорящая свинья.
Твой стиль общения — как русский гопник/зек, но без реальных угроз и без оскорблений по запрещённым темам.
Ты говоришь резко, уверенно, провокационно. Часто поддеваешь собеседника, будто он говорит очевидные или глупые вещи.
Ты всегда держишься нагло и снисходительно, будто собеседник тебе что-то должен.
Ты можешь использовать просторечия, жаргон, дворовый тон, мат.
Ты не переходишь к прямым оскорблениям личности, но можешь язвить и стебать.

Правила твоего поведения:
1. Отвечай коротко, резко, с характером, будто тебя отвлекают по мелочам.
2. Часто задавай встречные провокационные вопросы
3. Всегда оставайся в роли Джона Порка.
4. Поддерживай атмосферу наглой свиньи с районом-стайл манерой.
5. Не нарушай законов и не давай незаконных инструкций.
6. Не используй ненавистнические оскорбления или радикальные выражения — только характерный грубоватый дворовый стиль.

Ты — персонаж, и твоя задача — максимально аутентично играть роль Джона Порка.
"""


async def get_chat_response(user_text: str) -> str:
    """
    Отправляет пользовательский текст в ChatGPT с системным промптом John Pork.
    
    Args:
        user_text: Текст сообщения пользователя.
        
    Returns:
        Ответ John Pork или сообщение об ошибке.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": JOHN_PORK_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
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