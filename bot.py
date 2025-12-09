from telegram.ext import ApplicationBuilder, CommandHandler, ChatMemberHandler, MessageHandler, filters

from config import TOKEN
from handlers.start import start
from handlers.welcome import welcome_bot
from handlers.greeting import greet_new_member
from handlers.pig import pig
from handlers.generate_pig import generate_pig
from handlers.errors import error_handler
from handlers.snout import snout_handler

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(snout_handler)
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome_bot, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    app.add_handler(CommandHandler("pig", pig))
    app.add_handler(CommandHandler("generate_pig", generate_pig))

    # Ошибки
    app.add_error_handler(error_handler)

    print("🐷 Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
