import os
import io
import base64
import asyncio
import logging
from io import BytesIO

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

from openai import OpenAI
from config import PROXYAPI_API_KEY
from PIL import Image, ImageDraw, ImageFont
from handlers.chat import group_button
from utils.decorators import rate_limit

logger = logging.getLogger(__name__)

# --- CONFIG ---
WAITING_FOR_PHOTO = 1
PIG_IMAGE_PATH = "pig.jpg"
WATERMARK_TEXT = "@johnporkonton"

client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1",
)

def add_watermark(image_bytes: bytes, text: str) -> bytes:
    """
    Накладывает ватермарку с автоматическим подбором шрифта.
    """
    try:
        base_image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        width, height = base_image.size
        font_size = int(min(width, height) * 0.06)
        
        font_paths = [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf"
        ]
        
        font = None
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except IOError:
                continue
        
        if not font:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        margin = int(min(width, height) * 0.035)
        x = width - (text_bbox[2] - text_bbox[0]) - margin
        y = height - (text_bbox[3] - text_bbox[1]) - margin

        draw.text((x, y), text, fill=(255, 255, 255, 120), font=font)
        
        result = Image.alpha_composite(base_image, txt_layer)
        output = BytesIO()
        result.convert("RGB").save(output, format="JPEG", quality=95)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Watermark error in swap_face: {e}")
        return image_bytes

def sync_face_swap(human_image_bytes: bytes) -> bytes:
    """
    Синхронный вызов API для замены лица.
    """
    with open(PIG_IMAGE_PATH, "rb") as pig_file:
        human_file = io.BytesIO(human_image_bytes)
        human_file.name = "human.jpg"

        response = client.images.edit(
            model="gpt-image-1",
            image=[pig_file, human_file],
            prompt="Replace the human face with the pig face accurately",
            size="1024x1024",
            quality="medium"
        )
    return base64.b64decode(response.data[0].b64_json)

@rate_limit(seconds=30)
async def swap_face_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PIG_IMAGE_PATH):
        logger.error(f"Файл {PIG_IMAGE_PATH} не найден!")
        await update.message.reply_text("❌ Ошибка: Шхаблон свиньи отсутствует.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📸 Скидывай фотку человека. Сейчас сделаю его солидным свинтусом 🐷"
    )
    return WAITING_FOR_PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Это не фото. Пришли картинку!")
        return WAITING_FOR_PHOTO

    try:
        # Берем самое качественное фото
        photo = update.message.photo[-1]
        await update.message.reply_text("⏳ Снимаю мерки с лица...")

        file = await photo.get_file()
        photo_bytes = bytes(await file.download_as_bytearray())

        # Обработка в потоке
        result_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_face_swap, photo_bytes),
            timeout=90
        )
        
        final_image = await asyncio.to_thread(add_watermark, result_bytes, WATERMARK_TEXT)

        await update.message.reply_photo(
            photo=final_image,
            caption="🐷 Готово. Теперь он один из нас.",
            reply_markup=group_button()
        )
    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Слишком долго. API не отвечает.")
    except Exception as e:
        logger.error(f"Swap face error: {e}", exc_info=True)
        await update.message.reply_text("❌ Что-то пошло не так. Попробуй другое фото.")

    return ConversationHandler.END

async def cancel_swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отмена.")
    return ConversationHandler.END

def get_swap_face_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("swap_face", swap_face_start)],
        states={
            WAITING_FOR_PHOTO: [
                MessageHandler(filters.PHOTO, receive_photo)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_swap)],
        block=False
    )