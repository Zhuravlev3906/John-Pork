import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from handlers.chat import chat
from handlers.errors import error_handler, setup_logging
# from handlers.generate_pig import (
#     get_generate_pig_handler,
#     get_regenerate_callback_handler,
# )
from handlers.edit_pig import get_edit_pig_handler
from handlers.swap_face import get_swap_face_handler
from utils.decorators import rate_limit
from config import TOKEN

# Инициализация логов
setup_logging()
logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # # Регистрация хендлеров (лимиты уже внутри функций старта)
    # app.add_handler(get_generate_pig_handler())
    # app.add_handler(get_regenerate_callback_handler())
    app.add_handler(get_edit_pig_handler())
    app.add_handler(get_swap_face_handler())

    # Чат с лимитом в 2 секунды
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        rate_limit(seconds=2)(chat)
    ))

    # Обработка ошибок
    app.add_error_handler(error_handler)

    logger.info("Бот запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Критическая ошибка запуска: {e}", exc_info=True)