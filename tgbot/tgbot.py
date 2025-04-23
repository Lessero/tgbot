import logging
import random
import aiohttp
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 🔹 Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Основная клавиатура
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Скинь кота", callback_data="get_cat"),
            InlineKeyboardButton("Скинь цитату", callback_data="get_quote")
        ]
    ])

# 🔹 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажми одну из кнопок ниже:",
        reply_markup=main_keyboard()
    )

# 🔹 Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Нажата кнопка: {query.data}")

    if query.data == "get_cat":
        cat_url = await fetch_cat_url()
        if cat_url:
            caption = f"Вот твой котик 😺\n[Ссылка на изображение]({cat_url})"
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=cat_url,
                caption=caption,
                reply_markup=main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не удалось получить кота. Попробуй позже."
            )

    elif query.data == "get_quote":
        quote_text, quote_author = await fetch_russian_quote()
        if quote_text:
            text = f"_{quote_text}_\n\n— *{quote_author if quote_author else 'Неизвестный автор'}*"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не удалось получить цитату. Попробуй позже."
            )

# 🔹 Реакция на ручной ввод пользователя
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_path, "warn_replies.txt")
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        reply = random.choice(lines)
    except Exception as e:
        reply = "Кнопки тыкай, сюда не пиши! (ошибка загрузки фраз)"
        print(f"Ошибка при загрузке фраз: {e}")

    await update.message.reply_text(reply, reply_markup=main_keyboard())

# 🔹 Получение URL кота
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

# 🔹 Получение русской цитаты
async def fetch_russian_quote():
    url = "https://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",
        "format": "json",
        "lang": "ru"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        # Чистим кавычки (форизматик бывает кривой)
                        data = eval(text.replace('\r', '').replace('\n', ''))
                        return data.get("quoteText", "").strip(), data.get("quoteAuthor", "").strip()
                    except Exception as inner:
                        logger.warning(f"Ошибка обработки JSON цитаты: {inner}")
    except Exception as e:
        logger.error(f"Ошибка при получении цитаты: {e}")
    return None, None

# 🔹 Запуск бота
def main():
    app = ApplicationBuilder().token("7524337590:AAFGIHlEr5EUWZXQEpfYMVVV3pEpuwzwgAc").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern=".*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, warn_user))

    print("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
