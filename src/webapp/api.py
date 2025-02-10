from flask import Blueprint, jsonify, request
from src.database.database import get_db
from src.database.models import User, Statistics
import logging
import hashlib
import hmac
import json
from urllib.parse import parse_qs
from src.config import TELEGRAM_BOT_TOKEN
from sqlalchemy.orm import Session
from src.database.database import engine
from src.config import ai_handler, bot

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

def validate_telegram_data(init_data: str) -> bool:
    """Проверяет подлинность данных от Telegram"""
    try:
        logger.debug(f"Validating init_data: {init_data}")
        
        # Разбираем строку init_data
        data_dict = dict(parse_qs(init_data))
        
        # Получаем и удаляем hash из данных
        received_hash = data_dict.pop('hash')[0]
        
        # Сортируем оставшиеся поля
        data_check_string = '\n'.join(f"{k}={v[0]}" for k, v in sorted(data_dict.items()))
        
        # Создаем secret key из токена бота
        secret_key = hmac.new(b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        logger.error(f"Error validating Telegram data: {e}")
        return False

@api.route('/api/user-data')
def get_user_data():
    try:
        # Получаем и логируем все параметры запроса
        logger.debug(f"Request args: {request.args}")
        
        # Получаем init_data из параметров
        init_data = request.args.get('init_data')
        if not init_data:
            logger.error("No init_data provided")
            return jsonify({'error': 'No init_data provided'}), 400

        # Проверяем подлинность данных
        if not validate_telegram_data(init_data):
            logger.error("Invalid Telegram data")
            return jsonify({'error': 'Invalid Telegram data'}), 403

        # Получаем ID пользователя
        user_id = request.args.get('user_id')
        if not user_id:
            logger.error("No user_id provided")
            return jsonify({'error': 'No user_id provided'}), 400

        logger.debug(f"Processing request for user_id: {user_id}")

        # Получаем данные пользователя из базы
        db = next(get_db())
        user = db.query(User).filter_by(telegram_id=user_id).first()

        if not user:
            logger.error(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        stats = user.statistics[0] if user.statistics else None

        # Формируем ответ
        user_data = {
            'name': f"User {user_id}",
            'level': user.level,
            'messages': stats.messages_count if stats else 0,
            'exercises': stats.exercises_completed if stats else 0,
            'streak': user.streak_days
        }

        logger.debug(f"Returning user data: {user_data}")
        return jsonify(user_data)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500 

@api.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message')
        level = data.get('level')

        if not all([user_id, message, level]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Формируем промпт для AI с учетом уровня пользователя
        prompt = f"""You are an English teacher. The student's level is {level}.
        Respond to their message in a way that:
        1. Uses vocabulary appropriate for their level
        2. Gently corrects any mistakes
        3. Encourages further conversation
        4. Keeps responses concise and clear

        Student's message: {message}"""

        # Получаем ответ от AI
        response = ai_handler.get_response(prompt)

        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/api/correct', methods=['POST'])
def correct():
    data = request.json
    message = data.get('message')
    level = data.get('level')

    prompt = f"""As an English teacher, correct any mistakes in this message.
    Format the response with:
    - Original: [original text]
    - Corrected: [corrected text]
    - Explanation: [brief explanation]

    Message: {message}"""

    correction = ai_handler.get_response(prompt)
    return jsonify({'correction': correction})

@api.route('/api/explain-grammar', methods=['POST'])
def explain_grammar():
    data = request.json
    message = data.get('message')
    level = data.get('level')

    prompt = f"""Explain the grammar used in this message in a way that's appropriate 
    for a {level} level English learner. Focus on the main grammatical structures.

    Message: {message}"""

    explanation = ai_handler.get_response(prompt)
    return jsonify({'explanation': explanation})

@api.route('/api/end-session', methods=['POST'])
def end_session():
    try:
        data = request.json
        user_id = data.get('user_id')
        duration = data.get('duration')
        messages_count = data.get('messages_count')

        # Сохраняем статистику в базе данных
        with Session(engine) as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if user:
                stats = user.statistics[0]
                stats.total_time += duration
                stats.messages_count += messages_count
                session.commit()

        # Отправляем сообщение в Telegram
        bot.send_message(
            user_id,
            f"🎉 Great job! Today's practice:\n"
            f"⏱ Time: {duration//60} minutes\n"
            f"💬 Messages: {messages_count}\n"
            f"Keep up the good work!"
        )

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return jsonify({'error': str(e)}), 500 