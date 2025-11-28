import random
from telegram import Update
from telegram.ext import ContextTypes
from config import IMAGES_DIR, RATE_LIMIT_SECONDS
from utils.images import get_random_image
from utils.rate_limit import rate_limit
from utils.phrases import load_phrases

# @rate_limit(RATE_LIMIT_SECONDS)
async def pig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет случайную мемную свинку.
    """

    message = update.effective_message

    if not message:
        return 

    if message.reply_to_message:
        replied_user = message.reply_to_message.from_user
        
        if replied_user:
            username = replied_user.username if replied_user.username else f"id{replied_user.id}"
        elif message.reply_to_message.sender_chat:
            chat = message.reply_to_message.sender_chat
            username = chat.username if chat.username else chat.title
        else:
            sender = message.from_user
            username = sender.username if sender.username else f"id{sender.id}"

    elif context.args:
        username = context.args[0].lstrip("@")

    else:
        sender = message.from_user
        username = sender.username if sender.username else f"id{sender.id}"

    img_path = get_random_image(IMAGES_DIR)

    pig_phrases = load_phrases("data/pig_phrases.txt")
    caption = random.choice(pig_phrases).replace("{username}", "@" + username)

    # Отправляем фото с подписью
    with open(img_path, "rb") as f:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=f,
            caption=caption
        )