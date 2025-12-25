import os
import io
import base64
import asyncio
import logging

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

logger = logging.getLogger(__name__)

# --- ProxyAPI client ---
openai_client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

# --- Conversation state ---
WAITING_FOR_PHOTO = 1

# --- Constants ---
PIG_IMAGE_PATH = "pig.jpg"


async def swap_face_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт команды /swap_face"""
    if not os.path.exists(PIG_IMAGE_PATH):
        await update.message.reply_text("❌ Файл pig.jpg не найден.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📸 Пришли фото человека.\n"
        "Я заменю его лицо на свинское 🐷"
    )
    return WAITING_FOR_PHOTO


def sync_face_swap(human_image_bytes: bytes) -> bytes:
    """
    Синхронный вызов ProxyAPI (face swap).
    ВАЖНО: используем BytesIO + name, иначе будет unsupported mimetype.
    """
    with open(PIG_IMAGE_PATH, "rb") as pig_file:
        human_image_file = io.BytesIO(human_image_bytes)
        human_image_file.name = "human.jpg"  # 👈 критично для MIME-типа

        result = openai_client.images.edit(
            model="gpt-image-1",
            image=[
                pig_file,          # pig.jpg (image/jpeg)
                human_image_file,  # human.jpg (image/jpeg)
            ],
            prompt="Replace the human face with the pig face",
            size="1024x1024",
        )

    return base64.b64decode(result.data[0].b64_json)


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимаем фото и запускаем face swap"""
    try:
        photo = update.message.photo[-1]
        await update.message.reply_text("⏳ Меняю морду...")

        file = await photo.get_file()
        human_image_bytes = bytes(await file.download_as_bytearray())

        image_bytes = await asyncio.wait_for(
            asyncio.to_thread(sync_face_swap, human_image_bytes),
            timeout=90
        )

        await update.message.reply_photo(
            photo=image_bytes,
            caption="🐷 Готово. Теперь он один из нас."
        )

    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Слишком долго. Попробуй позже.")
    except Exception as e:
        logger.exception("Ошибка swap_face")
        await update.message.reply_text(f"❌ Ошибка:\n{e}")

    return ConversationHandler.END


async def cancel_swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена команды"""
    await update.message.reply_text("❌ Ладно, отменили.")
    return ConversationHandler.END


def get_swap_face_handler() -> ConversationHandler:
    """Регистрация ConversationHandler"""
    return ConversationHandler(
        entry_points=[CommandHandler("swap_face", swap_face_start)],
        states={
            WAITING_FOR_PHOTO: [
                MessageHandler(filters.PHOTO, receive_photo)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_swap)],
    )
