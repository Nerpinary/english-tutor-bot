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
        self.questions = [
            "What's your name and where are you from?",
            "Tell me about your family.",
            "What do you like to do in your free time?",
            "What did you do yesterday?",
            "What are your plans for the future?",
            "If you could change one thing about your city, what would it be and why?",
            "What's the most interesting book you've read or movie you've seen recently?",
            "Do you think technology makes our lives easier or more complicated? Why?",
            "What would you do if you won a million dollars?",
            "What are the most important challenges facing our world today?"
        ]
        
    async def should_take_test(self, user: User) -> bool:
        """Проверяет, нужно ли пользователю пройти тест"""
        return not user.level or user.level in ['Unknown', 'undefined', 'A0']
        
    async def start_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начинает тест на определение уровня"""
        user_id = update.effective_user.id
        
        # Инициализируем состояние теста
        self.test_states[user_id] = {
            'current_question': 0,
            'responses': [],
            'scores': [],
            'consecutive_low_scores': 0
        }
        
        await update.message.reply_text(
            "📝 Давайте определим ваш уровень английского языка!\n\n"
            "Я задам вам несколько вопросов на английском. "
            "Отвечайте на них как можно более полно и естественно.\n\n"
            "Тест состоит из 10 вопросов, но может закончиться раньше, "
            "если ваш уровень будет определен точно.\n\n"
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
            await query.message.delete()
            await self._ask_next_question(query.message)
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
        analysis = await self._analyze_response(response)
        state['scores'].append(analysis)
        
        # Проверяем на последовательные низкие оценки
        if analysis['level'] in ['A1', 'A2']:
            state['consecutive_low_scores'] += 1
        else:
            state['consecutive_low_scores'] = 0
            
        # Заканчиваем тест если:
        # 1. Получили 5 последовательных низких оценок
        # 2. Ответили на все 10 вопросов
        # 3. Получили 3 последовательных одинаковых уровня после 5 вопросов
        if (state['consecutive_low_scores'] >= 5 or 
            state['current_question'] >= 9 or 
            (state['current_question'] >= 4 and self._check_consistent_level(state['scores'][-3:]))):
            
            await self._finish_test(update, state)
            return
            
        state['current_question'] += 1
        await self._ask_next_question(update.message)
            
    async def _ask_next_question(self, message):
        """Задает следующий вопрос"""
        user_id = message.chat.id
        question_num = self.test_states[user_id]['current_question']
        
        await message.reply_text(
            f"Question {question_num + 1}:\n\n"
            f"{self.questions[question_num]}\n\n"
            "Please answer in English 🇬🇧"
        )
        
    async def _analyze_response(self, response: str) -> dict:
        """Анализирует ответ пользователя с помощью AI"""
        prompt = f"""As an English language expert, analyze this response:
        "{response}"
        
        Consider:
        1. Grammar accuracy
        2. Vocabulary range
        3. Sentence complexity
        4. Appropriateness of response
        
        Determine the CEFR level (A1-C2) and provide scores.
        
        Return only JSON:
        {{
            "level": "B1",
            "grammar_score": 4,
            "vocabulary_score": 3,
            "complexity_score": 4,
            "overall_score": 3.7
        }}"""
        
        try:
            result = await self.ai.get_response(prompt)
            return eval(result)  # В реальном коде используйте json.loads()
        except:
            return {
                "level": "A1",
                "grammar_score": 1,
                "vocabulary_score": 1,
                "complexity_score": 1,
                "overall_score": 1
            }
        
    def _check_consistent_level(self, recent_scores: list) -> bool:
        """Проверяет, получены ли последовательные одинаковые уровни"""
        if len(recent_scores) < 3:
            return False
        return all(score['level'] == recent_scores[0]['level'] for score in recent_scores)
        
    async def _finish_test(self, update: Update, state: dict):
        """Завершает тест и определяет итоговый уровень"""
        scores = state['scores']
        
        # Определяем итоговый уровень
        if state['consecutive_low_scores'] >= 5:
            final_level = 'A1'
        else:
            # Берем преобладающий уровень из последних ответов
            recent_levels = [score['level'] for score in scores[-3:]]
            final_level = max(set(recent_levels), key=recent_levels.count)
        
        # Вычисляем средние показатели
        avg_grammar = sum(s['grammar_score'] for s in scores) / len(scores)
        avg_vocab = sum(s['vocabulary_score'] for s in scores) / len(scores)
        avg_complex = sum(s['complexity_score'] for s in scores) / len(scores)
        
        # Сохраняем результат в базе данных
        with Session(self.engine) as session:
            user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
            user.level = final_level
            session.commit()
        
        await update.message.reply_text(
            f"🎉 Тест завершен!\n\n"
            f"Ваш уровень: {final_level}\n\n"
            f"📊 Детальные результаты:\n"
            f"Грамматика: {'⭐' * round(avg_grammar)}\n"
            f"Словарный запас: {'⭐' * round(avg_vocab)}\n"
            f"Сложность речи: {'⭐' * round(avg_complex)}\n\n"
            f"💡 Что означает уровень {final_level}:\n"
            f"{self._get_level_description(final_level)}\n\n"
            "Теперь я буду подстраивать общение и упражнения под ваш уровень! 🎯"
        )
        
        # Очищаем состояние теста
        del self.test_states[update.effective_user.id]
        
    def _get_level_description(self, level: str) -> str:
        """Возвращает описание уровня"""
        descriptions = {
            'A1': 'Начальный уровень. Вы можете общаться на простые темы и понимать базовые фразы.',
            'A2': 'Элементарный уровень. Вы можете общаться в простых ситуациях и описывать основные аспекты жизни.',
            'B1': 'Средний уровень. Вы можете общаться на большинство повседневных тем и выражать свое мнение.',
            'B2': 'Выше среднего. Вы можете свободно общаться с носителями языка и понимать сложные тексты.',
            'C1': 'Продвинутый уровень. Вы можете использовать язык гибко и эффективно для социальных и профессиональных целей.',
            'C2': 'Свободное владение. Вы понимаете практически все и можете выражать свои мысли спонтанно и точно.'
        }
        return descriptions.get(level, 'Уровень определен') 