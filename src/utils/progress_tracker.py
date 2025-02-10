from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.db = {}  # Можно заменить на реальную БД

    async def log_interaction(self, user_id: int, message: str, corrections: list):
        if user_id not in self.db:
            self.db[user_id] = []
        
        self.db[user_id].append({
            'timestamp': datetime.now(),
            'message': message,
            'corrections': corrections
        }) 