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
        "О, тебе нужна картинка? Хорошо. "
        "Только не вздумай присылать мне всякий мусор. "
        "**Пришли мне текст, описывающий свинью, которую ты хочешь получить.** "
        "И давай быстрее, я занят."
    )
    
    # Переходим в состояние ожидания промпта
    return AWAITING_PROMPT


async def generate_pig_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает описание от пользователя, генерирует изображение DALL-E и завершает диалог."""
    
    user_prompt = update.message.text
    chat_id = update.effective_chat.id
    
    if not user_prompt:
        # Если пришел не текст, просим повторить
        await update.message.reply_text("Я сказал ТЕКСТ. Не трать мое время. Пришли мне описание!")
        return AWAITING_PROMPT 

    # John Pork показывает, что он "думает"
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
    await update.message.reply_text("Хм... Посмотрим, что я могу для тебя сделать. Жди.")

    # --- Вызов утилиты для генерации ---
    image_url = await generate_dalle_image(user_prompt)
    
    if image_url:
        # Отправляем изображение пользователю
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption="Держи. Это, конечно, не шедевр, но для тебя сойдет."
        )
    else:
        # Ответ в случае ошибки (пришел из utils/openai_api.py)
        await update.message.reply_text(
            "Тут какая-то ерунда с картинками. Не удивлен, ты даже описание нормально дать не можешь. Попробуй позже."
        )

    # Завершаем разговор
    return ConversationHandler.END


async def cancel_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для команды /cancel в процессе генерации."""
    await update.message.reply_text("Скучно. Ладно, отменил. Когда повзрослеешь, приходи.")
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