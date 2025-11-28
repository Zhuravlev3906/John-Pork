import time
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

_last_called = {}  # chat_id → timestamp


def rate_limit(seconds: int):
    """
    Ограничивает частоту вызова команды в рамках одного чата.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            chat_id = update.effective_chat.id
            now = time.time()
            last = _last_called.get(chat_id, 0)

            if now - last < seconds:
                remaining = int(seconds - (now - last))
                await update.message.reply_text(
                    f"Не спамь, дружище 🐷 Подожди ещё {remaining} сек!"
                )
                return

            _last_called[chat_id] = now
            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator
