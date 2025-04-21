# Импорт необходимых классов и функций из библиотеки
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Асинхронная функция, обрабатывающая команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отправка приветственного сообщения пользователю
    await update.message.reply_text('Привет! Я эхо-бот. Отправь мне сообщение, и я повторю его.')

# Асинхронная функция, обрабатывающая все текстовые сообщения
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Повторение полученного сообщения
    await update.message.reply_text(update.message.text)

# Основная функция для запуска бота
def main():
    # Создание приложения бота с использованием токена
    app = ApplicationBuilder().token('7524337590:AAFGIHlEr5EUWZXQEpfYMVVV3pEpuwzwgAc').build()

    # Добавление обработчика команды /start
    app.add_handler(CommandHandler('start', start))

    # Добавление обработчика всех текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запуск бота
    app.run_polling()

# Проверка, что скрипт запускается напрямую
if __name__ == '__main__':
    main()
