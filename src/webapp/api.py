from flask import Blueprint, jsonify, request
from src.database.database import get_db
from src.database.models import User, Statistics

api = Blueprint('api', __name__)

@api.route('/api/user-data')
def get_user_data():
    telegram_id = request.args.get('user_id')
    if not telegram_id:
        return jsonify({'error': 'No user ID provided'}), 400
    
    db = next(get_db())
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    stats = user.statistics[0] if user.statistics else None
    
    # Получаем данные пользователя из Telegram через context.bot.get_chat
    try:
        from telegram import Bot
        from src.config import TELEGRAM_BOT_TOKEN
        
        bot = Bot(TELEGRAM_BOT_TOKEN)
        chat = bot.get_chat(telegram_id)
        
        user_data = {
            'name': chat.first_name,
            'username': chat.username,
            'photo_url': chat.photo.big_file_id if chat.photo else None,
            'level': user.level,
            'messages': stats.messages_count if stats else 0,
            'exercises': stats.exercises_completed if stats else 0,
            'streak': user.streak_days,
        }
        
        # Если есть фото профиля, получаем URL
        if user_data['photo_url']:
            file = bot.get_file(user_data['photo_url'])
            user_data['photo_url'] = file.file_path
            
        return jsonify(user_data)
        
    except Exception as e:
        # Если не удалось получить данные из Telegram, возвращаем базовые данные
        return jsonify({
            'name': f"User {telegram_id}",
            'username': None,
            'photo_url': None,
            'level': user.level,
            'messages': stats.messages_count if stats else 0,
            'exercises': stats.exercises_completed if stats else 0,
            'streak': user.streak_days
        }) 