from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler as TelegramMessageHandler,
    filters
)
from src.database.database import engine, Base
from src.handlers.message_handlers import MessageHandler
from src.handlers.stats_handler import StatsHandler
from src.exercises.exercise_handler import ExerciseHandler
from src.utils.reminder import ReminderManager
from src.handlers.ai_handler import AIHandler
from src.config import TELEGRAM_BOT_TOKEN

def setup_bot():
    # Инициализация базы данных
    Base.metadata.create_all(bind=engine)
    
    # Создание экземпляра приложения
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Создаем AI handler
    ai_handler = AIHandler()
    
    # Инициализация обработчиков
    message_handler = MessageHandler(engine, ai_handler)
    exercise_handler = ExerciseHandler(engine)
    stats_handler = StatsHandler(engine)
    reminder_manager = ReminderManager(application)
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", message_handler.start_command))
    application.add_handler(CommandHandler("help", message_handler.help_command))
    application.add_handler(CommandHandler("stats", stats_handler.show_stats))
    application.add_handler(CommandHandler("exercise", exercise_handler.handle_exercise_request))
    
    # Регистрация обработчика текстовых сообщений
    application.add_handler(TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_message))
    
    # Регистрация обработчика callback-кнопок
    application.add_handler(CallbackQueryHandler(exercise_handler.handle_callback))
    
    return application 