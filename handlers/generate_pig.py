from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
import logging
from utils.openai_api import generate_dalle_image 

logger = logging.getLogger(__name__)

# --- 1. Состояния ---
AWAITING_PROMPT = 1 

# --- 2. Функции-обработчики ---

async def start_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог /generate_pig. Просит описание."""
    
    # John Pork просит описание в своей манере
    await update.message.reply_text(
        "Что, <b>опять</b> тебе картинка нужна? "
        "Ладно, давай. Но если пришлёшь мне какой-нибудь мусор, отвечать не буду. "
        "Говори уже, <b>что за свинью ты там себе надумал</b>. "
        "Давай быстрее, не задерживай тут очередь, мне не до тебя.",
        parse_mode="HTML"
    )
    
    # Переходим в состояние ожидания промпта
    return AWAITING_PROMPT


async def generate_pig_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает описание от пользователя, генерирует изображение DALL-E и завершает диалог."""
    
    user_prompt = update.message.text
    chat_id = update.effective_chat.id
    
    if not user_prompt:
        # Если пришел не текст, просим повторить
        await update.message.reply_text("Я сказал <b>ТЕКСТ</b>! Ты что, читать не умеешь? Хватит мне всякую ерунду слать. <b>Давай нормальное описание!</b>", parse_mode="HTML")
        return AWAITING_PROMPT 

    # John Pork показывает, что он "думает"
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
    await update.message.reply_text("Хммм... Ладно. Сейчас посмотрим, что можно выжать из твоей ерунды. Сиди и не дергайся.")

    # --- Вызов утилиты для генерации ---
    image_url = await generate_dalle_image(user_prompt)
    
    if image_url:
        # Отправляем изображение пользователю
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption="На, подавись. Не говори, что я тебе ничего не сделал. И не вздумай мне жаловаться, если оно кривое."
        )
    else:
        # Ответ в случае ошибки (пришел из utils/openai_api.py)
        await update.message.reply_text(
            "Что-то у тебя там криво пошло. Ожидаемо. Скорее всего, ты что-то не то написал. Попробуй еще, но в следующий раз <b>думай, что печатаешь</b>.",
            parse_mode="HTML"
        )

    # Завершаем разговор
    return ConversationHandler.END


async def cancel_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для команды /cancel в процессе генерации."""
    await update.message.reply_text("Что, слился? Я так и думал. Вали отсюда. Когда решишь, что тебе <b>действительно</b> надо, тогда и вернешься.", parse_mode="HTML")
    return ConversationHandler.END


# --- 3. Создание ConversationHandler ---

def get_generate_pig_handler() -> ConversationHandler:
    """Возвращает готовый ConversationHandler для регистрации в bot.py."""
    return ConversationHandler(
        entry_points=[CommandHandler("generate_pig", start_generate_pig)],
        
        states={
            AWAITING_PROMPT: [
                # Ожидаем ТЕКСТ от пользователя
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pig_image),
                # Если пользователь прислал что-то другое (не текст)
                MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT, start_generate_pig),
            ],
        },
        
        # Команда отмены
        fallbacks=[CommandHandler("cancel", cancel_generate_pig)],
    )