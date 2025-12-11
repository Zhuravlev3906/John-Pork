import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from utils.openai_api import get_chat_response 

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
    """Обрабатывает текстовые сообщения и отвечает через ChatGPT, если к нему обратились."""
    
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text
    chat_id = update.effective_chat.id

    if not is_addressed_to_john_pork(user_text):
        return
        
    logger.info(f"Получено обращение к John Pork в чате {chat_id}: {user_text}")

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    john_pork_response = await get_chat_response(user_text)
    
    await update.message.reply_text(john_pork_response)