import logging
import uuid
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode, ChatAction
from utils.openai_api import generate_dalle_image 
from utils.decorators import rate_limit

logger = logging.getLogger(__name__)

# --- CONFIG ---
AWAITING_PROMPT = 1 
REGEN_PREFIX = "regen_pig_"

@rate_limit(seconds=30)
async def start_generate_pig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Что, <b>опять</b> тебе картинка нужна? Ладно, давай описание. "
        "Только не задерживай очередь, мне не до тебя.",
        parse_mode=ParseMode.HTML
    )
    return AWAITING_PROMPT

async def generate_pig_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    chat_id = update.effective_chat.id
    
    if update.message:
        user_prompt = update.message.text
        if not user_prompt:
            await update.message.reply_text("Я сказал <b>ТЕКСТ</b>! Давай нормальное описание.", parse_mode=ParseMode.HTML)
            return AWAITING_PROMPT
    elif update.callback_query:
        user_prompt = context.user_data.get('current_pig_prompt')
        if not user_prompt:
            await update.callback_query.answer("Промпт потерялся. Начни заново: /generate_pig")
            return None
    else:
        return None

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    
    if update.message:
        await update.message.reply_text("Хммм... Сейчас посмотрим, что можно выжать из твоей ерунды.")

    # Генерация уникального ключа для кнопки
    prompt_key = f"{REGEN_PREFIX}{uuid.uuid4().hex[:8]}"
    context.user_data[prompt_key] = user_prompt 
    context.user_data['current_pig_prompt'] = user_prompt 
    
    try:
        image_url = await generate_dalle_image(user_prompt)
        
        if image_url:
            keyboard = [[InlineKeyboardButton("🔄 Переделать", callback_data=prompt_key)]]
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption="На, подавись. Не вздумай мне жаловаться, если оно кривое.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Что-то у тебя там криво пошло. Скорее всего, ты ерунду написал.",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error in generate_pig_image: {e}", exc_info=True)
        await context.bot.send_message(chat_id, "❌ Ошибка генерации. Попробуй позже.")

    return ConversationHandler.END if update.message else None

async def regenerate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 
    
    user_prompt = context.user_data.get(query.data)
    
    if user_prompt:
        await query.edit_message_caption(
            caption=f"Понял, переделываю: <i>{user_prompt[:40]}...</i>\n<b>🔄 Генерирую...</b>",
            parse_mode=ParseMode.HTML
        )
        await generate_pig_image(update, context)
        # Очистка старого ключа для экономии памяти
        context.user_data.pop(query.data, None)
    else:
        await query.edit_message_caption(caption="Я забыл, что ты просил. Начни заново: /generate_pig")

async def cancel_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Что, слился? Я так и думал.", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def get_generate_pig_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("generate_pig", start_generate_pig)],
        states={
            AWAITING_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pig_image),
                MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT, start_generate_pig),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_generate)],
        block=False
    )

def get_regenerate_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(regenerate_callback, pattern=f"^{REGEN_PREFIX}")