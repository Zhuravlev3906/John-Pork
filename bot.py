from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.chat import chat
from handlers.errors import error_handler
from handlers.generate_pig import (
    get_generate_pig_handler,
    get_regenerate_callback_handler,
)
from handlers.edit_pig import get_edit_pig_handler  # <-- НОВОЕ
from handlers.swap_face import get_swap_face_handler


from config import TOKEN


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # --- Генерация свиньи ---
    # app.add_handler(get_generate_pig_handler())
    # app.add_handler(get_regenerate_callback_handler())

    # --- Редактирование свиньи ---
    app.add_handler(get_edit_pig_handler())

    app.add_handler(get_swap_face_handler())


    # --- Чат ---
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # --- Ошибки ---
    app.add_error_handler(error_handler)

    print("🐷 Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
