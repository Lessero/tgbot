import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токенов из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Главная клавиатура с кнопками
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Скинь кота", callback_data="get_cat"),
            InlineKeyboardButton("Скинь цитату", callback_data="get_quote")
        ],
        [
            InlineKeyboardButton("Ответь мне как...", callback_data="reply_as_character")
        ]
    ])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажми одну из кнопок ниже:",
        reply_markup=main_keyboard()
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я бот, который может:\n"
        "- Показать изображение кота\n"
        "- Отправить цитату\n"
        "- Ответить на вопрос в стиле выбранного персонажа\n\n"
        "Просто нажми соответствующую кнопку!"
    )

# Обработка нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Нажата кнопка: {query.data}")

    if query.data == "get_cat":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вот изображение кота: 🐱",
            reply_markup=main_keyboard()
        )
    elif query.data == "get_quote":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вот вдохновляющая цитата: \"Будь собой; все остальные роли уже заняты.\" — Оскар Уайльд",
            reply_markup=main_keyboard()
        )
    elif query.data == "reply_as_character":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите имя персонажа, в стиле которого вы хотите получить ответ:",
        )
        context.user_data['awaiting_character'] = True

# Обработка пользовательских сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_character'):
        # Сохраняем имя персонажа и запрашиваем вопрос
        context.user_data['character_name'] = update.message.text
        context.user_data['awaiting_character'] = False
        context.user_data['awaiting_question'] = True
        await update.message.reply_text(f"Отлично! Теперь введите ваш вопрос для {update.message.text}:")
    elif context.user_data.get('awaiting_question'):
        # Получаем вопрос и отправляем запрос к OpenAI
        character_name = context.user_data.get('character_name')
        question = update.message.text
        context.user_data['awaiting_question'] = False

        # Формируем prompt для OpenAI
        prompt = f"Представь, что ты {character_name}. Ответь на следующий вопрос в его стиле: {question}"

        # Отправляем запрос к OpenAI
        response = await get_openai_response(prompt)

        await update.message.reply_text(response, reply_markup=main_keyboard())
    else:
        # Обычная реакция на сообщение
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для взаимодействия со мной.",
            reply_markup=main_keyboard()
        )

# Функция для отправки запроса к OpenAI
async def get_openai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Вы — полезный помощник."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenAI: {e}")
        return "Произошла ошибка при получении ответа от AI."

# Запуск бота
def main():
    # Проверка наличия токенов
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        logger.error("Необходимо установить TELEGRAM_BOT_TOKEN и OPENAI_API_KEY в переменных окружения.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button, pattern=".*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()