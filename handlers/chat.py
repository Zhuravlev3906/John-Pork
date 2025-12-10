from telegram import Update
from telegram.ext import ContextTypes
import logging
from utils.openai_api import get_chat_response 

logger = logging.getLogger(__name__)

BOT_USERNAME = "@iamjohnpork_bot" 

JOHN_PORK_KEYWORDS = [
    "джон", "джо", "эй джо", "привет джон", "свин", "свинья", BOT_USERNAME
]

def is_addressed_to_john_pork(text: str) -> bool:
    """Проверяет, обращаются ли к боту John Pork."""
    if not text:
        return False
    
    text_lower = text.lower()
    
    for keyword in JOHN_PORK_KEYWORDS:
        if text_lower.startswith(keyword.lower()):
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