import time
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def rate_limit(seconds: int = 3):
    """
    Декоратор для ограничения частоты запросов пользователя.
    Данные о времени последнего запроса хранятся в context.user_data.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user or not update.effective_message:
                return await func(update, context, *args, **kwargs)

            current_time = time.time()
            last_request = context.user_data.get("last_action_time", 0)
            
            if current_time - last_request < seconds:
                remaining = int(seconds - (current_time - last_request))
                await update.effective_message.reply_text(
                    f"🐷 Тормози, пятачок! Куда летишь? Попробуй через {remaining} сек."
                )
                return 

            context.user_data["last_action_time"] = current_time
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator