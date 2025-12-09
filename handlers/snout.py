from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.snout_processing import add_snouts_to_faces

WAITING_PHOTO = 1

async def snout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога: просим фото."""
    await update.message.reply_text(
        "Хрю! 🐷 Пришли мне фотографию, где видно лицо, и я добавлю на него пятачок!\n\n"
        "Напиши /cancel, если передумал."
    )
    return WAITING_PHOTO

async def snout_process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получаем фото, обрабатываем и отправляем обратно."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    
    await update.message.reply_text("Ловлю фото... Обрабатываю... 🐽")

    image_bytes = await photo_file.download_as_bytearray()

    snouts_dir = "snouts" 

    try:
        processed_image = add_snouts_to_faces(image_bytes, snouts_dir)

        if processed_image:
            await update.message.reply_photo(photo=processed_image, caption="С-с-свежий кабанчик! 🐷")
        else:
            await update.message.reply_text("Хм... Я не нашел лиц на этом фото. Попробуй другое! 🐽")
            return WAITING_PHOTO 

    except Exception as e:
        print(f"Ошибка при обработке фото: {e}")
        await update.message.reply_text("Ой, что-то пошло не так при обработке. Попробуй еще раз.")
        return ConversationHandler.END

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога."""
    await update.message.reply_text("Хорошо, отбой! Хрю.")
    return ConversationHandler.END

snout_handler = ConversationHandler(
    entry_points=[CommandHandler("snout", snout_start)],
    states={
        WAITING_PHOTO: [MessageHandler(filters.PHOTO, snout_process_photo)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)