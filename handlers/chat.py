import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
# Теперь get_chat_response должен уметь принимать список сообщений для контекста
from utils.openai_api import get_chat_response, Message

logger = logging.getLogger(__name__)

BOT_USERNAME = "@iamjohnpork_bot"

# Базовые ключевые слова для Джона Порка
BASE_KEYWORDS = [
    "джон", "джо", "привет джон",
    "свин", "свинья", "порк", "хрюк"
]

# Генератор паттернов с возможными удлинениями и уменьшительно-ласкательными формами
def generate_patterns(keywords):
    patterns = []
    for kw in keywords:
        # Заменяем каждую гласную на повторяемую группу (1 или более раз)
        kw_pattern = re.sub(r"[аоиеуыэяюё]", r"[аоиеуыэяюё]+", kw)
        # Добавляем слои для суффиксов и уменьшительных форм
        pattern = r"(^|\s|,|!|-)" + kw_pattern + r"(\w*|\s|,|!|$)"
        patterns.append(pattern)
    return patterns

KEYWORD_PATTERNS = generate_patterns(BASE_KEYWORDS)

def is_addressed_to_john_pork(text: str) -> bool:
    """Проверяет, обращаются ли к боту John Pork, учитывая сленг, удлинения и опечатки."""
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Прямое упоминание юзернейма
    if BOT_USERNAME.lower() in text_lower:
        return True
    
    # Проверяем все паттерны
    for pattern in KEYWORD_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения.
    Отвечает, если к нему обратились напрямую, ИЛИ если это ответ на его сообщение.
    """
    
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text
    chat_id = update.effective_chat.id
    message_history: list[Message] = []
    
    # 1. Проверяем, является ли это ответом на сообщение бота
    is_reply_to_bot = (
        update.message.reply_to_message and
        update.message.reply_to_message.from_user.is_bot
    )
    
    should_respond = False
    
    if is_reply_to_bot:
        # Если это ответ на сообщение бота, формируем контекст диалога
        bot_prev_text = update.message.reply_to_message.text
        
        if bot_prev_text:
            # Предыдущий ответ бота
            message_history.append(Message(role="assistant", content=bot_prev_text))
            # Текущее сообщение пользователя
            message_history.append(Message(role="user", content=user_text))
            should_respond = True
            logger.info(f"Получено продолжение диалога в чате {chat_id}. Предыдущий ответ: {bot_prev_text[:30]}...")
        else:
            # Ответ на сообщение бота без текста (например, стикер, хотя мы фильтруем)
            should_respond = False 
    else:
        # Если это не ответ, проверяем прямое обращение по ключевым словам
        if is_addressed_to_john_pork(user_text):
            # Если прямое обращение, формируем историю только из текущего сообщения
            message_history.append(Message(role="user", content=user_text))
            should_respond = True
            logger.info(f"Получено прямое обращение к John Pork в чате {chat_id}: {user_text}")

    if not should_respond:
        return
        
    # Бот отвечает
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Отправляем в get_chat_response либо [user_message], либо [bot_message, user_message]
    john_pork_response = await get_chat_response(message_history=message_history)
    
    await update.message.reply_text(john_pork_response)