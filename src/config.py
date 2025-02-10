import os
from dotenv import load_dotenv

load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Настройки бота
BOT_NAME = "English Tutor Bot"
WELCOME_MESSAGE = """
Привет! Я твой персональный репетитор английского языка. 
Я помогу тебе улучшить твой английский через общение.

Команды:
/start - Начать общение
/help - Показать помощь
"""

SYSTEM_PROMPT = """You are an English language tutor. Your tasks:
1. Maintain natural conversation in English
2. Correct student's mistakes politely
3. Provide explanations in Russian when needed
4. Adapt to student's level
5. Keep conversations engaging and motivating"""

# Добавим новые константы
LEARNING_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

ACHIEVEMENTS = {
    'first_message': 'Первое сообщение! 🎉',
    'daily_streak_7': 'Неделя практики! 🔥',
    'grammar_master': 'Грамматический мастер 📚',
    'vocabulary_hero': 'Словарный герой 📖'
}

EXERCISE_TYPES = {
    'grammar': 'Грамматика 📝',
    'vocabulary': 'Словарный запас 📚',
    'listening': 'Аудирование 🎧',
    'speaking': 'Разговорная практика 🗣',
    'writing': 'Письмо ✍️'
}

REMINDER_INTERVALS = {
    'daily': 24 * 60 * 60,  # 24 часа
    'weekly': 7 * 24 * 60 * 60,
    'inactive': 3 * 24 * 60 * 60  # Если пользователь неактивен 3 дня
}

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./english_bot.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Web app settings
WEBAPP_URL = 'https://english-tutor-bot.onrender.com'  # Добавили конкретный URL
