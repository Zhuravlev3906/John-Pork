import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.phrases import load_phrases

async def welcome_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие группы при добавлении бота.
    """
    old_status = update.my_chat_member.old_chat_member.status
    new_status = update.my_chat_member.new_chat_member.status

    # keyboard = [
    #     [InlineKeyboardButton("Кто я сегодня", callback_data="whoiamtoday")]
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)

    phrases = load_phrases("data/welcome_phrases.txt")
    text = random.choice(phrases)

    if old_status in ['left', 'kicked'] and new_status in ['member', 'administrator']:
        chat_id = update.my_chat_member.chat.id
        # await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        await context.bot.send_message(chat_id=chat_id, text=text)
