import os
import base64
import logging
import asyncio
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

from handlers.chat import group_button  # 👈 кнопка группы


# ---------- CONFIG ----------
WAITING_FOR_PROMPT = 1
IMAGE_PATH = "pig.jpg"
WATERMARK_TEXT = "@johnporkonton"
# ----------------------------


openai_client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1",
)

logger = logging.getLogger(__name__)


# ---------- WATERMARK ----------
def add_watermark(
    image_bytes: bytes,
    text: str,
    opacity: int = 120,
    margin: int = 20,
) -> bytes:
    base_image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    font_size = max(24, base_image.size[0] // 30)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = base_image.size[0] - text_width - margin
    y = base_image.size[1] - text_height - margin

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
def sync_generate_image(prompt: str) -> bytes:
    with open(IMAGE_PATH, "rb") as image_file:
        result = openai_client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
        )

    return base64.b64decode(result.data[0].b64_json)


# ---------- HANDLERS ----------
async def edit_pig_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(IMAGE_PATH):
        await update.message.reply_text("❌ Файл pig.jpg не найден.")
        return ConversationHandler.END

    await update.message.reply_text(
        "Ну давай, пиши что хочешь увидеть 👀\n\n"
        "Пример:\n"
        "`Свинья-халк едет на мотоцикле`",
        parse_mode="Markdown",
    )

    return WAITING_FOR_PROMPT


async def receive_edit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text

    final_prompt = (
        "Главное правило: сохрани морду свинки, глаза, пятачок, прическу "
        "и узнаваемый характер.\n"
        f"Запрос пользователя: {user_prompt}"
    )

    await update.message.reply_text("⏳ Ща поколдую над свиньёй...")

    try:
        image_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_generate_image, final_prompt),
            timeout=60,
        )

        image_bytes = await asyncio.to_thread(
            add_watermark,
            image_bytes,
            WATERMARK_TEXT,
        )

        await update.message.reply_photo(
            photo=image_bytes,
            caption="🐷 Готово. Любуйся.",
            reply_markup=group_button(),  # 👈 ВСЕГДА
        )

    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Слишком долго. Попробуй позже.")
    except Exception:
        logger.exception("Ошибка edit_pig")
        await update.message.reply_text("❌ Что-то пошло не так. Зайди позже.")

    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменили.")
    return ConversationHandler.END


def get_edit_pig_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("edit_pig", edit_pig_start)],
        states={
            WAITING_FOR_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_prompt)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_edit)],
        block=False,
        allow_reentry=True,
    )
