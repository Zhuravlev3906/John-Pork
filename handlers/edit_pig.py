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
from telegram.constants import ParseMode

from openai import OpenAI
from config import PROXYAPI_API_KEY
from PIL import Image, ImageDraw, ImageFont
from handlers.chat import group_button
from utils.decorators import rate_limit

logger = logging.getLogger(__name__)

# --- CONFIG ---
WAITING_FOR_PROMPT = 1
IMAGE_PATH = "pig.jpg"
WATERMARK_TEXT = "@johnporkonton"

client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1",
)

def add_watermark(image_bytes: bytes, text: str) -> bytes:
    """
    Накладывает ватермарку. Безопасно подбирает шрифт для любой ОС.
    """
    try:
        base_image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        width, height = base_image.size
        font_size = int(min(width, height) * 0.06)
        
        # Попытка найти стандартные шрифты для Linux или Windows
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
        logger.error(f"Watermark error: {e}")
        return image_bytes

def sync_generate_edit(prompt: str) -> bytes:
    """
    Синхронный вызов API для редактирования изображения.
    """
    with open(IMAGE_PATH, "rb") as f:
        response = client.images.edit(
            model="gpt-image-1",
            image=f,
            prompt=prompt,
            size="1024x1024",
            quality="medium"
        )
    return base64.b64decode(response.data[0].b64_json)

@rate_limit(seconds=30)
async def edit_pig_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(IMAGE_PATH):
        logger.error(f"Файл {IMAGE_PATH} не найден!")
        await update.message.reply_text("че, фото мое куда-то подевалось. видать свиньи в тг его съели.")
        return ConversationHandler.END

    await update.message.reply_text(
        "ну че, гений, шли свою идею.\n"
        "типа `свинья в скафандре с кошельком вместо головы`\n\n"
        "пиши /cancel если ты не уверен в себе",
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_FOR_PROMPT

async def receive_edit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    final_prompt = f"Maintain the pig face and character. Add: {user_prompt}"
    
    await update.message.reply_text("щас поколдую... если получится кринж - это твои проблемы.")

    try:
        # Запуск тяжелых операций в отдельном потоке
        image_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_generate_edit, final_prompt),
            timeout=60
        )
        
        processed_image = await asyncio.to_thread(add_watermark, image_bytes, WATERMARK_TEXT)

        await update.message.reply_photo(
            photo=processed_image,
            caption="готово. можешь выставлять как nft, вдруг кто-то купит этого уродца.",
            reply_markup=group_button()
        )
    except asyncio.TimeoutError:
        await update.message.reply_text("ой, сервера опять тупят. попробуй позже, если не передумал.")
    except Exception as e:
        logger.error(f"Edit pig error: {e}", exc_info=True)
        await update.message.reply_text("что-то пошло не так. может, твой запрос был слишком криповым для ии.")

    return ConversationHandler.END

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("отмена. ну и ладно, идея была так себе.")
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
        block=False
    )