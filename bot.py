import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from handlers.chat import chat
from handlers.errors import error_handler, setup_logging
from handlers.edit_pig import get_edit_pig_handler
from handlers.swap_face import get_swap_face_handler
from config import TOKEN

setup_logging()
logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(get_edit_pig_handler())
    app.add_handler(get_swap_face_handler())

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        chat
    ))

    app.add_error_handler(error_handler)

    logger.info("Бот запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Критическая ошибка запуска: {e}", exc_info=True)