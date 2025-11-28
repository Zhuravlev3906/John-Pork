import random
from telegram import Update
from telegram.ext import ContextTypes
from utils.phrases import load_phrases

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrases = load_phrases("data/greeting_phrases.txt")
    
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        
        username = member.username
        text = random.choice(phrases).replace("{username}", "@" + username)
        await update.message.reply_text(text=text)
