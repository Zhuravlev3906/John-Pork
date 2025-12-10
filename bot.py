from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from handlers.chat import chat
from handlers.errors import error_handler
from handlers.generate_pig import get_generate_pig_handler
from handlers.person_to_pig import person_to_pig
from config import TOKEN

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    app.add_handler(get_generate_pig_handler())
    # app.add_handler(CommandHandler("person_to_pig", person_to_pig))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    # Ошибки
    app.add_error_handler(error_handler)

    print("🐷 Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
