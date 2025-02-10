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
    
    return jsonify({
        'name': f"User {telegram_id}",
        'level': user.level,
        'messages': stats.messages_count if stats else 0,
        'exercises': stats.exercises_completed if stats else 0,
        'streak': user.streak_days
    }) 