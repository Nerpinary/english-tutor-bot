from flask import Blueprint, jsonify, request
from src.database.database import get_db
from src.database.models import User, Statistics
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/api/user-data')
def get_user_data():
    telegram_id = request.args.get('user_id')
    logger.debug(f'Received request for user_id: {telegram_id}')
    
    if not telegram_id:
        logger.error('No user ID provided')
        return jsonify({'error': 'No user ID provided'}), 400
    
    try:
        db = next(get_db())
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        
        if not user:
            logger.error(f'User not found: {telegram_id}')
            return jsonify({'error': 'User not found'}), 404
        
        stats = user.statistics[0] if user.statistics else None
        
        user_data = {
            'name': f"User {telegram_id}",
            'level': user.level,
            'messages': stats.messages_count if stats else 0,
            'exercises': stats.exercises_completed if stats else 0,
            'streak': user.streak_days
        }
        
        logger.debug(f'Returning user data: {user_data}')
        return jsonify(user_data)
        
    except Exception as e:
        logger.error(f'Error processing request: {str(e)}')
        return jsonify({'error': str(e)}), 500 