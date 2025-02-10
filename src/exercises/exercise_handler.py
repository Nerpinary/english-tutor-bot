from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.database.models import User, Statistics
from .exercise_generator import ExerciseGenerator

class ExerciseHandler:
    def __init__(self, engine):
        self.engine = engine
        self.generator = ExerciseGenerator()

    async def handle_exercise_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик запроса на упражнение"""
        keyboard = [
            [
                InlineKeyboardButton("Грамматика 📝", callback_data='exercise_grammar'),
                InlineKeyboardButton("Лексика 📚", callback_data='exercise_vocabulary')
            ],
            [
                InlineKeyboardButton("Аудирование 🎧", callback_data='exercise_listening'),
                InlineKeyboardButton("Письмо ✍️", callback_data='exercise_writing')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Выберите тип упражнения:",
            reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        exercise_type = query.data.split('_')[1]
        
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
            exercise = self.generator.get_exercise(exercise_type, user.level)
            
            await query.message.reply_text(
                f"📝 Упражнение:\n\n{exercise['question']}\n\n"
                "Напишите ваш ответ в чат."
            ) 