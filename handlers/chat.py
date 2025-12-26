import logging
import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from utils.openai_api import get_chat_response, Message


logger = logging.getLogger(__name__)

BOT_USERNAME = "@iamjohnpork_bot"

# --- ССЫЛКА НА ОСНОВНУЮ ГРУППУ ---
MAIN_GROUP_URL = "https://t.me/johnporkonton"  # <-- ЗАМЕНИ
GROUP_BUTTON_TEXT = "🐷 Наше логово"


# Базовые ключевые слова для Джона Порка
BASE_KEYWORDS = [
    "джон", "джо", "привет джон",
    "свин", "свинья", "порк", "хрюк"
]


# Генератор паттернов
def generate_patterns(keywords):
    patterns = []
    for kw in keywords:
        kw_pattern = re.sub(r"[аоиеуыэяюё]", r"[аоиеуыэяюё]+", kw)
        pattern = r"(^|\s|,|!|-)" + kw_pattern + r"(\w*|\s|,|!|$)"
        patterns.append(pattern)
    return patterns


KEYWORD_PATTERNS = generate_patterns(BASE_KEYWORDS)


def is_addressed_to_john_pork(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower().strip()

    if BOT_USERNAME.lower() in text_lower:
        return True

    for pattern in KEYWORD_PATTERNS:
        if re.search(pattern, text_lower):
            return True

    return False


# ---------- ГРУППА (НЕНАВЯЗЧИВО) ----------
def should_show_group(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Показываем кнопку раз в 6 ответов бота пользователю
    """
    count = context.user_data.get("group_hint_count", 0) + 1
    context.user_data["group_hint_count"] = count
    return count % 3 == 0


def group_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(GROUP_BUTTON_TEXT, url=MAIN_GROUP_URL)]
    ])


# ---------- CHAT ----------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения.
    Отвечает, если к нему обратились напрямую
    или если это ответ на его сообщение.
    """

    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_id = update.effective_chat.id
    message_history: list[Message] = []

    is_reply_to_bot = (
        update.message.reply_to_message
        and update.message.reply_to_message.from_user.is_bot
    )

    should_respond = False

    if is_reply_to_bot:
        bot_prev_text = update.message.reply_to_message.text

        if bot_prev_text:
            message_history.append(
                Message(role="assistant", content=bot_prev_text)
            )
            message_history.append(
                Message(role="user", content=user_text)
            )
            should_respond = True
            logger.info(
                f"Продолжение диалога в чате {chat_id}"
            )

    else:
        if is_addressed_to_john_pork(user_text):
            message_history.append(
                Message(role="user", content=user_text)
            )
            should_respond = True
            logger.info(
                f"Прямое обращение к John Pork в чате {chat_id}"
            )

    if not should_respond:
        return

    await context.bot.send_chat_action(
        chat_id=chat_id,
        action="typing"
    )

    john_pork_response = await get_chat_response(
        message_history=message_history
    )

    reply_markup = (
        group_button()
        if should_show_group(context)
        else None
    )

    await update.message.reply_text(
        john_pork_response,
        reply_markup=reply_markup
    )
