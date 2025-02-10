from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from src.config import TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY, WELCOME_MESSAGE
from .handlers.ai_handler import get_ai_response

class EnglishTutorBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        # Настраиваем Gemini вместо OpenAI
        genai.configure(api_key=GOOGLE_API_KEY)
        
    async def start_command(self, update, context):
        """Обработчик команды /start"""
        await update.message.reply_text(WELCOME_MESSAGE)
    
    async def help_command(self, update, context):
        """Обработчик команды /help"""
        await update.message.reply_text(WELCOME_MESSAGE)
    
    async def handle_message(self, update, context):
        """Обработчик текстовых сообщений"""
        message = update.message.text
        response = await get_ai_response(message)
        await update.message.reply_text(response)
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def run(self):
        """Запуск бота"""
        self.setup_handlers()
        print("Бот запущен...")
        self.application.run_polling()