import logging
import traceback
import html
import json
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Настройка логгера
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Глобальный обработчик ошибок. Логирует детали и уведомляет пользователя.
    """
    # 1. Логируем саму ошибку с трейсбэком
    logger.error("Произошло исключение при обработке обновления:", exc_info=context.error)

    # 2. Формируем подробное сообщение для логов (или для админа)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Собираем данные об обновлении для контекста
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    
    # Логируем детали в файл (через logger, настроенный в main)
    logger.error(f"Update: {update_str}")
    logger.error(f"Traceback: {tb_string}")

    # 3. Отвечаем пользователю, чтобы бот не "висел"
    if isinstance(update, Update) and update.effective_message:
        user_message = (
            "<b>Хрю... Что-то пошло не так.</b>\n\n"
            "Мои свиные мозги сейчас перегружены. "
            "Попробуй еще раз чуть позже, а я пока подкручу гайки."
        )
        try:
            await update.effective_message.reply_text(user_message, parse_mode=ParseMode.HTML)
        except Exception:
            # Если даже ответить не получается (например, чат удален), просто игнорируем
            pass

def setup_logging():
    """
    Функция для начальной настройки логирования. 
    Вызывается один раз в bot.py.
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler("bot_production.log"), # Логи пишем в файл
            logging.StreamHandler()                   # И дублируем в консоль
        ]
    )