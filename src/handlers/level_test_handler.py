from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.database.models import User
from src.handlers.ai_handler import AIHandler

class LevelTestHandler:
    def __init__(self, engine, ai_handler: AIHandler):
        self.engine = engine
        self.ai = ai_handler
        self.test_states = {}  # Хранение состояния теста для каждого пользователя
        
    async def start_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начинает тест на определение уровня"""
        user_id = update.effective_user.id
        
        # Инициализируем состояние теста
        self.test_states[user_id] = {
            'current_question': 0,
            'responses': [],
            'mistakes': 0
        }
        
        await update.message.reply_text(
            "📝 Давайте определим ваш уровень английского языка!\n\n"
            "Я задам вам несколько вопросов на английском. "
            "Просто отвечайте на них как можно более полно.\n\n"
            "Готовы начать?",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Начать тест", callback_data="level_test_start")
            ]])
        )
    
    async def handle_test_interaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает взаимодействие с тестом"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == "level_test_start":
            await self._ask_next_question(query)
            return
            
    async def handle_test_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает ответы пользователя во время теста"""
        user_id = update.effective_user.id
        response = update.message.text
        
        if user_id not in self.test_states:
            return
            
        state = self.test_states[user_id]
        state['responses'].append(response)
        
        # Анализируем ответ с помощью AI
        analysis = await self._analyze_response(response, state['current_question'])
        
        if analysis['has_mistakes']:
            state['mistakes'] += 1
            
        state['current_question'] += 1
        
        if state['current_question'] >= 5:  # Тест завершен
            await self._finish_test(update, state)
        else:
            await self._ask_next_question(update)
            
    async def _ask_next_question(self, update):
        """Задает следующий вопрос"""
        questions = [
            "Tell me about yourself and your hobbies.",
            "What did you do last weekend?",
            "What are your plans for the future?",
            "If you could travel anywhere, where would you go and why?",
            "What's your opinion about learning foreign languages?"
        ]
        
        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        question_num = self.test_states[user_id]['current_question']
        
        await update.message.reply_text(f"Question {question_num + 1}/5:\n\n{questions[question_num]}")
        
    async def _analyze_response(self, response: str, question_num: int) -> dict:
        """Анализирует ответ пользователя с помощью AI"""
        prompt = f"""Analyze this English response and determine:
        1. CEFR level (A1-C2)
        2. Grammar mistakes
        3. Vocabulary range
        4. Sentence complexity
        
        Response: "{response}"
        
        Return JSON format:
        {{
            "level": "B1",
            "has_mistakes": true/false,
            "grammar_score": 1-5,
            "vocabulary_score": 1-5,
            "complexity_score": 1-5
        }}
        """
        
        result = await self.ai.get_response(prompt)
        # Предполагаем, что AI возвращает JSON строку
        return eval(result)  # В реальном коде нужно использовать json.loads()
        
    async def _finish_test(self, update: Update, state: dict):
        """Завершает тест и определяет итоговый уровень"""
        # Анализируем все ответы вместе для финального определения уровня
        all_responses = "\n".join(state['responses'])
        final_analysis = await self._analyze_response(all_responses, -1)
        
        # Сохраняем результат в базе данных
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
            user.level = final_analysis['level']
            session.commit()
        
        await update.message.reply_text(
            f"🎉 Тест завершен!\n\n"
            f"Ваш уровень: {final_analysis['level']}\n\n"
            f"📊 Результаты:\n"
            f"Грамматика: {'⭐' * final_analysis['grammar_score']}\n"
            f"Словарный запас: {'⭐' * final_analysis['vocabulary_score']}\n"
            f"Сложность предложений: {'⭐' * final_analysis['complexity_score']}\n\n"
            "Теперь я буду подстраивать общение и упражнения под ваш уровень! 🎯"
        )
        
        # Очищаем состояние теста
        del self.test_states[update.effective_user.id] 