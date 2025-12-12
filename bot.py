from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler # <-- Добавили CallbackQueryHandler
from handlers.chat import chat
from handlers.errors import error_handler
from handlers.generate_pig import get_generate_pig_handler, get_regenerate_callback_handler # <-- Добавили новую функцию
from handlers.person_to_pig import person_to_pig
from config import TOKEN

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # --- 1. Обработчик для генерации изображения (ConversationHandler) ---
    app.add_handler(get_generate_pig_handler())
    
    # --- 2. Глобальный обработчик для кнопки "Перегенерировать" (CallbackQueryHandler) ---
    # Это устраняет PTBUserWarning, так как кнопка работает вне диалога ConversationHandler.
    app.add_handler(get_regenerate_callback_handler())

    # Команды
    # app.add_handler(CommandHandler("person_to_pig", person_to_pig))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    # Ошибки
    app.add_error_handler(error_handler)

    print("🐷 Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()