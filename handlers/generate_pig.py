from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, # <-- ИМПОРТ
    filters
)
import logging
from utils.openai_api import generate_dalle_image 
import uuid 

logger = logging.getLogger(__name__)

# --- 1. Состояния ---
AWAITING_PROMPT = 1 

# --- 2. Константа для Callback-запроса ---
REGENERATE_CALLBACK_PREFIX = "regenerate_pig_image_"


# --- 3. Функции-обработчики ---

async def start_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог /generate_pig. Просит описание."""
    
    await update.message.reply_text(
        "Что, <b>опять</b> тебе картинка нужна? "
        "Ладно, давай. Но если пришлёшь мне какой-нибудь мусор, отвечать не буду. "
        "Говори уже, <b>что за свинью ты там себе надумал</b>. "
        "Давай быстрее, не задерживай тут очередь, мне не до тебя.",
        parse_mode="HTML"
    )
    
    return AWAITING_PROMPT


async def generate_pig_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """
    Получает описание от пользователя или кнопки, генерирует изображение DALL-E и отправляет его с кнопкой.
    """
    
    # Инициализация переменных для промпта и chat_id
    user_prompt = None
    chat_id = None
    
    # 1. Определяем источник запроса: Сообщение (первый запуск) или Callback (перегенерация)
    if update.message:
        user_prompt = update.message.text
        chat_id = update.effective_chat.id
        
        if not user_prompt:
            await update.message.reply_text("Я сказал <b>ТЕКСТ</b>! Ты что, читать не умеешь? Хватит мне всякую ерунду слать. <b>Давай нормальное описание!</b>", parse_mode="HTML")
            return AWAITING_PROMPT 
            
    elif update.callback_query:
        # Если это callback, промпт был сохранен в user_data в regenerate_pig_callback
        user_prompt = context.user_data.get('current_pig_prompt')
        chat_id = update.effective_chat.id
        
        if not user_prompt:
            await update.callback_query.answer("Эх, промпт куда-то делся. Попробуй сначала, лопух.")
            await context.bot.send_message(chat_id, "/generate_pig - давай еще раз")
            return None # Завершаем, так как данные потеряны (вне ConversationHandler)
            
    
    # 2. Логика генерации
    
    # Отправляем "думаю"
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
    if update.message:
        await update.message.reply_text("Хммм... Ладно. Сейчас посмотрим, что можно выжать из твоей ерунды. Сиди и не дергайся.")
        
    # Генерируем уникальный ключ и сохраняем промпт
    prompt_key = f"{REGENERATE_CALLBACK_PREFIX}{uuid.uuid4()}"
    context.user_data[prompt_key] = user_prompt 
    context.user_data['current_pig_prompt'] = user_prompt # Для использования при регенерации
    
    # --- Вызов утилиты для генерации ---
    image_url = await generate_dalle_image(user_prompt)
    
    # 3. Отправка результата
    if image_url:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Перегенерировать", 
                    callback_data=prompt_key
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption="На, подавись. Не говори, что я тебе ничего не сделал. И не вздумай мне жаловаться, если оно кривое.",
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
             chat_id=chat_id,
             text="Что-то у тебя там криво пошло. Ожидаемо. Скорее всего, ты что-то не то написал. Попробуй еще, но в следующий раз <b>думай, что печатаешь</b>.",
             parse_mode="HTML"
        )

    # Завершаем ConversationHandler только если это был первый ввод (Message)
    if update.message:
        return ConversationHandler.END
    
    return None # Если это была регенерация (Callback), возвращаем None


async def regenerate_pig_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатие инлайн-кнопки "Перегенерировать"."""
    
    query = update.callback_query
    await query.answer() 
    
    callback_data = query.data 
    user_prompt = context.user_data.get(callback_data)
    
    if user_prompt:
        # Изменяем сообщение, чтобы показать прогресс
        await query.edit_message_caption(
            caption=f"Понял, понял. В прошлый раз, видимо, криво вышло. Ладно, держи. Перегенерирую: **«{user_prompt[:50]}...»**\n\n**🔄 Идет генерация...**",
            parse_mode="Markdown"
        )
        
        # Запускаем генерацию снова, используя CallbackQuery's update
        # Важно: тут мы используем update от CallbackQuery, а не от Message.
        await generate_pig_image(update, context)
        
        # Удаляем старые данные
        del context.user_data[callback_data]
        # Если больше нет активных промптов в context.user_data, можно удалить 'current_pig_prompt'
        # Но оставим его для простоты, т.к. он перезапишется при следующем нажатии
        
    else:
        await query.edit_message_caption(
            caption="Проехали! Я забыл, что ты там просил. Говорю же, не дергай меня. Начни заново: /generate_pig",
        )


async def cancel_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для команды /cancel в процессе генерации."""
    await update.message.reply_text("Что, слился? Я так и думал. Вали отсюда. Когда решишь, что тебе <b>действительно</b> надо, тогда и вернешься.", parse_mode="HTML")
    return ConversationHandler.END


# --- 4. Функции для регистрации хендлеров ---

def get_generate_pig_handler() -> ConversationHandler:
    """Возвращает ConversationHandler для диалога /generate_pig."""
    return ConversationHandler(
        entry_points=[CommandHandler("generate_pig", start_generate_pig)],
        
        states={
            AWAITING_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pig_image),
                MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT, start_generate_pig),
            ],
        },
        
        fallbacks=[CommandHandler("cancel", cancel_generate_pig)],
    )

def get_regenerate_callback_handler() -> CallbackQueryHandler:
    """
    Возвращает CallbackQueryHandler для кнопки "Перегенерировать".
    Регистрируется ГЛОБАЛЬНО в Application.
    """
    return CallbackQueryHandler(
        regenerate_pig_callback, 
        pattern=f"^{REGENERATE_CALLBACK_PREFIX}"
    )