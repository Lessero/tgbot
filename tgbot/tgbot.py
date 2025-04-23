import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Вызвана команда /start")
    keyboard = [[InlineKeyboardButton("Скинь кота", callback_data="get_cat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет! Нажми кнопку ниже, чтобы получить изображение кота.',
        reply_markup=reply_markup
    )

# Обработка кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info("Нажата кнопка: %s", query.data)

    if query.data == "get_cat":
        cat_url = await fetch_cat_url()
        if cat_url:
            keyboard = [[InlineKeyboardButton("Скинь кота", callback_data="get_cat")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            caption = f"Вот твой котик 😺\nСсылка: {cat_url}"
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=cat_url,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не удалось получить кота. Попробуй позже."
            )

# Получение URL картинки
async def fetch_cat_url():
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and isinstance(data, list) and "url" in data[0]:
                        return data[0]["url"]
    except Exception as e:
        logger.error(f"Ошибка загрузки кота: {e}")
    return None

# Основной запуск
def main():
    app = ApplicationBuilder().token("7524337590:AAFGIHlEr5EUWZXQEpfYMVVV3pEpuwzwgAc").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^get_cat$"))

    print("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()