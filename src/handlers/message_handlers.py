from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.database.models import User, Statistics, Achievement
from ..utils.progress_tracker import ProgressTracker
from ..exercises.generator import ExerciseGenerator
from src.handlers.ai_handler import AIHandler
from src.config import WEBAPP_URL
from src.handlers.level_test_handler import LevelTestHandler

class MessageHandler:
    def __init__(self, engine, ai_handler: AIHandler):
        self.engine = engine
        self.ai = ai_handler
        self.progress_tracker = ProgressTracker()
        self.exercise_generator = ExerciseGenerator()
        self.level_test = LevelTestHandler(engine, ai_handler)
        # Создаем основную клавиатуру
        self.main_keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("📝 Упражнения"), KeyboardButton("📊 Статистика")],
                [KeyboardButton("📚 Уроки"), KeyboardButton("🎯 Цели")],
                [KeyboardButton("❓ Помощь")]
            ],
            resize_keyboard=True
        )
        # Создаем клавиатуру с кнопкой веб-приложения
        self.webapp_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("🌐 Открыть Web App", web_app=WebAppInfo(url=WEBAPP_URL))]
        ], resize_keyboard=True)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if not user:
                # Новый пользователь - начинаем тест
                user = User(telegram_id=user_id, level='Unknown')
                session.add(user)
                stats = Statistics(user=user)
                session.add(stats)
                session.commit()
                
                await update.message.reply_text(
                    "👋 Привет! Я твой персональный помощник в изучении английского языка.\n"
                    "Давайте для начала определим ваш уровень английского!"
                )
                await self.level_test.start_test(update, context)
                return
                
        # Существующий пользователь - показываем обычное приветствие
        await update.message.reply_text(
            "👋 С возвращением!\n"
            "Нажми на кнопку ниже, чтобы открыть интерактивное приложение:",
            reply_markup=self.webapp_keyboard
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "🤖 Вот что я умею:\n\n"
            "/start - Начать обучение\n"
            "/stats - Посмотреть статистику\n"
            "/exercise - Начать упражнение\n"
            "/help - Показать это сообщение\n\n"
            "Просто пиши мне на английском, и я помогу тебе улучшить язык!"
        )
        await update.message.reply_text(help_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        message = update.message.text

        # Обработка нажатий на кнопки меню
        if message == "📝 Упражнения":
            return await self.show_exercises_menu(update, context)
        elif message == "📊 Статистика":
            return await self.show_statistics(update, context)
        elif message == "📚 Уроки":
            return await self.show_lessons_menu(update, context)
        elif message == "🎯 Цели":
            return await self.show_goals(update, context)
        elif message == "❓ Помощь":
            return await self.help_command(update, context)
        
        # Обычная обработка сообщения через AI
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if not user:
                user = User(telegram_id=user_id, level='A1')
                session.add(user)
                stats = Statistics(user=user)
                session.add(stats)
            else:
                stats = user.statistics[0]
                stats.messages_count += 1
            
            ai_response = await self.ai.get_response(message, user.level)
            session.commit()
            
            await update.message.reply_text(ai_response, reply_markup=self.main_keyboard)

    async def show_exercises_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню упражнений"""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Грамматика 📝", callback_data='exercise_grammar'),
                InlineKeyboardButton("Лексика 📚", callback_data='exercise_vocabulary')
            ],
            [
                InlineKeyboardButton("Аудирование 🎧", callback_data='exercise_listening'),
                InlineKeyboardButton("Письмо ✍️", callback_data='exercise_writing')
            ]
        ])
        await update.message.reply_text("Выберите тип упражнения:", reply_markup=keyboard)

    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает подробную статистику"""
        user_id = update.effective_user.id
        
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if not user or not user.statistics:
                await update.message.reply_text(
                    "Статистика пока недоступна. Начните обучение!",
                    reply_markup=self.main_keyboard
                )
                return

            stats = user.statistics[0]
            stats_message = (
                "📊 *Ваша статистика:*\n\n"
                f"📝 Сообщений отправлено: {stats.messages_count}\n"
                f"✍️ Исправлено ошибок: {stats.corrections_count}\n"
                f"📚 Выполнено упражнений: {stats.exercises_completed}\n"
                f"🔥 Дней подряд: {user.streak_days}\n"
                f"📈 Текущий уровень: {user.level}\n\n"
                "Продолжайте в том же духе! 💪"
            )
            
            await update.message.reply_text(
                stats_message,
                parse_mode='Markdown',
                reply_markup=self.main_keyboard
            )

    async def show_lessons_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню уроков"""
        await update.message.reply_text(
            "🔜 Уроки скоро будут доступны!",
            reply_markup=self.main_keyboard
        )

    async def show_goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает цели обучения"""
        await update.message.reply_text(
            "🔜 Система целей скоро будет доступна!",
            reply_markup=self.main_keyboard
        )

    async def check_achievements(self, user):
        stats = user.statistics[0]
        if stats.messages_count == 1:
            self.award_achievement(user, 'first_message')
        if user.streak_days == 7:
            self.award_achievement(user, 'daily_streak_7')
        # Добавьте другие проверки достижений

    def award_achievement(self, user, achievement_name):
        if not any(a.name == achievement_name for a in user.achievements):
            achievement = Achievement(user_id=user.id, name=achievement_name)
            session.add(achievement)
            # Отправить уведомление о получении достижения
