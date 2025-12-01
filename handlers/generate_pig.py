from telegram import Update
from telegram.ext import ContextTypes
from utils.fusion_api import generate_pig_image

async def generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генерирует свинку по текстовому описанию
    """

    if not context.args:
        await update.message.reply_text("Напишите описание: /generate_pig розовая свинка в пиджаке")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text("Генерирую свинку... 🐷")

    img_bytes = await generate_pig_image(prompt)

    if img_bytes == None:
        await update.message.reply_text("Не удалось сгенерировать изображение :(")
        return

    await update.message.reply_photo(img_bytes)