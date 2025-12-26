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

from openai import OpenAI
from config import PROXYAPI_API_KEY

from PIL import Image, ImageDraw, ImageFont

from handlers.chat import group_button


logger = logging.getLogger(__name__)

# ---------- CONFIG ----------
WAITING_FOR_PHOTO = 1
PIG_IMAGE_PATH = "pig.jpg"
WATERMARK_TEXT = "@johnporkonton"
# ---------------------------


openai_client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1",
)


# ---------- WATERMARK ----------
def add_watermark(image_bytes: bytes, text: str, opacity: int = 120) -> bytes:
    base_image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    width, height = base_image.size
    base = min(width, height)

    font_size = int(base * 0.045)
    margin = int(base * 0.035)

    txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = width - text_width - margin
    y = height - text_height - margin

    draw.text(
        (x, y),
        text,
        fill=(255, 255, 255, opacity),
        font=font,
    )

    result = Image.alpha_composite(base_image, txt_layer)
    output = BytesIO()
    result.convert("RGB").save(output, format="JPEG", quality=95)

    return output.getvalue()


# ---------- OPENAI ----------
def sync_face_swap(human_image_bytes: bytes) -> bytes:
    with open(PIG_IMAGE_PATH, "rb") as pig_file:
        human_image_file = io.BytesIO(human_image_bytes)
        human_image_file.name = "human.jpg"

        result = openai_client.images.edit(
            model="gpt-image-1",
            image=[pig_file, human_image_file],
            prompt="Replace the human face with the pig face",
            size="1024x1024",
        )

    return base64.b64decode(result.data[0].b64_json)


# ---------- HANDLERS ----------
async def swap_face_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PIG_IMAGE_PATH):
        await update.message.reply_text("❌ Файл pig.jpg не найден.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📸 Ну давай, скидывай фотку\n"
        "Сделаю её более престижной 🐷"
    )

    return WAITING_FOR_PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        await update.message.reply_text("⏳ Меняю морду...")

        file = await photo.get_file()
        human_image_bytes = bytes(await file.download_as_bytearray())

        image_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_face_swap, human_image_bytes),
            timeout=90,
        )

        image_bytes = await asyncio.to_thread(
            add_watermark,
            image_bytes,
            WATERMARK_TEXT,
        )

        await update.message.reply_photo(
            photo=image_bytes,
            caption="🐷 Готово. Теперь он один из нас.",
            reply_markup=group_button(),
        )

    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Слишком долго. Попробуй позже.")
    except Exception:
        logger.exception("Ошибка swap_face")
        await update.message.reply_text("❌ Тут какие-то проблемки. Потом зайди, добро?")

    return ConversationHandler.END


async def cancel_swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ладно, отменили.")
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
        block=False,
        allow_reentry=True,
    )
