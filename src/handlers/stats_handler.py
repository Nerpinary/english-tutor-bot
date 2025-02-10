from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.database.models import User, Statistics

class StatsHandler:
    def __init__(self, engine):
        self.engine = engine

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Создаем сессию базы данных
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                await update.message.reply_text("Статистика пока недоступна. Начните общение с ботом!")
                return
            
            stats = user.statistics[0] if user.statistics else None
            
            if not stats:
                await update.message.reply_text("Статистика пока недоступна. Продолжайте общение с ботом!")
                return
            
            # Формируем сообщение со статистикой
            stats_message = (
                "📊 Ваша статистика:\n\n"
                f"Сообщений отправлено: {stats.messages_count}\n"
                f"Исправлено ошибок: {stats.corrections_count}\n"
                f"Выполнено упражнений: {stats.exercises_completed}\n"
                f"Дней подряд: {user.streak_days}\n"
            )
            
            await update.message.reply_text(stats_message) 