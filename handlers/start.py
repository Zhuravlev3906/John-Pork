import random
from telegram import Update
from telegram.ext import ContextTypes
from utils.phrases import load_phrases

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    bot_username = context.bot.username
    phrases = load_phrases("data/start_phrases.txt")
    text = random.choice(phrases) + f"\n\nМой username: @{bot_username}"

    await update.message.reply_text(text=text)
