from telegram.ext import ContextTypes
from datetime import datetime, timedelta

class ReminderManager:
    def __init__(self, application):
        self.application = application

    async def schedule_reminder(self, chat_id: int, interval: int):
        """
        Планирует напоминание
        :param chat_id: ID чата пользователя
        :param interval: Интервал в секундах
        """
        await self.application.job_queue.run_once(
            self._send_reminder,
            interval,
            chat_id=chat_id,
            name=f'reminder_{chat_id}'
        )

    async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Отправляет напоминание"""
        job = context.job
        await context.bot.send_message(
            job.chat_id,
            "👋 Привет! Давно не виделись! Готовы продолжить изучение английского?"
        )

    def cancel_reminder(self, chat_id: int):
        """Отменяет напоминание"""
        self.application.job_queue.get_jobs_by_name(f'reminder_{chat_id}') 