import os
import base64
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

openai_client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=5)  # больше потоков для параллельных запросов

WAITING_FOR_PROMPT = 1
IMAGE_PATH = "pig.jpg"


async def edit_pig_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(IMAGE_PATH):
        await update.message.reply_text("❌ Файл pig.jpg не найден.")
        return ConversationHandler.END

    await update.message.reply_text(
        "Ну давай, пиши что хочешь увидеть. Только шустро.\n\n"
        "Пример:\n"
        "`Свинья-халк едет на мотоцикле`",
        parse_mode="Markdown"
    )

    return WAITING_FOR_PROMPT


def sync_generate_image(d_prompt: str) -> bytes:
    """Синхронный вызов OpenAI API для редактирования изображения"""
    with open(IMAGE_PATH, "rb") as image_file:
        result = openai_client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=d_prompt,
            size="1024x1024",
        )
    return base64.b64decode(result.data[0].b64_json)


async def receive_edit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    d_prompt = (
        "Главное правило: Сохрани морду свинки, глаза, пятачок, прическу и узнаваемый характер\n"
        f"Вот запрос пользователя: {prompt}"
    )

    await update.message.reply_text("⏳ Ща поколдую над свиньёй...")

    try:
        # Асинхронно запускаем синхронный вызов в отдельном потоке с таймаутом
        image_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_generate_image, d_prompt),
            timeout=60  # например, 60 секунд
        )

        await update.message.reply_photo(
            photo=image_bytes,
            caption="🐷 Готово. Любуйся."
        )

    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Слишком долго. Попробуй ещё раз позже.")
    except Exception as e:
        logger.exception("Ошибка edit_pig")
        await update.message.reply_text(f"❌ Ошибка:\n{e}")

    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ладно, передумал.")
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
    )
