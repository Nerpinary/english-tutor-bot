import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler as TGMessageHandler, filters
from src.config import TELEGRAM_BOT_TOKEN
from src.database.database import engine
from src.handlers.message_handlers import MessageHandler
from src.handlers.ai_handler import AIHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Создаем экземпляр AIHandler
    ai_handler = AIHandler()
    
    # Создаем экземпляр нашего обработчика сообщений
    message_handler = MessageHandler(engine, ai_handler)
    
    # Создаем приложение
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", message_handler.start_command))
    application.add_handler(TGMessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 